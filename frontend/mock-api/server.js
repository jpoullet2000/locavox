// Convert from CommonJS to ES Module syntax
import jsonServer from 'json-server';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

// Get __dirname equivalent in ESM
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

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
        // Use dynamic import for ES modules
        const routesModule = JSON.parse(fs.readFileSync(routesPath, 'utf8'));
        server.use(jsonServer.rewriter(routesModule));
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
