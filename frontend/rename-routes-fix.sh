#!/bin/bash

# Move the routes-fix.js to routes-fix.cjs
mv mock-api/routes-fix.js mock-api/routes-fix.cjs

# Update the import in server.cjs
sed -i 's/require(\.\/routes-fix)/require(\.\/routes-fix.cjs)/' mock-api/server.cjs

echo "Renamed routes-fix.js to routes-fix.cjs and updated references"
