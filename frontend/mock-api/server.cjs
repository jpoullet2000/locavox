// This is a CommonJS version of the server
const jsonServer = require('json-server');
const path = require('path');
const fs = require('fs');
const express = require('express');
const applyCustomRoutes = require('./routes-fix.cjs');

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

// Enhanced error logging
const logErrorDetails = (err) => {
    console.error('\n💥 ERROR DETAILS:');
    console.error(`Message: ${err.message}`);
    console.error(`Stack: ${err.stack}`);
    console.error('-------------------------------\n');
};

// Set up static file directories - multiple paths for flexibility
const publicPath = path.resolve(__dirname, '../public');
const srcPath = path.resolve(__dirname, '../src');
const rootPath = path.resolve(__dirname, '..');
const distPath = path.resolve(__dirname, '../dist');

console.log(`Serving static files from multiple paths:`);
console.log(`- Primary public path: ${publicPath}`);
console.log(`- Source path: ${srcPath}`);
console.log(`- Root path: ${rootPath}`);
console.log(`- Dist path: ${distPath}`);

// Ensure the public directory exists
if (!fs.existsSync(publicPath)) {
    console.log(`Creating missing public directory: ${publicPath}`);
    fs.mkdirSync(publicPath, { recursive: true });
}

// Set default middlewares with single static path
// Fix: Using just publicPath as the static path (not an array)
const middlewares = jsonServer.defaults({
    bodyParser: true,
    static: publicPath // Single path instead of array
});
server.use(middlewares);

// Make sure body parsing works correctly
server.use(express.json());
server.use(express.urlencoded({ extended: true }));

// Add additional static middleware for other directories
console.log('Adding additional static middleware for other directories');
server.use(express.static(publicPath));
server.use('/src', express.static(srcPath));
server.use('/assets', express.static(path.join(rootPath, 'assets')));
server.use('/assets', express.static(path.join(publicPath, 'assets')));
server.use('/images', express.static(path.join(publicPath, 'images')));
server.use('/icons', express.static(path.join(publicPath, 'icons')));

// Create common missing files
const createMissingFiles = () => {
    // Files to check/create
    const filesToCreate = [
        {
            path: path.join(publicPath, 'manifest.json'),
            content: JSON.stringify({
                "short_name": "LocaVox",
                "name": "LocaVox - Community Connection Platform",
                "icons": [
                    {
                        "src": "favicon.ico",
                        "sizes": "64x64 32x32 24x24 16x16",
                        "type": "image/x-icon"
                    },
                    {
                        "src": "logo192.png",
                        "type": "image/png",
                        "sizes": "192x192"
                    },
                    {
                        "src": "logo512.png",
                        "type": "image/png",
                        "sizes": "512x512"
                    }
                ],
                "start_url": ".",
                "display": "standalone",
                "theme_color": "#3182CE",
                "background_color": "#ffffff"
            }, null, 2)
        },
        {
            path: path.join(publicPath, 'robots.txt'),
            content: `User-agent: *\nDisallow: `
        },
        {
            path: path.join(publicPath, 'favicon.ico'),
            create: true // Just create an empty file
        },
        {
            path: path.join(publicPath, 'logo192.png'),
            create: true // Just create an empty file
        },
        {
            path: path.join(publicPath, 'logo512.png'),
            create: true // Just create an empty file
        }
    ];

    // Check and create each file
    filesToCreate.forEach(file => {
        if (!fs.existsSync(file.path)) {
            console.log(`Creating missing file: ${file.path}`);
            try {
                if (file.content) {
                    fs.writeFileSync(file.path, file.content);
                } else if (file.create) {
                    // Create empty file
                    fs.writeFileSync(file.path, '');
                }
                console.log(`✅ Created ${file.path}`);
            } catch (err) {
                console.error(`❌ Failed to create ${file.path}: ${err.message}`);
            }
        } else {
            console.log(`File already exists: ${file.path}`);
        }
    });

    // Create assets directory if it doesn't exist
    const assetsDir = path.join(publicPath, 'assets');
    if (!fs.existsSync(assetsDir)) {
        console.log(`Creating assets directory: ${assetsDir}`);
        fs.mkdirSync(assetsDir, { recursive: true });
    }
};

// Create any missing files before starting the server
createMissingFiles();

// Custom handler for special files
server.get('/manifest.json', (req, res) => {
    const manifestPath = path.join(publicPath, 'manifest.json');

    if (fs.existsSync(manifestPath)) {
        res.sendFile(manifestPath);
        console.log(`Served manifest.json from ${manifestPath}`);
    } else {
        console.log(`manifest.json not found at ${manifestPath}, creating default`);
        const defaultManifest = {
            "short_name": "LocaVox",
            "name": "LocaVox - Community Connection Platform",
            "icons": [
                {
                    "src": "favicon.ico",
                    "sizes": "64x64 32x32 24x24 16x16",
                    "type": "image/x-icon"
                }
            ],
            "start_url": ".",
            "display": "standalone",
            "theme_color": "#3182CE",
            "background_color": "#ffffff"
        };

        // Write the file for future requests
        fs.writeFileSync(manifestPath, JSON.stringify(defaultManifest, null, 2));
        res.json(defaultManifest);
    }
});

