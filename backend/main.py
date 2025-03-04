from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from locavox.routers import topics, messages, users  # Updated import path

app = FastAPI(
    title="LocaVox API",
    description="API for the LocaVox community platform",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the routers
app.include_router(topics.router)
app.include_router(messages.router)
app.include_router(users.router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to the LocaVox API",
        "documentation": "/docs",
        "endpoints": {"topics": "/topics", "messages": "/messages", "users": "/users"},
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
