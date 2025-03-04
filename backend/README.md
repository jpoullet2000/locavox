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
