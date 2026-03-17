# Business Verification API

[![Backend Tests](https://github.com/NoobCoder12/BusinessValidator/actions/workflows/tests.yml/badge.svg)](https://github.com/NoobCoder12/BusinessValidator/actions/workflows/tests.yml)

A REST API that lets users verify whether a business is an active VAT taxpayer using its NIP (tax ID). Built with FastAPI and integrated with the official VIES SOAP service.

> **Version:** 1.7.0

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
- Integrating Sentry for error tracking and performance monitoring

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
- **GUI** — for redis and pgadmin
- **Sentry** — see [Monitoring](#monitoring)
- **Pytest** - see [Testing](#testing)

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
**Infrastructure:** Docker, Sentry
**Testing:** pytest, pytest-asyncio, httpx

---

## Monitoring

### Sentry Integration

Integrated Sentry SDK for error tracking and performance monitoring:

- SQLAlchemy and Redis integrations provide **Breadcrumbs** (query/cache history) attached to every error report
- FastAPI dependency automatically injects user context (`ID`, `Username`) into Sentry events — passwords are filtered out
- `traces_sample_rate: 1.0` in dev for full request tracing

A global exception handler catches unhandled exceptions, reports them to Sentry, and returns a JSON response with a unique **Event ID** — making it easy to locate the exact error in the dashboard.

Errors trigger an automatic email notification to the app owner.

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

# Optional
SENTRY_URL=your_dsn_url
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


### 4. GUI Access (Optional)

**pgAdmin**
Default credentials: 
- Login: `admin@test.com`
- Password: `admin`

Add a new server: 
- host: `db`
- port: `5432` 
- database: from `.env` (POSTGRES_DB)
- credentials: from `.env` (POSTGRES_USER, POSTGRES_PASSWORD)

**Redis Insight**
Add a new database: 
- Connection URL: `redis://redis:6379`

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

The project includes an automated test suite built with **pytest** and **pytest-asyncio**.

- **Integration tests** — endpoint testing using `httpx.AsyncClient` with an isolated PostgreSQL test database, created fresh and dropped after each test
- **Unit tests** — validators and Pydantic schemas tested directly without HTTP layer
- **Mocking** — external services (VIES, httpx) are mocked to avoid real API calls and ensure deterministic results
- **CI/CD** — GitHub Actions runs the full suite on every push and pull request
- **Coverage** — minimum 80% enforced via `pytest-cov`

---

## Changelog

### v1.7.0
- Automated test suite with pytest and pytest-asyncio
- Integration tests with isolated test database
- GitHub Actions CI/CD pipeline
- 80% coverage enforced via pytest-cov

### v.1.6.0
- Asynchronous requests for Zeep

### v1.5.1
- GUI configuration instruction added to readme

### v1.5.0
- Sentry integration for error tracking and performance monitoring

### v1.4.1
- Fixed Redis caching in Docker (incorrect localhost hostname replaced with redis service name)

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