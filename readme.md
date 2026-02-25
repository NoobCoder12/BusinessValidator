# Business Verification API

A REST API that lets users verify whether a business is an active VAT taxpayer using its NIP (tax ID). Built with FastAPI and integrated with the official VIES SOAP service.

> **Version:** 1.2

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
- **Rate Limiting** — 10 requests/minute on validation endpoints (UTC)
- **JWT Auth** — user account management endpoints (register, login, token refresh)
- **Redis caching** — cache VIES responses to avoid redundant external calls
- **GUI** for redis and pgadmin

---

## Authentication

**JWT** — used for user account management.

**API Key** — required for all /business/ endpoints. Pass it via the `X-API-Key` header.

Generate a key (JWT required):
POST /api/v1/users/me/api-key

The raw key is returned once — store it securely. Only a bcrypt hash is saved in the database. Calling the endpoint again rotates the key.

---

## Tech Stack

**Backend:** FastAPI, SQLAlchemy, Pydantic, Zeep, SlowAPI, Alembic  
**Database:** PostgreSQL  
**Infrastructure:** Docker

---

## Quick Start

> Note: PostgreSQL runs in Docker. FastAPI and Alembic run locally in a virtual environment.

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
POSTGRES_SERVER=localhost
POSTGRES_DB=business_db

JWT_SECRET_KEY=your_secret_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE=minutes

REFRESH_TOKEN_KEY=your_refresh_secret_key_here
REFRESH_ACCESS_TOKEN_EXPIRE=days
```

### 3. Run Docker
```bash
docker compose up -d --build
```

### 4. Create and activate Virtual Environment
```
python3 -m venv venv
source venv/bin/activate
```

### 5. Install requirements
```
pip install -r requirements.txt
```

### 6. Create DB migrations
```
alembic upgrade head
```

### 7. Run API from root directory
```
uvicorn app.main:app --reload
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
├── .env.example
├── requirements.txt
└── README.md
```

---

## Testing

Currently verified through manual end-to-end testing. A full automated suite is planned for v2.0:

- Integration tests using FastAPI's `TestClient`
- Isolated test database
- GitHub Actions CI/CD pipeline
- Full pytest coverage (unit + integration)

---

## Roadmap (v1.5)

- **Rate limit headers** — expose `X-RateLimit-Remaining` so clients know their usage
- **Pytest suite** — unit and integration test coverage
- **Async VIES** — the current SOAP client is synchronous and blocks the event loop, worth fixing
- **Sentry** — error tracking for production monitoring

---

## Changelog

### v1.2
- Redis caching to avoid external API calls
- Docker container with pgadmin and redis insight as GUI

### v1.1
- All /business/ endpoints (validation, history, statistics) now use API Key only
- Keys generated via `POST /api/v1/users/me/api-key` (JWT required)
- Hashed with bcrypt, never stored in plaintext

### v1.0
- Initial release

---

## License

MIT — feel free to use this as a reference or starting point.