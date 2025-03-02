#!/bin/bash

# Color variables for nice output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}LocaVox Mock API Server Repair Script${NC}"
echo "======================================"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}Error: Node.js is not installed!${NC}"
    echo "Please install Node.js before continuing."
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d 'v' -f 2)
echo -e "${GREEN}Using Node.js version:${NC} $NODE_VERSION"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo -e "${RED}Error: npm is not installed!${NC}"
    echo "Please install npm before continuing."
    exit 1
fi

# Print npm version
NPM_VERSION=$(npm -v)
echo -e "${GREEN}Using npm version:${NC} $NPM_VERSION"

# Create the mock-api directory if it doesn't exist
mkdir -p mock-api
echo -e "${GREEN}✓${NC} Created mock-api directory"

# Install json-server and concurrently
echo -e "\n${YELLOW}Installing required dependencies...${NC}"
npm install --save-dev json-server concurrently
echo -e "${GREEN}✓${NC} Dependencies installed"

# Check if json-server is properly installed
if ! ls node_modules/json-server &> /dev/null; then
    echo -e "${RED}Error: json-server was not installed correctly!${NC}"
    echo "Trying to install it explicitly..."
    npm install --save-dev json-server
    
    if ! ls node_modules/json-server &> /dev/null; then
        echo -e "${RED}Installation failed. Please install manually:${NC}"
        echo "npm install --save-dev json-server"
        exit 1
    fi
    echo -e "${GREEN}✓${NC} json-server installed successfully"
fi

# Create db.json with test data
echo -e "\n${YELLOW}Creating mock API data...${NC}"
cat > mock-api/db.json << 'EOL'
{
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
}
EOL
echo -e "${GREEN}✓${NC} Created db.json with test data"

# Create routes.json
cat > mock-api/routes.json << 'EOL'
{
  "/api/*": "/$1",
  "/auth/login": "/auth/login",
  "/auth/register": "/auth/register",
  "/auth/logout": "/auth/logout",
  "/auth/me": "/auth/me",
  "/users/:userId/messages": "/messages?userId=:userId"
}
EOL
echo -e "${GREEN}✓${NC} Created routes.json"

# Create server.js for CommonJS environment
cat > mock-api/server.js << 'EOL'
const jsonServer = require('json-server');
const path = require('path');
const fs = require('fs');

// Create the server
const server = jsonServer.create();

// Get the absolute path to db.json
const dbPath = path.join(__dirname, 'db.json');

// Check if db.json exists
if (!fs.existsSync(dbPath)) {
  console.error(`Error: ${dbPath} does not exist!`);
  process.exit(1);
}

// Create the router using the absolute path
const router = jsonServer.router(dbPath);

// Set default middlewares (logger, static, cors and no-cache)
const middlewares = jsonServer.defaults();
server.use(middlewares);

// Parse JSON bodies
server.use(jsonServer.bodyParser);

// Log all requests
server.use((req, res, next) => {
  console.log(`${req.method} ${req.path}`);
  next();
});

// Add custom routes before JSON Server router
server.post('/auth/register', (req, res) => {
  console.log('Register request received:', req.body);
  const { email, password, displayName } = req.body;
  
  if (!email || !password) {
    console.log('Registration failed: missing email or password');
    return res.status(400).json({ message: 'Email and password are required' });
  }
  
  const db = router.db; // Lowdb instance
  const user = db.get('users').find({ email }).value();
  
  if (user) {
    console.log('Registration failed: user already exists');
    return res.status(400).json({ message: 'User already exists' });
  }
  
  const newUser = { 
    id: Date.now().toString(), 
    email, 
    password,  // Note: In a real app, NEVER store passwords in plain text
    displayName: displayName || email.split('@')[0],
    photoURL: `https://ui-avatars.com/api/?name=${displayName || email.split('@')[0]}&background=random`
  };
  
  db.get('users').push(newUser).write();
  
  // Create a token (in a real app, use JWT)
  const token = Buffer.from(`${email}:${Date.now()}`).toString('base64');
  
  const responseUser = { ...newUser };
  delete responseUser.password; // Don't send password back to client
  
  console.log('Registration successful for:', email);
  res.status(200).json({ token, user: responseUser });
});

server.post('/auth/login', (req, res) => {
  console.log('Login request received:', req.body);
  const { email, password } = req.body;
  
  if (!email || !password) {
    console.log('Login failed: missing email or password');
    return res.status(400).json({ message: 'Email and password are required' });
  }
  
  const db = router.db;
  const user = db.get('users').find({ email, password }).value();
  
  if (!user) {
    console.log('Login failed: invalid credentials for', email);
    return res.status(401).json({ message: 'Invalid credentials' });
  }
  
  // Create a token (in a real app, use JWT)
  const token = Buffer.from(`${email}:${Date.now()}`).toString('base64');
  
  const responseUser = { ...user };
  delete responseUser.password; // Don't send password back to client
  
  console.log('Login successful for:', email);
  res.status(200).json({ token, user: responseUser });
});

