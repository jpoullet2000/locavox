#!/bin/bash

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Creating LocaVox static assets...${NC}"

# Make sure the public directory exists
mkdir -p public/assets
mkdir -p public/images
mkdir -p public/icons

# Create a simple favicon.ico using base64 data
echo -e "${GREEN}Creating favicon.ico...${NC}"
cat > public/favicon.ico << 'EOL'
AAABAAEAEBAAAAEAIABoBAAAFgAAACgAAAAQAAAAIAAAAAEAIAAAAAAAAAQAABILAAASCwAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAxsbGAJubmwCUlJQAlJSUAJubmwDGxsYAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAA9fX1AMvLy0OQkJCPd3d3mnZ2dpp/f3+PoKCgQ+/v7wAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAADLy8sAm5ubPICAgOBdXV3/QEBA/zg4OP9AQED/XV1d/35+fuCX
l5c89fX1AAAAAAAAAAAAAAAAAPr6+gCkpKQAfHx8j2VlZf8/Pz//Li4u/ygoKP8mJib/KCgo/y4u
Lv8/Pz//ZGRk/3x8fI+ioqIA9fX1AAAAAACkpKQAkZGRj2BgYP8wMDD/JiYm/yMjI/8iIiL/ISEh
/yIiIv8jIyP/JiYm/zAwMP9gYGD/kZGRj6SkpAAAAAAAlJSUj2JiYv8sLCz/IyMj/yAgIP8fHx//
Hh4e/x4eHv8eHh7/Hx8f/yAgIP8jIyP/LCws/2FhYf+Tk5OPAAAAAJSUlJpISEj/JiYm/yEhIf8f
Hx//HR0d/xwcHP8bGxv/HBwc/x0dHf8fHx//ISEh/yYmJv9GRkb/k5OTmgAAAACUlJSaQkJC/yQk
JP8gICD/Hh4e/x0dHf8cHBz/Gxsb/xwcHP8dHR3/Hh4e/yAgIP8kJCT/QUFB/5OTk5oAAAAAlJSU
j1tbW/8oKCj/ISEh/x8fH/8eHh7/HR0d/xwcHP8dHR3/Hh4e/x8fH/8hISH/KCgo/1paWv+Tk5OP
AAAAAKSkpACRkZGPWlpa/y4uLv8jIyP/ISEh/yAgIP8fHx//ICAg/yEhIf8jIyP/Li4u/1lZWf+R
kZGPpKSkAAAAAAAAAAAApKSkAHx8fI9aWlr/Ozs7/ysrK/8nJyf/JiYm/ycnJ/8rKyv/Ozs7/1pa
Wv98fHyPpKSkAPX19QAAAAAAAAAAAMvLywCbm5s8fn5+4FJSUv82Njb/LCws/ywsLP82Njb/UlJS
/35+fuCbm5s89fX1AAAAAAAAAAAAAAAAAAAAAAD19fUAy8vLQ5CQkI9/f3+adnZ2mnZ2dpp/f3+P
kJCQQ8vLywD19fUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMbGxgCbm5sAlJSUAJSUlACU
lJQAlJSUAJubmwDGxsYAAAAAAAAAAAAAAAAA//8AAP//AAD+fwAA/B8AAPgPAADwBwAA4AMAAMAD
AADAAwAA4AMAAPAHAA/4DwAP/B8AD/5/AA//fwAA//8AAA==
EOL

# Create a simple index.html fallback
echo -e "${GREEN}Creating index.html fallback...${NC}"
cat > public/index.html << 'EOL'
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="theme-color" content="#3182CE" />
    <meta name="description" content="LocaVox - Connect with your local community" />
    <link rel="manifest" href="/manifest.json" />
    <title>LocaVox</title>
    <style>
      body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        margin: 0;
        padding: 0;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 100vh;
        background-color: #f8f9fa;
      }
      header {
        text-align: center;
        margin-bottom: 2rem;
      }
      h1 {
        color: #3182CE;
        font-size: 2.5rem;
      }
      .content {
        max-width: 600px;
        padding: 2rem;
        background-color: white;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
      }
      .loading {
        display: inline-block;
        width: 50px;
        height: 50px;
        border: 5px solid rgba(49, 130, 206, 0.3);
        border-radius: 50%;
        border-top-color: #3182CE;
        animation: spin 1s linear infinite;
        margin: 2rem 0;
      }
      @keyframes spin {
        to { transform: rotate(360deg); }
      }
    </style>
  </head>
  <body>
    <div class="content">
      <header>
        <h1>LocaVox</h1>
        <p>A community connection platform</p>
      </header>
      <p>Loading the application...</p>
      <div class="loading"></div>
      <p id="status">Please wait while we set things up.</p>
    </div>
    <script>
      // Check if the real app is loaded elsewhere
      setTimeout(() => {
        document.getElementById('status').innerText = 
          'If the application doesn\'t load automatically, please check your console for errors.';
      }, 5000);
    </script>
  </body>
</html>
EOL

# Create a simple logo
echo -e "${GREEN}Creating logo192.png...${NC}"
cat > public/logo192.png << 'EOL'
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
Wwr8V96QxvN7pTx2ObH7pXbv