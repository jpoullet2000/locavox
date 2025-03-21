# Backend API Documentation

## Project Structure

```
backend/
├── locavox/           # Python package with FastAPI implementation
│   ├── models/        # Data models
│   ├── routers/       # API route definitions
│   ├── services/      # Business logic
│   └── db/            # Database connections and queries
├── tests/             # Test suite
└── mock/              # Mock server for development
```

## Installation

To install the required dependencies:

```bash
cd /home/jbp/projects/locavox/backend
poetry install
```

## Running the Application

To run the application with hot reloading:

```bash
cd /home/jbp/projects/locavox/backend
uvicorn locavox.main:app --reload --port 8000
```

This will start the server at http://localhost:8000

## Troubleshooting

### SQLite Database Locking Issues

SQLite may experience database locking errors ("database is locked") during concurrent access or if a process crashes without properly closing connections. Common symptoms include:

- Error messages containing `[SQLITE_BUSY] The database file is locked`
- Authentication issues even with correct credentials
- API requests failing with 500 errors

#### Using the Database Lock Fix Tool

The project includes a utility to diagnose and fix database locking issues:

```bash
# Install required dependency
pip install psutil

# Check if the database is locked and identify locking processes
python -m locavox.tools.run_fix_db --check --identify

# Attempt to release locks (safe operation)
python -m locavox.tools.run_fix_db --release

# For more aggressive fixing (use with caution)
python -m locavox.tools.run_fix_db --release --kill --force --repair
```

#### Quick Fixes

If you're experiencing database lock issues:

1. **Restart your application**: Stop all running instances and restart
2. **Check for zombie processes**: Look for hanging Python processes
3. **Delete journal files**: As a last resort, delete `-journal`, `-wal`, and `-shm` files (may cause data loss)
4. **Verify authentication**: Run the diagnostic tool to check credentials:
   ```bash
   python -m tests.test_auth_login_issue <username> <password>
   ```

#### Prevention

To prevent database locking issues:

- Avoid long-running transactions
- Ensure proper connection closing with context managers
- Consider using a more robust database like PostgreSQL for production environments
- Use connection pooling with appropriate timeouts

## Real Backend

The real backend API runs on port 8000 by default. The main implementation is in the `locavox` Python package.

## Endpoints

### Topics

- `GET /topics` - Get all topics
  - URL: `http://localhost:8000/topics`
  - Response: Array of topic objects
    ```json
    [
      {
        "id": "1",
        "name": "General",
        "description": "General discussions about the community",
        "icon": "💬"
      },
      ...
    ]
    ```

### Messages

- `POST /topics/:topicName/messages` - Create a new message in a topic
  - URL: `http://localhost:8000/topics/:topicName/messages`
  - Request body:
    ```json
    {
      "content": "Message content",
      "userId": "user-id",
      "metadata": {}
    }
    ```
  - Response: Created message object

- `GET /topics/:topicName/messages` - Get all messages in a topic
  - URL: `http://localhost:8000/topics/:topicName/messages`
  - Response: Array of message objects

- `GET /users/:userId/messages` - Get all messages by a user
  - URL: `http://localhost:8000/users/:userId/messages`
  - Response: Object containing user messages

- `DELETE /topics/:topicName/messages/:messageId` - Delete a specific message
  - URL: `http://localhost:8000/topics/:topicName/messages/:messageId`
  - Headers:
    - Authorization: `Bearer <jwt_token>`
  - Authorization: Only the message creator can delete their own messages
  - Response: Status 204 (No Content)
  - Error responses:
    - 401: Unauthorized (missing or invalid token)
    - 403: Forbidden (not the message creator)
    - 404: Message not found
    - 500: Server error

## Authentication

Most endpoints require authentication using a JWT token passed in the Authorization header as a Bearer token.