// Handle %PUBLIC_URL% references and other path variables
server.use((req, res, next) => {
    const originalUrl = req.url;

    // Replace template variables
    if (req.path.includes('%PUBLIC_URL%')) {
        req.url = req.url.replace(/%PUBLIC_URL%/g, '');
        console.log(`Transformed ${originalUrl} to ${req.url}`);
    }

    // Other common template variables
    if (req.path.includes('${VITE_')) {
        // Handle VITE_ environment variables
        req.url = req.url.replace(/\${VITE_[^}]+}/g, '');
        console.log(`Transformed ${originalUrl} to ${req.url}`);
    }

    next();
});

// Log which file is being requested with detailed info to debug 404s
server.use((req, res, next) => {
    console.log(`📄 ${req.method} ${req.path}`);
    if (req.path.endsWith('.js') || req.path.endsWith('.css') || req.path.endsWith('.json')) {
        console.log(`  Possible locations for ${req.path}:`);
        [publicPath, srcPath, rootPath].forEach(basePath => {
            const fullPath = path.join(basePath, req.path);
            console.log(`  - ${fullPath} ${fs.existsSync(fullPath) ? '✅' : '❌'}`);
        });
    }
    next();
});

// Apply custom routes to fix login 404 errors - FIXED: Pass jsonServer as parameter and use middleware
const customRoutes = applyCustomRoutes(server, router, jsonServer);
// Use the middleware returned by applyCustomRoutes
server.use(customRoutes.middleware);
console.log(`Applied custom routes for auth endpoints: ${Object.keys(customRoutes.routes).slice(0, 5).join(', ')}...`);

// Enhanced 404 handler to provide more information
server.use((req, res, next) => {
    if (!res.headersSent) {
        console.log(`⚠️ 404 for ${req.method} ${req.originalUrl}`);

        // Check if it's a login-related request and provide a helpful message
        if (req.path.includes('login') || req.path.includes('auth')) {
            console.log('❗ Auth-related 404 error. Routes that should be available:');
            console.log('  - POST /login');
            console.log('  - POST /auth/login');
            console.log('  - POST /register');
            console.log('  - GET /me');
        }

        // Check if it's an asset request
        if (req.path.match(/\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$/)) {
            console.log(`Missing asset: ${req.path}`);

            // For development, return a transparent 1x1 pixel for images to prevent console errors
            if (req.path.match(/\.(png|jpg|jpeg|gif|ico|svg)$/)) {
                console.log(`Serving empty image for ${req.path}`);
                res.set('Content-Type', 'image/png');
                res.send(Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=', 'base64'));
                return;
            }
        }

        res.status(404).json({
            status: 404,
            message: 'Not Found',
            path: req.originalUrl,
            timestamp: new Date().toISOString()
        });
    } else {
        next();
    }
});

// Use default router for any routes not matched by custom handlers
server.use(router);

// Start server with improved error handling
const port = process.env.PORT || 8080;
console.log(`Will attempt to listen on port ${port}`);

// Check if port is available before attempting to listen
const net = require('net');
const testServer = net.createServer();

testServer.once('error', (err) => {
    if (err.code === 'EADDRINUSE') {
        console.error(`⚠️ Port ${port} is already in use.`);
        console.error(`Please try a different port by setting the PORT environment variable:`);
        console.error(`   PORT=8081 node mock-api/server.cjs`);
        process.exit(1);
    } else {
        console.error(`Error checking port: ${err.message}`);
        logErrorDetails(err);
    }
});

testServer.once('listening', () => {
    // If we can listen on the port, it's free, so close it and start the real server
    testServer.close(() => {
        server.listen(port, () => {
            console.log(`\n=======================================`);
            console.log(`🚀 Mock API Server running on port ${port}`);
            console.log(`=======================================`);
            console.log(`\nTest user:`);
            console.log(`  Email: user@example.com`);
            console.log(`  Password: password123`);
            console.log(`\nAvailable endpoints:`);
            console.log(`  POST /login - Login with email/password`);
            console.log(`  POST /register - Register a new user`);
            console.log(`  GET /me - Get current user (requires auth token)`);
            console.log(`  POST /logout - Logout`);
            console.log(`  GET /topics - List all topics`);
            console.log(`\nServing static files from multiple locations`);
            console.log(`\nPress Ctrl+C to stop the server\n`);
        });
    });
});

// Check if port is available
console.log(`Checking if port ${port} is available...`);
testServer.listen(port);

// Handle termination signals
process.on('SIGINT', () => {
    console.log('\nShutting down mock API server...');
    process.exit();
});
