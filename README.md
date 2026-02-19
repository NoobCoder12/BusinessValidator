# Reminder App (v1.0)

### Backend Tests

**Reminder App**

A reminder application with email notifications. Built to explore FastAPI and learn how to integrate background task processing with Celery.

### Why this stack?

I wanted to get hands-on with FastAPI and see how it handles operations using endpoints and background tasks. Since FastAPI doesn't use templates like Django or Flask, I paired it with React for the frontend — this kept the backend focused purely on API logic.

The project taught me:
- How to structure FastAPI application
- Working with Celery for scheduled tasks
- Managing timezones properly (UTC in backend, local time in frontend)
- Creating basic frontend using React

### Features

- Create reminders with title, description, deadline and email
- Choose when to get notified:
    - 15 minutes before
    - 1 hour before
    - 1 day before
- Automatic email notifications via Celery Beat:
    - Tasks are checked/sent every minute by default (can be edited in `backend/app/config/celery_app.py`)
    - All times stored in UTC, displayed in local timezone

### Tech Stack

#### Backend
- FastAPI
- SQLAlchemy (SQLite)
- Celery + Redis
- Pydantic for validation
- Pytest

#### Frontend
- React

#### Infrastructure
- Docker

### Testing & Quality Assurance

To ensure the reliability of the API and database operations the project includes a comprehensive test suite:
- **Integrations Tests**: Built with Pytest, covering the full CRUD lifecycle
- **API Simulation**: Uses FastAPI's TestClient with httpx to simulate real-world requests
- **Isolated Database**: Tests run on separate, temporary SQLite database to ensure no side effects on development base
- **CI/CD Pipeline**: Automated testing via GitHub Actions. Every push and pull request triggers the test suite on clean Linux environment.
- **Note on Celery Testing**: Background workers and email tasks are currently excluded from the integration suite to keep the CI pipeline lightweight. These components are verified through manual end-to-end testing with a Redis broker.

To run tests locally:
```bash
cd backend
pytest --cov=app --cov-report=term-missing
```

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Reminder
   ```

2. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   MAIL_HOST=smtp.gmail.com
   MAIL_USERNAME=your_email@gmail.com
   MAIL_PASSWORD=your_app_password
   MAIL_PORT=587
   ```
   *Note: Password should be app password, not the one you use to log in to Gmail.*
   [Learn more about app passwords](https://support.google.com/mail/answer/185833?hl=en#zippy=)

3. **Run FastAPI to create database:**
   ```bash
   cd backend/app
   fastapi dev main.py
   ```
   After seeing "test.db" in `db/` press CTRL + C to close the server.

4. **Run with Docker**
   ```bash
   docker compose up --build
   ```

The app will be available at:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Project Structure

```
├── .github/workflows/
│   └── tests.yml           # Config file for GitHub Actions
│
├── backend/
│   ├── app/
│   │   ├── config/
│   │   ├── main.py         # FastAPI routes
│   │   ├── schemas.py      # Pydantic models
│   │   ├── send_mail.py    # Email logic
│   │   └── tasks.py        # Celery tasks
│   │
│   ├── db/
│   │   ├── models.py       # SQLAlchemy models
│   │   ├── crud.py         # Database operations
│   │   └── base.py         # DB connection
│   │
│   ├── tests/
│   │   ├── conftest.py     # Config file with fixtures
│   │   └── test_api.py     # File with tests
│   │
│   ├── Dockerfile
│   ├── requirements.txt
│   └── pytest.ini          # Config file for pytest
│
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── docker-compose.yml
├── .env
└── README.md
```

### What I learned?

- FastAPI makes building API surprisingly straightforward
- Celery Beat is perfect for recurring tasks, but need careful timezone handling for tasks connected with time
- Docker is great for managing multiple services, especially when each one of them needs command to start in different terminal
- SQLite is fine for development, but production may need PostgreSQL
- Creating basic layout with React and its structure

### Future Improvements (Roadmap v2.0)

Planned features for the next version:
- **API Key**: Implementation of API key authentication.
- **Redis Caching**: Integration of Redis for high-performance caching.
- **Rate Limit Display**: Real-time display of remaining rate limit quota.
- **Comprehensive Testing**: Full test suite expansion with Pytest.
- **User Authentication**: Ensuring reminders are private to each user.
- **PostgreSQL**: Migration from SQLite to PostgreSQL for production use.
- **Mobile Notifications**: Sending alerts directly to mobile phones.
- **Better Error Handling**: Improved validation and user feedback.
- **Deployment**: Full production deployment setup.

### License

MIT

Feel free to use this as a reference or starting point for your own projects.