server.get('/auth/me', (req, res) => {
  const authHeader = req.headers.authorization;
  
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    console.log('Auth check failed: missing or invalid token');
    return res.status(401).json({ message: 'Authorization token is required' });
  }
  
  const token = authHeader.split(' ')[1];
  
  try {
    // In a real app, verify JWT token
    // Here we just decode our simple token
    const decoded = Buffer.from(token, 'base64').toString();
    const email = decoded.split(':')[0];
    
    const db = router.db;
    const user = db.get('users').find({ email }).value();
    
    if (!user) {
      console.log('Auth check failed: user not found for token');
      return res.status(401).json({ message: 'User not found' });
    }
    
    const responseUser = { ...user };
    delete responseUser.password; // Don't send password back
    
    console.log('Auth check successful for:', email);
    res.json(responseUser);
  } catch (error) {
    console.log('Auth check failed: error decoding token', error);
    res.status(401).json({ message: 'Invalid token' });
  }
});

server.post('/auth/logout', (req, res) => {
  // In a real app, invalidate the token
  console.log('Logout successful');
  res.status(200).json({ message: 'Logged out successfully' });
});

// Get all topics
server.get('/topics', (req, res) => {
  const db = router.db;
  const topics = db.get('topics').value();
  console.log('Topics requested, returning:', topics.length, 'topics');
  res.json(topics);
});

// For any route that requires authentication
server.use((req, res, next) => {
  const protectedRoutes = [
    '/messages/create',
    '/users/profile'
  ];
  
  if (protectedRoutes.some(route => req.path.includes(route))) {
    const authHeader = req.headers.authorization;
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ message: 'Authorization required' });
    }
  }
  
  next();
});

// Use routes.json for custom routes
try {
  const routesPath = path.join(__dirname, 'routes.json');
  if (fs.existsSync(routesPath)) {
    const routes = require(routesPath);
    server.use(jsonServer.rewriter(routes));
    console.log('Using custom routes from routes.json');
  }
} catch (error) {
  console.log('Warning: Could not load routes.json -', error.message);
}

// Use default router
server.use(router);

// Start server
const port = process.env.PORT || 8080;
server.listen(port, () => {
  console.log(`\n=======================================`);
  console.log(`🚀 Mock API Server running on port ${port}`);
  console.log(`=======================================`);
  console.log(`\nTest user:`);
  console.log(`  Email: user@example.com`);
  console.log(`  Password: password123`);
  console.log(`\nAvailable endpoints:`);
  console.log(`  POST /auth/register - Register a new user`);
  console.log(`  POST /auth/login - Login with email/password`);
  console.log(`  GET /auth/me - Get current user (requires auth token)`);
  console.log(`  POST /auth/logout - Logout`);
  console.log(`  GET /topics - List all topics`);
  console.log(`\nPress Ctrl+C to stop the server\n`);
});

// Handle termination signals
process.on('SIGINT', () => {
  console.log('\nShutting down mock API server...');
  process.exit();
});
EOL
echo -e "${GREEN}✓${NC} Created server.js"

# Create a simple start script
cat > start-mock-api.sh << 'EOL'
#!/bin/bash
cd "$(dirname "$0")"
echo "Starting Mock API Server on port 8080..."
node mock-api/server.js
EOL
chmod +x start-mock-api.sh
echo -e "${GREEN}✓${NC} Created start-mock-api.sh script"

# Update package.json to add mock-api script if it doesn't exist
if ! grep -q "mock-api" package.json; then
    echo -e "\n${YELLOW}Updating package.json scripts...${NC}"
    
    # Create a temporary file for processing package.json
    TMP_FILE=$(mktemp)
    
    # Simple JSON manipulation to add the scripts
    node -e "
        const fs = require('fs');
        const packageJson = JSON.parse(fs.readFileSync('package.json'));
        
        if (!packageJson.scripts) {
            packageJson.scripts = {};
        }
        
        packageJson.scripts['mock-api'] = 'node mock-api/server.js';
        packageJson.scripts['dev-with-mock'] = 'concurrently \"npm run dev\" \"npm run mock-api\"';
        
        fs.writeFileSync('$TMP_FILE', JSON.stringify(packageJson, null, 2));
    "
    
    # Check if the temp file was created successfully and has content
    if [ -s "$TMP_FILE" ]; then
        cp "$TMP_FILE" package.json
        echo -e "${GREEN}✓${NC} Updated package.json with mock-api scripts"
    else
        echo -e "${RED}Failed to update package.json. Please add these scripts manually:${NC}"
        echo "\"mock-api\": \"node mock-api/server.js\""
        echo "\"dev-with-mock\": \"concurrently \\\"npm run dev\\\" \\\"npm run mock-api\\\"\""
    fi
    
    # Clean up
    rm -f "$TMP_FILE"
fi

echo -e "\n${GREEN}Setup complete!${NC}"
echo -e "To start the mock API server, run one of these commands:"
echo -e "  ${YELLOW}./start-mock-api.sh${NC}"
echo -e "  ${YELLOW}npm run mock-api${NC}"
echo -e "\nTo start both the frontend and mock API server together:"
echo -e "  ${YELLOW}npm run dev-with-mock${NC}"
echo -e "\n${GREEN}Test user:${NC}"
echo -e "  Email: user@example.com"
echo -e "  Password: password123"

# Offer to start the server now
echo -e "\n${YELLOW}Would you like to start the mock API server now? (y/n)${NC}"
read -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${GREEN}Starting mock API server...${NC}"
    echo -e "Press Ctrl+C to stop the server when you're done.\n"
    node mock-api/server.js
fi
