# type: ignore
import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel, Field, ValidationError

import src.config as config

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# Models
class ChatwootUserDetails(BaseModel):
    id: int
    uid: str
    name: str
    available_name: str
    display_name: Optional[str] = None
    email: str
    account_id: Optional[int] = None
    role: Optional[str] = None
    confirmed: bool
    custom_attributes: dict = Field(default_factory=dict)
    accounts: List[dict] = Field(default_factory=list)


class ChatwootUser(BaseModel):
    id: int
    account_id: int
    user_id: int
    role: str
    inviter_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    active_at: Optional[datetime] = None
    availability: str
    auto_offline: bool
    details: Optional[ChatwootUserDetails] = None

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class ChatwootUsersResponse(BaseModel):
    users: List[ChatwootUser]


class CloudflareUser(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime
    uid: str
    name: str
    email: str
    last_successful_login: Optional[datetime]
    access_seat: bool
    gateway_seat: bool
    seat_uid: str


class CloudflareUsersResponse(BaseModel):
    cloudflare_users: List[CloudflareUser]


# Cloudflare functions
async def fetch_cloudflare_access_users(client: httpx.AsyncClient) -> Dict[str, Any]:
    try:
        cloudflare_api_endpoint = f"https://api.cloudflare.com/client/v4/accounts/{config.CLOUDFLARE_ACCOUNT_ID}/access/users"
        cloudflare_headers = {
            "Authorization": f"Bearer {config.CLOUDFLARE_API_TOKEN}",
            "Content-Type": "application/json",
        }
        response = await client.get(cloudflare_api_endpoint, headers=cloudflare_headers)
        response.raise_for_status()
        users_data = response.json()
        users = CloudflareUsersResponse(cloudflare_users=users_data.get("result", []))
        return users.model_dump()["cloudflare_users"]
    except httpx.HTTPStatusError as e:
        logger.error(f"Failed to fetch Cloudflare Access users: {str(e)}")
        return {"message": "Failed to fetch Cloudflare Access users", "error_details": str(e)}
    except ValidationError as e:
        logger.error(f"Failed to validate Cloudflare Access users data: {str(e)}")
        return {
            "message": "Failed to validate Cloudflare Access users data",
            "error_details": str(e),
        }
    except Exception as e:
        logger.error(f"Unexpected error in fetch_cloudflare_access_users: {str(e)}")
        return {"message": "Unexpected error occurred", "error_details": str(e)}


async def update_cloudflare_access_group(
    client: httpx.AsyncClient, user_emails: List[str]
) -> Dict[str, Any]:
    try:
        cloudflare_api_endpoint = f"https://api.cloudflare.com/client/v4/accounts/{config.CLOUDFLARE_ACCOUNT_ID}/access/groups/{config.CLOUDFLARE_ACCESS_GROUP_ID}"
        cloudflare_headers = {
            "Authorization": f"Bearer {config.CLOUDFLARE_API_TOKEN}",
            "Content-Type": "application/json",
        }
        data = {
            "exclude": [],
            "include": [{"email": {"email": email}} for email in user_emails],
            "is_default": False,
            "name": config.CLOUDFLARE_ACCESS_GROUP_NAME,
            "require": [],
        }
        response = await client.put(cloudflare_api_endpoint, headers=cloudflare_headers, json=data)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"Failed to update Cloudflare Access group: {str(e)}")
        return {
            "status": "error",
            "message": "Failed to update Cloudflare Access group",
            "error_details": str(e),
        }
    except Exception as e:
        logger.error(f"Unexpected error in update_cloudflare_access_group: {str(e)}")
        return {"status": "error", "message": "Unexpected error occurred", "error_details": str(e)}


async def remove_cloudflare_user_seat(client: httpx.AsyncClient, seat_uid: str) -> Dict[str, Any]:
    try:
        cloudflare_api_endpoint = f"https://api.cloudflare.com/client/v4/accounts/{config.CLOUDFLARE_ACCOUNT_ID}/access/seats"
        cloudflare_headers = {
            "Authorization": f"Bearer {config.CLOUDFLARE_API_TOKEN}",
            "Content-Type": "application/json",
        }
        data = [{"access_seat": False, "gateway_seat": False, "seat_uid": seat_uid}]
        response = await client.patch(
            cloudflare_api_endpoint, headers=cloudflare_headers, json=data
        )
        response.raise_for_status()
        result = response.json()
        if result.get("success"):
            return {
                "status": "success",
                "message": f"Successfully removed seat for user with seat_uid: {seat_uid}",
                "result": result.get("result"),
            }
        else:
            return {
                "status": "error",
                "message": f"Failed to remove seat for user with seat_uid: {seat_uid}",
                "errors": result.get("errors"),
            }
    except httpx.HTTPStatusError as e:
        logger.error(f"Failed to remove Cloudflare user seat: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to remove seat for user with seat_uid: {seat_uid}",
            "error_details": str(e),
        }
    except Exception as e:
        logger.error(f"Unexpected error in remove_cloudflare_user_seat: {str(e)}")
        return {"status": "error", "message": "Unexpected error occurred", "error_details": str(e)}


