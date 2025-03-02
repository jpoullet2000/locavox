#!/bin/bash

# Create the public directory if it doesn't exist
mkdir -p public

# Create a simple favicon using ImageMagick if available
if command -v convert &> /dev/null; then
    echo "Creating favicon.ico using ImageMagick..."
    convert -size 32x32 \
            -background '#3182CE' \
            -fill white \
            -gravity center \
            label:LV \
            public/favicon.ico
    echo "✅ Created favicon.ico"
else
    # If ImageMagick is not available, create an empty file as a placeholder
    echo "ImageMagick not found. Creating an empty favicon.ico placeholder..."
    touch public/favicon.ico
    echo "✅ Created empty favicon.ico placeholder"
fi

echo "✅ Setup complete!"
