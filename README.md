# Bit Bot

## Getting Started

### Prerequisites:
- Python

1. Create and activate a [Python virtual environment](https://docs.python.org/3/library/venv.html)
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Create a file `.env` and paste the secrets from the Exec Bitwarden
4. Run the bot:
```bash
flask run -p 8080
```

## Deployment
Bit Bot is deployed as an Azure App Service on the free tier. When deploying for
the first time, environment variables must be installed manually. The CI/CD
pipeline builds and uploads a new Docker image. Updates to the Docker image must
be deployed manually by restarting the App Service.