# Chatwoot functions
async def fetch_chatwoot_users(
    client: httpx.AsyncClient,
    chatwoot_url: str,
    chatwoot_api_key: str,
    chatwoot_account_id: str,
):
    api_endpoint = f"{chatwoot_url}/platform/api/v1/accounts/{chatwoot_account_id}/account_users"
    headers = {"api_access_token": chatwoot_api_key, "Content-Type": "application/json"}
    response = await client.get(api_endpoint, headers=headers)
    if response.status_code == 200:
        users_data = response.json()
        users_list = users_data if isinstance(users_data, list) else users_data.get("users", [])
        return ChatwootUsersResponse(users=[ChatwootUser(**user) for user in users_list])
    else:
        raise Exception(
            f"Failed to fetch Chatwoot users. Status: {response.status_code}, Response: {response.text}"
        )


async def fetch_user_details(
    client: httpx.AsyncClient, chatwoot_url: str, headers: dict, user: ChatwootUser
):
    user_details_endpoint = f"{chatwoot_url}/platform/api/v1/users/{user.user_id}"
    response = await client.get(user_details_endpoint, headers=headers)
    if response.status_code == 200:
        user_details_data = response.json()
        user.details = ChatwootUserDetails(**user_details_data)
    elif response.status_code in [401, 404]:
        user.details = None
    else:
        raise Exception(
            f"Failed to fetch details for user {user.user_id}. Status: {response.status_code}, Response: {response.text}"
        )


async def fetch_all_user_details(
    client: httpx.AsyncClient,
    chatwoot_url: str,
    chatwoot_api_key: str,
    users: ChatwootUsersResponse,
):
    headers = {"api_access_token": chatwoot_api_key, "Content-Type": "application/json"}
    await asyncio.gather(*[
        fetch_user_details(client, chatwoot_url, headers, user) for user in users.users
    ])


async def remove_seat(client: httpx.AsyncClient, cf_user: dict, removal_reason: str):
    if cf_user["access_seat"] or cf_user["gateway_seat"]:
        result = await remove_cloudflare_user_seat(client, cf_user["seat_uid"])
        return {
            "user_id": cf_user["id"],
            "email": cf_user["email"],
            "seat_uid": cf_user["seat_uid"],
            "removal_reason": removal_reason,
            "result": result,
        }
    return None


# Main function
async def on_fetch(request):
    try:
        async with httpx.AsyncClient() as client:
            users = await fetch_chatwoot_users(
                client, config.CHATWOOT_URL, config.CHATWOOT_API_KEY, config.CHATWOOT_ACCOUNT_ID
            )
            await fetch_all_user_details(
                client, config.CHATWOOT_URL, config.CHATWOOT_API_KEY, users
            )
            chatwoot_users = [user for user in users.users if user.account_id == 1]
            chatwoot_user_emails = [user.details.email for user in chatwoot_users if user.details]

            cloudflare_group_update_result = await update_cloudflare_access_group(
                client, chatwoot_user_emails
            )

            cloudflare_users = await fetch_cloudflare_access_users(client)
            if isinstance(cloudflare_users, dict) and "message" in cloudflare_users:
                raise Exception(cloudflare_users["message"])

            current_time = datetime.now(timezone.utc)
            inactivity_threshold = current_time - timedelta(
                days=int(config.INACTIVITY_DAYS_THRESHOLD)
            )

            seat_removal_tasks = []
            for cf_user in cloudflare_users:
                should_remove_seat, removal_reason = should_remove_user_seat(
                    cf_user, chatwoot_user_emails, inactivity_threshold
                )
                if should_remove_seat and (cf_user["access_seat"] or cf_user["gateway_seat"]):
                    seat_removal_tasks.append(remove_seat(client, cf_user, removal_reason))

            seat_removal_results = await asyncio.gather(*seat_removal_tasks, return_exceptions=True)
            seat_removal_results = [
                result
                for result in seat_removal_results
                if result is not None and not isinstance(result, Exception)
            ]

            formatted_result = format_result(
                users, cloudflare_group_update_result, cloudflare_users, seat_removal_results
            )

            if config.DEBUG:
                return formatted_result
            else:
                return {"status": "success"}

    except Exception as e:
        logger.error(f"Error in on_fetch: {str(e)}")
        raise  # Let the API handler deal with the error


# Helper functions
def should_remove_user_seat(
    cf_user: dict, chatwoot_user_emails: List[str], inactivity_threshold: datetime
) -> tuple[bool, str]:
    if cf_user["email"] not in chatwoot_user_emails:
        return True, "Not in Chatwoot"
    elif cf_user["last_successful_login"]:
        last_login = cf_user["last_successful_login"]
        if isinstance(last_login, str):
            last_login = datetime.strptime(last_login, "%Y-%m-%d %H:%M:%S%z")
        if isinstance(last_login, datetime):
            if last_login.tzinfo is None:
                last_login = last_login.replace(tzinfo=timezone.utc)
            if last_login < inactivity_threshold:
                return True, f"Inactive for more than {config.INACTIVITY_DAYS_THRESHOLD} days"
    return False, ""


def format_result(users, cloudflare_group_update_result, cloudflare_users, seat_removal_results):
    return {
        "status": "success",
        "users": {
            "count": len(users.users),
            "data": [
                {
                    "id": user.id,
                    "name": user.details.name if user.details else "N/A",
                    "email": user.details.email if user.details else "N/A",
                    "role": user.role,
                    "availability": user.availability,
                }
                for user in users.users
            ],
        },
        "cloudflare_group_update": cloudflare_group_update_result,
        "cloudflare_users": cloudflare_users,
        "seat_removal_results": seat_removal_results,
    }


def handle_error(e):
    if config.DEBUG:
        error_result = {
            "status": "error",
            "message": "An unexpected error occurred",
            "error_details": str(e),
        }
    else:
        error_result = {"status": "error"}

    logger.error(f"Error handled: {str(e)}")
    return error_result
