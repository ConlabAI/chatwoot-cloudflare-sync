from environs import Env

env = Env()
env.read_env()

# Get environment variables
CHATWOOT_URL = env.str("CHATWOOT_URL")
CHATWOOT_ACCOUNT_ID = env.str("CHATWOOT_ACCOUNT_ID")
CHATWOOT_API_KEY = env.str("CHATWOOT_API_KEY")
CLOUDFLARE_API_TOKEN = env.str("CLOUDFLARE_API_TOKEN")
CLOUDFLARE_ACCOUNT_ID = env.str("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_ACCESS_GROUP_ID = env.str("CLOUDFLARE_ACCESS_GROUP_ID")
CLOUDFLARE_ACCESS_GROUP_NAME = env.str("CLOUDFLARE_ACCESS_GROUP_NAME")
INACTIVITY_DAYS_THRESHOLD = env.int("INACTIVITY_DAYS_THRESHOLD", 7)
DEBUG = env.bool("DEBUG", False)