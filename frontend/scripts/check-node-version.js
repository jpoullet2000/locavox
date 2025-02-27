const requiredVersion = '16.0.0';

if (process.versions.node.localeCompare(requiredVersion, undefined, { numeric: true }) < 0) {
    console.error(`Node.js version ${requiredVersion} or higher is required. Current version: ${process.versions.node}`);
    process.exit(1);
}
