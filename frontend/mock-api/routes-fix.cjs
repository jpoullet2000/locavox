/**
 * This script applies custom routes and fixes login-related 404 errors
 * It will be used directly in server.cjs
 */

function applyCustomRoutes(server, router, jsonServer) {
    // Direct route handlers for auth endpoints without the /auth prefix
    server.post('/login', (req, res, next) => {
        console.log('🔐 Login request received at /login');

        // Handle login directly rather than forwarding
        const { email, password } = req.body;

        if (!email || !password) {
            return res.status(400).json({ message: 'Email and password are required' });
        }

        const db = router.db;
        const user = db.get('users').find({ email, password }).value();

        if (!user) {
            console.log('❌ Login failed: invalid credentials for', email);
            return res.status(401).json({ message: 'Invalid credentials' });
        }

        // Create a token (in a real app, use JWT)
        const token = Buffer.from(`${email}:${Date.now()}`).toString('base64');

        const responseUser = { ...user };
        delete responseUser.password; // Don't send password back to client

        console.log('✅ Login successful for:', email);
        return res.status(200).json({ token, user: responseUser });
    });

    server.post('/register', (req, res) => {
        console.log('🔐 Register request received at /register');

        const { email, password, displayName } = req.body;

        if (!email || !password) {
            return res.status(400).json({ message: 'Email and password are required' });
        }

        const db = router.db;
        const user = db.get('users').find({ email }).value();

        if (user) {
            console.log('❌ Registration failed: user already exists');
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

        console.log('✅ Registration successful for:', email);
        return res.status(200).json({ token, user: responseUser });
    });

    server.get('/me', (req, res) => {
        console.log('🔐 Me request received at /me');
        const authHeader = req.headers.authorization;

        if (!authHeader || !authHeader.startsWith('Bearer ')) {
            console.log('❌ Auth check failed: missing or invalid token');
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
                console.log('❌ Auth check failed: user not found for token');
                return res.status(401).json({ message: 'User not found' });
            }

            const responseUser = { ...user };
            delete responseUser.password; // Don't send password back

            console.log('✅ Auth check successful for:', email);
            return res.json(responseUser);
        } catch (error) {
            console.log('❌ Auth check failed: error decoding token', error);
            return res.status(401).json({ message: 'Invalid token' });
        }
    });

    server.post('/logout', (req, res) => {
        console.log('🔐 Logout request received at /logout');
        // In a real app, invalidate the token
        console.log('✅ Logout successful');
        return res.status(200).json({ message: 'Logged out successfully' });
    });

    // Enhanced route rewriting - IMPORTANT: We need to use jsonServer.rewriter correctly
    const routes = {
        "/api/*": "/$1",
        "/login": "/login",
        "/register": "/register",
        "/logout": "/logout",
        "/me": "/me",
        "/auth/login": "/login",
        "/auth/register": "/register",
        "/auth/logout": "/logout",
        "/auth/me": "/me",
        "/users/:userId/messages": "/messages?userId=:userId"
    };

    console.log('🔄 Registering custom route mappings:', Object.keys(routes).join(', '));

    // The key fix: Return the rewriter middleware itself, not a function that creates it
    return {
        routes,
        middleware: jsonServer.rewriter(routes)  // THIS is the fix - we return the middleware directly
    };
}

module.exports = applyCustomRoutes;
