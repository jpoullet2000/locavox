# Locavox
Locavox is a smart framework that connects local communities by routing questions and needs to the right topic, sparking seamless interactions with the help of AI

## Installation and Setup

### Prerequisites
- Python 3.11 or higher
- pip (Python package installer)
- poetry (recommended)
- PostgreSQL (recommended) or SQLite

### Installing Dependencies

1. Clone the repository
   ```bash
   git clone https://github.com/jpoullet2000/locavox.git
   cd locavox
   ```

2. Create a virtual environment (optional but recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   poetry install
   ```

4. For PostgreSQL support (recommended for production)
   ```bash
   pip install asyncpg
   ```

   or with `poetry`
   ```bash
   poetry install --with database
   ```

   You might need to install system-level dependencies:
   - Ubuntu/Debian: `sudo apt-get install libpq-dev`
   - RHEL/CentOS: `sudo dnf install postgresql-devel`
   - macOS (with Homebrew): `brew install postgresql`

5. For SQLite support (development/testing)
   ```bash
   pip install aiosqlite
   ```

### Configuration

1. Create a `.env` file in the project root by copying the example
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file to set your configuration values:
   - Set the `DATABASE_URL` for your database connection
   - Configure other settings as needed

## Running the Application

1. Initialize the database
   ```bash
   python -m backend.locavox.cli init-db
   ```

2. Start the server
   ```bash
   uvicorn backend.locavox.main:app --reload
   ```

3. Access the application at http://localhost:8000

## Docker Setup

For a quick development setup with Docker:

### Using Docker Compose

1. Start PostgreSQL with Docker Compose:
   ```bash
   docker-compose up -d postgres
   ```

2. This will create two databases:
   - `locavox` - Main development database
   - `locavox_test` - Test database

3. Configure your application to use the dockerized PostgreSQL:
   ```bash
   cp .env.docker .env
   ```

4. Access PostgreSQL:
   ```bash
   # Using psql client
   psql -h localhost -p 5432 -U locavox_user -d locavox
   # Password: locavox_pass
   ```

### Database Connection Details

- **Main Database**:
  - Host: `localhost` (or `postgres` from other containers)
  - Port: `5432`
  - Database name: `locavox`
  - Username: `locavox_user`
  - Password: `locavox_pass`
  - Connection string: `postgresql+asyncpg://locavox_user:locavox_pass@localhost:5432/locavox`

- **Test Database**:
  - Database name: `locavox_test`
  - Username: `locavox_test`
  - Password: `locavox_test`
  - Connection string: `postgresql+asyncpg://locavox_test:locavox_test@localhost:5432/locavox_test`

## Development

### Running Tests
```bash
pytest
```

### Code Structure
- `backend/` - Backend application code
  - `locavox/` - Main application package
    - `models/` - Data models and schemas
    - `services/` - Business logic
    - `routers/` - API endpoints
    - `utils/` - Utility functions and helpers

## Start the backend 

```
export LOCAVOX_DOT_ENV_FILE=<path_to_env_file>
# e.g. export LOCAVOX_DOT_ENV_FILE=./backend/.env
```

## Developer's guide

### Project Structure
```
locavox/
├── frontend/        # React frontend application
├── backend/         # Node.js backend server
└── ...
```

### Using the real backend

To use the real backend API, ensure that the backend server is running on port 8000:

```
cd backend
npm run start
```

### Using the mock backend

If you need to use the mock API for development purposes, run from the `backend` folder:

```
npm run dev-with-mock
```

The frontend is configured to automatically fall back to the mock API (port 8080) if the real backend (port 8000) is unavailable.

### API Fallback Flow
```
Frontend App
    ↓
    ↓ First tries API calls to localhost:8000
    ↓
Real Backend API (port 8000)
    ↓
    ↓ If real backend fails
    ↓
Mock API Server (port 8080)
    ↓
    ↓ If mock API also fails
    ↓
Hardcoded fallback values
```

This ensures your application remains functional in various development scenarios.

## Administration Tools

### Creating Admin Users

To create an administrator user with elevated permissions, use the following command:

```bash
cd /home/jbp/projects/locavox/backend
python -m locavox.tools.create_admin --username admin --email admin@example.com --password securepassword
```

Options:
- `--username` or `-u`: Admin username (required)
- `--email` or `-e`: Admin email address (required)
- `--password` or `-p`: Admin password (required)
- `--force` or `-f`: Override existing user with the same username or email

This will create a new user with superuser privileges who can access administrative functions in the application.

### Inspecting Database Tables

To view all tables in the database and inspect their structure, use the following command:

```bash
cd /home/jbp/projects/locavox/backend
python -m locavox.tools.log_tables
```

Options:
- `--verbose` or `-v`: Show detailed information about columns and constraints
- `--data` or `-d`: Show sample data from each table
- `--limit` or `-l`: Maximum number of rows to show when displaying sample data (default: 5)

This tool helps verify that all expected tables have been created correctly in the database.