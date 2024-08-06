# Chatwoot-Cloudflare User Sync

This application synchronizes users between Chatwoot and Cloudflare Access, running on Cloudflare Workers using Python. It performs the following tasks:

1. Fetches users from Chatwoot
2. Updates a Cloudflare Access group with active Chatwoot users
3. Removes Cloudflare Access seats for users who are no longer in Chatwoot or have been inactive for a specified period

## Prerequisites

- Cloudflare Workers account
- Chatwoot instance with API access
- Cloudflare Access configured

## Setup

1. Clone this repository:
   ```
   git clone https://github.com/your-username/chatwoot-cloudflare-sync.git
   cd chatwoot-cloudflare-sync
   ```

2. Install Wrangler CLI:
   ```
   npm install -g @cloudflare/wrangler
   ```

3. Authenticate Wrangler with your Cloudflare account:
   ```
   wrangler login
   ```

4. Create a `wrangler.toml` file in the project root with the following content:
   ```toml
   name = "chatwoot-cloudflare-sync"
   main = "src/entry.py"
   compatibility_date = "2024-07-26"
   compatibility_flags = ["python_workers"]

   [vars]
   CHATWOOT_URL = "https://your-chatwoot-instance.com"
   CHATWOOT_ACCOUNT_ID = "your-chatwoot-account-id"
   CLOUDFLARE_ACCOUNT_ID = "your-cloudflare-account-id"
   CLOUDFLARE_ACCESS_GROUP_ID = "your-cloudflare-access-group-id"
   CLOUDFLARE_ACCESS_GROUP_NAME = "Your Access Group Name"
   INACTIVITY_DAYS_THRESHOLD = "7"
   DEBUG = "false"
   ```

   Replace the placeholder values with your actual configuration.

5. Add your secrets using Wrangler:
   ```
   wrangler secret put CHATWOOT_API_KEY
   wrangler secret put CLOUDFLARE_API_TOKEN
   ```

6. Deploy the worker:
   ```
   wrangler deploy
   ```

## Usage

The worker will run on a schedule or can be triggered manually through the Cloudflare dashboard. It will synchronize users between Chatwoot and Cloudflare Access based on the configured settings.

## Development

To run the worker locally for development:

1. Create a `.dev.vars` file in the project root with your secrets:
   ```
   CHATWOOT_API_KEY=your_chatwoot_api_key
   CLOUDFLARE_API_TOKEN=your_cloudflare_api_token
   ```

2. Run the worker locally:
   ```
   wrangler dev
   ```

This will start a local development server that you can use to test and debug your worker. The `.dev.vars` file will be used to provide the necessary secrets during local development, without exposing them in your `wrangler.toml` file.

Note: Make sure to add `.dev.vars` to your `.gitignore` file to prevent accidentally committing sensitive information to your repository.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.