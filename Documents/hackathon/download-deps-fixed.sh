#!/bin/bash

# Create lib directory
mkdir -p lib

echo "Downloading React dependencies..."

# Download React (production versions)
curl -L -o lib/react.production.min.js https://unpkg.com/react@18/umd/react.production.min.js
curl -L -o lib/react-dom.production.min.js https://unpkg.com/react-dom@18/umd/react-dom.production.min.js

# Download React (development versions)
curl -L -o lib/react.development.js https://unpkg.com/react@18/umd/react.development.js
curl -L -o lib/react-dom.development.js https://unpkg.com/react-dom@18/umd/react-dom.development.js

# Download Babel
curl -L -o lib/babel.min.js https://unpkg.com/@babel/standalone/babel.min.js

# Download Font Awesome CSS
curl -L -o lib/fontawesome.css https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css

# Download Font Awesome Web Fonts
mkdir -p lib/webfonts
curl -L -o lib/webfonts/fa-solid-900.woff2 https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/fa-solid-900.woff2
curl -L -o lib/webfonts/fa-regular-400.woff2 https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/fa-regular-400.woff2
curl -L -o lib/webfonts/fa-brands-400.woff2 https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/fa-brands-400.woff2

echo "Dependencies downloaded successfully!"
echo ""
echo "File sizes:"
ls -lh lib/
echo ""
echo "Now you can use these options:"
echo "1. Use ankid-robust.html (with multiple CDN fallbacks)"
echo "2. Use ankid-simple.html (no external dependencies)"
echo "3. Modify your original index.html to use local files:"
echo ""
echo "Replace the CDN links with:"
echo '<script src="./lib/react.development.js"></script>'
echo '<script src="./lib/react-dom.development.js"></script>'
echo '<script src="./lib/babel.min.js"></script>'
echo '<link href="./lib/fontawesome.css" rel="stylesheet">'
