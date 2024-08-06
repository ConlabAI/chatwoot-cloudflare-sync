# Chatwoot-Cloudflare User Sync

This application synchronizes users between Chatwoot and Cloudflare Access, running in a Docker container. It performs the following tasks:

1. Fetches users from Chatwoot
2. Updates a Cloudflare Access group with active Chatwoot users
3. Removes Cloudflare Access seats for users who are no longer in Chatwoot or have been inactive for a specified period

## Prerequisites

- Docker
- Chatwoot instance with API access
- Cloudflare Access configured

## Setup

1. Clone this repository:
   ```
   git clone https://github.com/conlabai/chatwoot-cloudflare-sync.git
   cd chatwoot-cloudflare-sync
   ```

2. Create a `.env` file in the project root with the following content:
   ```
   CHATWOOT_URL=https://your-chatwoot-instance.com
   CHATWOOT_ACCOUNT_ID=your-chatwoot-account-id
   CHATWOOT_API_KEY=your-chatwoot-api-key
   CLOUDFLARE_API_TOKEN=your-cloudflare-api-token
   CLOUDFLARE_ACCOUNT_ID=your-cloudflare-account-id
   CLOUDFLARE_ACCESS_GROUP_ID=your-cloudflare-access-group-id
   CLOUDFLARE_ACCESS_GROUP_NAME=Your Access Group Name
   INACTIVITY_DAYS_THRESHOLD=7
   DEBUG=false
   ```

   Replace the placeholder values with your actual configuration.

3. Build the Docker image:
   ```
   docker build -t chatwoot-cloudflare-sync .
   ```

4. Run the Docker container:
   ```
   docker run -d -p 8000:8000 --env-file .env chatwoot-cloudflare-sync
   ```

4. Alternatively, you can use Docker Compose to run the container:
   ```
   docker-compose up -d
   ```

   This will build the image if necessary and start the container in detached mode.

## Usage

The application exposes a FastAPI endpoint at `http://localhost:8000/`. You can trigger the synchronization by sending a GET request to this endpoint.

To set up automatic synchronization, you can use a cron job or a scheduling service to periodically call this endpoint.

## Development

To run the application locally for development:

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the FastAPI application:
   ```
   python src/api.py
   ```

This will start a local development server at `http://localhost:8000/`.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.