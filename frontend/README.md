# LocaVox Frontend

A community connection platform that brings neighbors together.

## Getting Started

### Prerequisites

- Node.js (v18 or newer)
- npm or yarn

### Installation

1. Clone the repository
2. Install dependencies:

```bash
cd frontend
npm install
```

### Running the Development Server

#### Option 1: Frontend Only (requires backend server)

```bash
npm run dev
```

#### Option 2: Frontend with Mock API Server

```bash
npm run dev-with-mock
```

This will start both the frontend development server and a mock API server.

### Mock API Credentials

For testing with the mock API, you can use these credentials:

- Email: user@example.com
- Password: password123

Or register a new user through the registration form.

## Available Scripts

- `npm run dev`: Start the development server
- `npm run build`: Build for production
- `npm run preview`: Preview production build
- `npm run lint`: Run linting
- `npm run mock-api`: Run just the mock API server
- `npm run dev-with-mock`: Run both frontend and mock API server

## Project Structure

- `/src`: Source files
  - `/components`: Reusable React components
  - `/contexts`: React context providers
  - `/pages`: Page components
  - `/api`: API client functions
  - `/utils`: Utility functions
  - `/hooks`: Custom React hooks

## Mock API

The mock API server provides:

- Authentication (register, login, profile)
- Topics listing
- Messages (create, list, search)

API endpoints:
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login
- `GET /auth/me` - Get current user profile
- `POST /auth/logout` - Logout
- `GET /topics` - Get all topics
- `GET /topics/:name` - Get a specific topic
- `GET /messages` - Get all messages

## Environment Variables

Create a `.env.local` file for local development:

```
VITE_API_BASE_URL=http://localhost:8080
```

## Learn More

For more information about the tools used in this project:

- [React](https://reactjs.org/)
- [Vite](https://vitejs.dev/)
- [Chakra UI](https://chakra-ui.com/)
- [React Router](https://reactrouter.com/)
