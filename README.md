# Business Verification API (v1.0)

### Backend API

**Business Verification API**

A robust business verification application with VAT validation via VIES. Built to explore FastAPI and learn how to integrate external SOAP services and handle rate limiting.

### Why this stack?

I wanted to get hands-on with FastAPI and see how it handles high-performance operations using endpoints and database integration. Since this project focuses on reliability and external service communication, I used PostgreSQL for persistence and SlowAPI to manage traffic — this keeps the backend focused purely on data integrity and security.

The project taught me:
- How to structure a professional FastAPI application
- Working with legacy SOAP services (VIES) using Zeep
- Managing database migrations with Alembic
- Implementing secure JWT-based authentication
- Protecting endpoints with rate limiting

### Features

- **Validate Business**: Verify tax IDs (NIP) against the official VIES service.
- **Search History**: View your past verification requests with pagination.
- **Usage Statistics**: Get insights into your activity:
    - Total searches count
    - Most searched tax IDs
    - Active VAT status percentage
- **Rate Limiting**:
    - Automatic protection (e.g., 10/minute for validation)
    - All times handled in UTC
- **Secure Access**: Fully authenticated endpoints using JWT tokens.

### Tech Stack

#### Backend
- FastAPI
- SQLAlchemy (PostgreSQL)
- Zeep (SOAP client)
- Pydantic for validation
- SlowAPI for rate limiting
- Alembic for migrations

#### Infrastructure
- Docker
- PostgreSQL

### Testing & Quality Assurance

To ensure the reliability of the API and database operations the project includes a planned comprehensive test suite:
- **Integration Tests**: (Planned for v2.0) covering the full validation lifecycle
- **API Simulation**: Using FastAPI's TestClient to simulate real-world requests
- **Isolated Database**: Configured to run on separate environments for safe testing
- **Note on current state**: Verification is currently done through manual end-to-end testing and logging. Automated CI/CD with GitHub Actions is prepared for the next release.

To run the application locally:
```bash
docker compose up --build
```

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Set up environment variables**
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

3. **Initialize the database**
   ```bash
   # Run with docker
   docker compose up --build
   ```

The app will be available at:
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Project Structure

```
├── alembic/                # Database migration scripts
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/  # API route handlers
│   ├── core/               # Configuration, security, and logging
│   ├── db/                 # Database session and deps
│   ├── models/             # SQLAlchemy database models
│   ├── schemas/            # Pydantic models
│   ├── services/           # VIES and health services
│   └── main.py             # FastAPI entry point
├── alembic.ini             # Alembic configuration
├── docker-compose.yml
├── .env.example
├── requirements.txt
└── README.md
```

### What I learned?

- FastAPI makes building API surprisingly straightforward
- SOAP services can be tricky, but Zeep simplifies the integration significantly
- Docker is great for managing multiple services, especially PostgreSQL setups
- Alembic is essential for managing database schema evolutions
- Rate limiting is crucial for public-facing APIs to prevent abuse

### Future Improvements (Roadmap v2.0)

Things I'd add in the next version:
- **API Key**: Support for static API keys for service-to-service communication.
- **Redis Caching**: Caching VIES responses to speed up repeated lookups.
- **Rate Limit Headers**: Displaying `X-RateLimit-Remaining` to the user.
- **Pytest Suite**: Implementing full unit and integration test coverage.
- **Sentry**: Better error tracking and production monitoring.
- **Async VIES**: Refactoring the SOAP client for asynchronous operations.

### License

MIT

Feel free to use this as a reference or starting point for your own projects.
