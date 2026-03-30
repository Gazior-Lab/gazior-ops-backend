# Gazior Ops Backend

A scalable backend system for Gazior Ops built with FastAPI and PostgreSQL.

## Tech Stack
- **Framework:** FastAPI
- **Database:** PostgreSQL (asyncpg)
- **ORM & Migrations:** SQLAlchemy 2.0 & Alembic
- **Validation:** Pydantic
- **Development & Linting:** Hatchling, Ruff, Mypy, Pytest

## Quick Start

### 1. Set up a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the root directory and configure it. At minimum, you will need:
```env
# Example .env configuration
APP_ENV=development
DEBUG=True
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/db_name
SECRET_KEY=your-secret-key-here
```

### 4. Run the development server
Start the local server using the following command:
```bash
python run.py
```
*(In development mode with `APP_ENV=development`, tables are auto-created on startup.)*

The API will be available at `http://localhost:8000`. You can test by navigating to `http://localhost:8000/` or `http://localhost:8000/docs` in your browser.


## 📂 Architecture Overview

This backend is designed with a production-ready **Layered Architecture**.
*   **`app/api/`**: The Controller Layer containing your FastAPI routers and dependencies (e.g., `get_db`).
*   **`app/schemas/`**: The Validation Layer storing all Pydantic DTOs for strict type-checking on HTTP requests/responses.
*   **`app/services/`**: The Business Logic Layer handling the core application features independent of HTTP or DB routing. 
*   **`app/repositories/`**: The Data Access Layer centralizing all SQLAlchemy database queries safely.
*   **`app/models/`**: The Data Layer housing your SQLAlchemy table classes.
*   **`app/core/`**: Security (`jwt`, `hashing`), Custom exceptions, and Global Configurations.
*   **`app/db/`**: Connection logic, asynchronous engines, and `Base` metadata.