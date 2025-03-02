#!/bin/bash

# Color variables for nice output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up Mock API Server for LocaVox...${NC}"

# Create the mock-api directory if it doesn't exist
mkdir -p mock-api

# Function to check and create a file
create_file() {
    local file=$1
    local content=$2
    
    if [ ! -f "$file" ]; then
        echo -e "${YELLOW}Creating $file...${NC}"
        echo "$content" > "$file"
        echo -e "${GREEN}✅ Created $file${NC}"
    else
        echo -e "${YELLOW}$file already exists, skipping...${NC}"
    fi
}

# Install required dependencies
echo -e "${GREEN}Installing required dependencies...${NC}"
npm install --save-dev json-server concurrently

# Create db.json if it doesn't exist
DB_JSON='{
  "users": [
    {
      "id": "1",
      "email": "user@example.com",
      "password": "password123",
      "displayName": "Demo User",
      "photoURL": "https://via.placeholder.com/150"
    }
  ],
  "topics": [
    {
      "id": "1",
      "name": "General",
      "description": "General neighborhood discussions"
    },
    {
      "id": "2",
      "name": "Events",
      "description": "Local events and gatherings"
    },
    {
      "id": "3",
      "name": "Services",
      "description": "Local services and recommendations"
    }
  ],
  "messages": [
    {
      "id": "1",
      "content": "Welcome to the General discussion!",
      "userId": "1",
      "timestamp": "2023-07-15T12:00:00Z",
      "topicId": "1",
      "metadata": {
        "priority": "high"
      }
    },
    {
      "id": "2",
      "content": "Is anyone interested in a community picnic next weekend?",
      "userId": "1",
      "timestamp": "2023-07-16T14:30:00Z",
      "topicId": "2",
      "metadata": {
        "eventDate": "2023-07-30"
      }
    },
    {
      "id": "3",
      "content": "I am looking for a reliable plumber in the neighborhood.",
      "userId": "1",
      "timestamp": "2023-07-17T09:45:00Z",
      "topicId": "3",
      "metadata": {
        "urgency": "medium"
      }
    }
  ]
}'

create_file "mock-api/db.json" "$DB_JSON"

# Create routes.json if it doesn't exist
ROUTES_JSON='{
  "/api/*": "/$1",
  "/auth/login": "/auth/login",
  "/auth/register": "/auth/register",
  "/auth/logout": "/auth/logout",
  "/auth/me": "/auth/me",
  "/users/:userId/messages": "/messages?userId=:userId"
}'

create_file "mock-api/routes.json" "$ROUTES_JSON"

# Create server.js if it doesn't exist
SERVER_JS='const jsonServer = require("json-server");
const path = require("path");
const server = jsonServer.create();
const router = jsonServer.router(path.join(__dirname, "db.json"));
const middlewares = jsonServer.defaults();

// Set default middlewares (logger, static, cors and no-cache)
server.use(middlewares);
server.use(jsonServer.bodyParser);

// Add custom routes before JSON Server router
server.post("/auth/register", (req, res) => {
  const { email, password, displayName } = req.body;
  
  if (!email || !password) {
    return res.status(400).json({ message: "Email and password are required" });
  }
  
  const db = router.db; // Lowdb instance
  const user = db.get("users").find({ email }).value();
  
  if (user) {
    return res.status(400).json({ message: "User already exists" });
  }
  
  const newUser = { 
    id: Date.now().toString(), 
    email, 
    password,  // Note: In a real app, NEVER store passwords in plain text
    displayName: displayName || email.split("@")[0],
    photoURL: `https://ui-avatars.com/api/?name=${displayName || email.split("@")[0]}&background=random`
  };
  
  db.get("users").push(newUser).write();
  
  // Create a token (in a real app, use JWT)
  const token = Buffer.from(`${email}:${Date.now()}`).toString("base64");
  
  const responseUser = { ...newUser };
  delete responseUser.password; // Do not send password back to client
  
  res.status(200).json({ token, user: responseUser });
});

