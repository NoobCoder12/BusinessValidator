# Business Verification API

A REST API that lets users verify whether a business is an active VAT taxpayer using its NIP (tax ID). Built with FastAPI and integrated with the official VIES SOAP service.

---

## Why this project?

I built this to get hands-on experience with FastAPI and explore how to integrate with external SOAP services. Along the way I also tackled rate limiting, JWT authentication, database migrations, and Docker — things that come up in real backend projects.

**What I learned:**
- Structuring a professional FastAPI application
- Working with legacy SOAP services using Zeep
- Managing database schema changes with Alembic
- Implementing JWT-based authentication (access + refresh tokens)
- Protecting public endpoints with rate limiting

---

## Features

- **Business Validation** — verify a NIP against the official VIES service
- **Search History** — paginated list of past verification requests
- **Usage Statistics** — total searches, most searched NIPs, active VAT percentage
- **Rate Limiting** — 10 requests/minute on validation endpoints (UTC)
- **JWT Auth** — all endpoints protected with access and refresh tokens

---

## Tech Stack

**Backend:** FastAPI, SQLAlchemy, Pydantic, Zeep, SlowAPI, Alembic  
**Database:** PostgreSQL  
**Infrastructure:** Docker

---

## Quick Start

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
ACCESS_TOKEN_EXPIRE=30

REFRESH_TOKEN_KEY=your_refresh_secret_key_here
REFRESH_ACCESS_TOKEN_EXPIRE=60
```

### 3. Run with Docker
```bash
docker compose up --build
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs

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

- **API Key support** — static keys as an alternative to JWT for service-to-service communication
- **Redis caching** — cache VIES responses to avoid redundant external calls
- **Rate limit headers** — expose `X-RateLimit-Remaining` so clients know their usage
- **Pytest suite** — unit and integration test coverage
- **Async VIES** — the current SOAP client is synchronous and blocks the event loop, worth fixing
- **Sentry** — error tracking for production monitoring

---

## License

MIT — feel free to use this as a reference or starting point.