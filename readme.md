# Business Verification API

A REST API that lets users verify whether a business is an active VAT taxpayer using its NIP (tax ID). Built with FastAPI and integrated with the official VIES SOAP service.

> **Version:** 1.4

---

## Why this project?

I built this to get hands-on experience with FastAPI and explore how to integrate with external SOAP services. Along the way I also tackled rate limiting, JWT authentication, database migrations, and Docker — things that come up in real backend projects.

**What I learned:**
- Structuring a professional FastAPI application
- Working with legacy SOAP services using Zeep
- Managing database schema changes with Alembic
- Implementing JWT-based authentication (access + refresh tokens)
- Protecting public endpoints with rate limiting
- Generating and verifying hashed API keys as an alternative authentication method

---

## Features

- **Business Validation** — verify a NIP against the official VIES service (requires API Key)
- **Search History** — paginated list of past verification requests (requires API Key)
- **Usage Statistics** — total searches, most searched NIPs, active VAT percentage (requires API Key)
- **Rate Limiting** — 10 requests/minute on validation endpoints. Limit status is returned in every response via headers:
    - `X-RateLimit-Limit` — maximum requests allowed per minute
    - `X-RateLimit-Remaining` — requests left in the current window
    - `X-RateLimit-Reset` — Unix timestamp (UTC) when the window resets
- **JWT Auth** — user account management endpoints (register, login, token refresh)
- **Redis caching** — cache VIES responses to avoid redundant external calls
- **GUI** - for redis and pgadmin

---

## Authentication

**JWT** — used for user account management.

**API Key** — required for all /business/ endpoints. Pass it via the `X-API-Key` header.

Generate a key (JWT required):
POST /api/v1/auth/me/api-key

The raw key is returned once — store it securely. Only a bcrypt hash is saved in the database. Calling the endpoint again rotates the key.

---

## Tech Stack

**Backend:** FastAPI, SQLAlchemy, Pydantic, Zeep, SlowAPI, Alembic  
**Database:** PostgreSQL  
**Infrastructure:** Docker

---

## Quick Start

> Note: The entire stack (API, Database, Redis, and Alembic) is fully containerized. No local Python installation is required to run the app.

### 1. Clone the repository
```bash
git clone https://github.com/NoobCoder12/BusinessValidator.git
cd BusinessValidator
```

### 2. Set up environment variables

Create a `.env` file in the root directory:
```env
POSTGRES_USER=admin
POSTGRES_PASSWORD=yourpassword
POSTGRES_SERVER=db
POSTGRES_DB=business_db

JWT_SECRET_KEY=your_secret_key_here
JWT_ALGORITHM=HS256

# Value must be int (e.g. 30)
ACCESS_TOKEN_EXPIRE=30

REFRESH_TOKEN_KEY=your_refresh_secret_key_here

# Value must be int (e.g. 7)
REFRESH_ACCESS_TOKEN_EXPIRE=7
```

### 3. Run Docker
```bash
docker compose up -d --build
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs

GUI will be available at:
- **pgadmin**: http://localhost:5050
- **redis**: http://localhost:5540

---

## Project Structure
```
├── alembic/                # Database migrations
├── app/
│   ├── api/v1/endpoints/   # Route handlers
│   ├── core/               # Config, security, logging
│   ├── db/                 # Session and dependencies
│   ├── models/             # SQLAlchemy models
│   ├── schemas/            # Pydantic schemas
│   ├── services/           # VIES integration, health checks
│   └── main.py             # Entry point
├── docker-compose.yml
├── Dockerfile
├── .dockerignore
├── .env.example
├── requirements.txt
└── README.md
```

---

## Testing

Currently verified through manual end-to-end testing. A full automated suite is planned for v1.6:

- Integration tests using FastAPI's `TestClient`
- Isolated test database
- GitHub Actions CI/CD pipeline
- Full pytest coverage (unit + integration)

---

## Roadmap (v1.6)

- **Pytest suite** — unit and integration test coverage
- **Async VIES** — the current SOAP client is synchronous and blocks the event loop, worth fixing
- **Sentry** — error tracking for production monitoring

---

## Changelog

### v1.4
- Added rate limit headers to responses (`X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`)
- Username instead of a nickname in Pydantic

### v1.3
- Docker container for FastAPI
- User registration fix

### v1.2
- Redis caching to avoid external API calls
- Docker container with pgadmin and redis insight as GUI

### v1.1
- All /business/ endpoints (validation, history, statistics) now use API Key only
- Keys generated via `POST /api/v1/auth/me/api-key` (JWT required)
- Hashed with bcrypt, never stored in plaintext

### v1.0
- Initial release

---

## License

MIT — feel free to use this as a reference or starting point.