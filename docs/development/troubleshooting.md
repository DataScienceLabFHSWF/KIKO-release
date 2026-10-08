# 🐛 Troubleshooting in KIKO

## Backend logs

Follow backend logs:

```bash
docker compose --env-file .env.dev -p <YOUR_PROJECT_NAME> -f docker-compose.dev.yml logs -f kiko-backend-service-dev
```

Show the last 200 backend log lines:

```bash
docker compose --env-file .env.dev -p <YOUR_PROJECT_NAME> -f docker-compose.dev.yml logs --tail=200 kiko-backend-service-dev
```

Show backend logs with timestamps:

```bash
docker compose --env-file .env.dev -p <YOUR_PROJECT_NAME> -f docker-compose.dev.yml logs -f --timestamps kiko-backend-service-dev
```

Using the container name directly:

```bash
docker logs -f kiko-backend-service-dev
```

## Password reset email logs

In development, `EMAIL_PROVIDER=console` prints password-reset emails to the backend logs.

Search for password-reset links:

```bash
docker logs kiko-backend-service-dev 2>&1 | grep -i "reset-password"
```

Search for console email debug output:

```bash
docker logs kiko-backend-service-dev 2>&1 | grep -i "KIKO EMAIL DEBUG"
```

## Other service logs

Frontend:

```bash
docker compose --env-file .env.dev -p <YOUR_PROJECT_NAME> -f docker-compose.dev.yml logs -f kiko-frontend-service-dev
```

Database:

```bash
docker compose --env-file .env.dev -p <YOUR_PROJECT_NAME> -f docker-compose.dev.yml logs -f kiko-db-service-dev
```

Ollama:

```bash
docker compose --env-file .env.dev -p <YOUR_PROJECT_NAME> -f docker-compose.dev.yml logs -f kiko-ollama-service-dev
```
