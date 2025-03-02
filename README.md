# locavox
Locavox is a smart framework that connects local communities by routing questions and needs to the right topic, sparking seamless interactions with the help of AI


## Start the backend 

```
export LOCAVOX_DOT_ENV_FILE=<path_to_env_file>
# e.g. export LOCAVOX_DOT_ENV_FILE=./backend/.env
```

Browser (You)
    ↓
    ↓ HTTP requests to localhost:5173
    ↓
Vite Dev Server (port 5173) 
   ↑
   ↑ Serves HTML/JS/CSS for your app
   ↑
Frontend App Code
    ↓
    ↓ API calls to localhost:8080
    ↓
Mock API Server (port 8080)
    ↑
    ↑ Returns mock data
    ↑
Mock Database (in-memory)