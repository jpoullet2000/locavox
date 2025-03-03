# locavox
Locavox is a smart framework that connects local communities by routing questions and needs to the right topic, sparking seamless interactions with the help of AI


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