server.post("/auth/login", (req, res) => {
  const { email, password } = req.body;
  
  if (!email || !password) {
    return res.status(400).json({ message: "Email and password are required" });
  }
  
  const db = router.db;
  const user = db.get("users").find({ email, password }).value();
  
  if (!user) {
    return res.status(401).json({ message: "Invalid credentials" });
  }
  
  // Create a token (in a real app, use JWT)
  const token = Buffer.from(`${email}:${Date.now()}`).toString("base64");
  
  const responseUser = { ...user };
  delete responseUser.password; // Do not send password back to client
  
  res.status(200).json({ token, user: responseUser });
});

server.get("/auth/me", (req, res) => {
  const authHeader = req.headers.authorization;
  
  if (!authHeader || !authHeader.startsWith("Bearer ")) {
    return res.status(401).json({ message: "Authorization token is required" });
  }
  
  const token = authHeader.split(" ")[1];
  
  try {
    // In a real app, verify JWT token
    // Here we just decode our simple token
    const decoded = Buffer.from(token, "base64").toString();
    const email = decoded.split(":")[0];
    
    const db = router.db;
    const user = db.get("users").find({ email }).value();
    
    if (!user) {
      return res.status(401).json({ message: "User not found" });
    }
    
    const responseUser = { ...user };
    delete responseUser.password; // Do not send password back
    
    res.json(responseUser);
  } catch (error) {
    res.status(401).json({ message: "Invalid token" });
  }
});

server.post("/auth/logout", (req, res) => {
  // In a real app, invalidate the token
  res.status(200).json({ message: "Logged out successfully" });
});

// Get all topics
server.get("/topics", (req, res) => {
  const db = router.db;
  const topics = db.get("topics").value().map(topic => topic.name);
  res.json(topics);
});

// Get messages for a topic
server.get("/topics/:topicName/messages", (req, res) => {
  const topicName = req.params.topicName;
  const db = router.db;
  
  // Find the topic by name
  const topic = db.get("topics").find({ name: topicName }).value();
  
  if (!topic) {
    return res.status(404).json({ message: "Topic not found" });
  }
  
  // Get messages for this topic
  const messages = db.get("messages").filter({ topicId: topic.id }).value();
  
  res.json(messages);
});

// For any route that requires authentication
server.use((req, res, next) => {
  const protectedRoutes = [
    "/messages/create",
    "/users/profile"
  ];
  
  if (protectedRoutes.some(route => req.path.includes(route))) {
    const authHeader = req.headers.authorization;
    
    if (!authHeader || !authHeader.startsWith("Bearer ")) {
      return res.status(401).json({ message: "Authorization required" });
    }
  }
  
  next();
});

// Routes config
const routes = require("./routes.json");
server.use(jsonServer.rewriter(routes));

// Use default router
server.use(router);

// Start server
const port = process.env.PORT || 8080;
server.listen(port, () => {
  console.log(`Mock API Server is running on port ${port}`);
  console.log(`\nTest user:\n  Email: user@example.com\n  Password: password123\n`);
});'

create_file "mock-api/server.js" "$SERVER_JS"

# Create start-mock-api.sh if it doesn't exist
START_MOCK_API='#!/bin/bash
cd "$(dirname "$0")"
echo "Starting Mock API Server on port 8080..."
node mock-api/server.js'

create_file "start-mock-api.sh" "$START_MOCK_API"
chmod +x start-mock-api.sh

echo -e "${GREEN}Setup complete! 🚀${NC}"
echo -e "${GREEN}To start the mock API server:${NC}"
echo -e "  ./start-mock-api.sh"
echo -e "  - or -"
echo -e "  npm run mock-api"
echo -e "\n${GREEN}To start both frontend and mock API:${NC}"
echo -e "  npm run dev-with-mock"
echo -e "\n${GREEN}Default test user:${NC}"
echo -e "  Email: user@example.com"
echo -e "  Password: password123"
