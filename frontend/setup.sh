#!/bin/bash
# Enhanced script to set up the LocaVox frontend project

# Make script executable
chmod +x setup.sh

# Color variables for nice output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up LocaVox Frontend...${NC}"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm is not installed. Please install Node.js and npm first.${NC}"
    exit 1
fi

# Print node and npm versions
echo -e "${GREEN}Node version:${NC}"
node --version
echo -e "${GREEN}NPM version:${NC}"
npm --version

# Check for existing node_modules
if [ -d "node_modules" ]; then
    echo -e "${YELLOW}Existing node_modules directory detected.${NC}"
    read -p "Do you want to perform a clean installation? This will remove node_modules and package-lock.json (y/n): " clean_install
    if [[ $clean_install == "y" ]]; then
        echo "Cleaning previous installation..."
        rm -rf node_modules package-lock.json
        echo "Previous installation cleaned!"
    fi
fi

# Install dependencies
echo -e "${GREEN}Installing dependencies...${NC}"
npm install

# Check if installation was successful
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Dependencies installed successfully!${NC}"
    
    # Verify critical packages are installed
    echo -e "${GREEN}Verifying critical dependencies...${NC}"
    
    # Function to check package
    check_package() {
        if [ -d "node_modules/$1" ]; then
            echo -e "  ✅ $1 is installed"
        else
            echo -e "  ${RED}⚠️ $1 might be missing${NC}"
            npm install $1 --save
        fi
    }
    
    # Check core dependencies
    check_package "react"
    check_package "react-dom"
    check_package "react-router-dom"
    check_package "@chakra-ui/react"
    check_package "axios"
    
    echo -e "${GREEN}You can now start the development server with: npm run dev${NC}"
else
    echo -e "${RED}❌ Error installing dependencies. Please check the logs above.${NC}"
    exit 1
fi

# Create a .env.local file if it doesn't exist
if [ ! -f ".env.local" ]; then
    echo "Creating .env.local file..."
    cat > .env.local << EOL
# API settings - customize as needed
VITE_API_BASE_URL=http://localhost:8080

# Auth settings
VITE_AUTH_ENABLED=true

# Debug settings
VITE_LOG_LEVEL=debug
EOL
    echo -e "${GREEN}Created .env.local file with default settings${NC}"
else
    echo -e "${YELLOW}Using existing .env.local file${NC}"
fi

# Clean cache if needed
read -p "Do you want to clear browser cache? This can help with stale files (y/n): " clear_cache
if [[ $clear_cache == "y" ]]; then
    echo "To clear your browser cache:"
    echo "  • Chrome: Press Ctrl+Shift+Delete"
    echo "  • Firefox: Press Ctrl+Shift+Delete" 
    echo "  • Edge: Press Ctrl+Shift+Delete"
    echo ""
    echo "Remember to check 'Cached images and files' option"
fi

# Setup complete
echo -e "${GREEN}Setup complete! 🚀${NC}"
echo "----------------------------"
echo -e "${GREEN}Available commands:${NC}"
echo "  npm run dev      - Start development server"
echo "  npm run build    - Build for production"
echo "  npm run preview  - Preview production build"
echo "----------------------------"
echo -e "${GREEN}Troubleshooting:${NC}"
echo "  • If the app doesn't load, check browser console (F12) for errors"
echo "  • Make sure backend server is running at http://localhost:8080"
echo "  • Try clearing browser cache and restarting the development server"
echo "----------------------------"
