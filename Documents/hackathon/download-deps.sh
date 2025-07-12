#!/bin/bash

# Create lib directory
mkdir -p lib

echo "Downloading React dependencies..."

# Download React
curl -o lib/react.development.js https://unpkg.com/react@18/umd/react.development.js
curl -o lib/react-dom.development.js https://unpkg.com/react-dom@18/umd/react-dom.development.js

# Download Babel
curl -o lib/babel.min.js https://unpkg.com/@babel/standalone/babel.min.js

# Download Tailwind CSS
curl -o lib/tailwind.min.css https://unpkg.com/tailwindcss@3.4.0/dist/tailwind.min.css

# Download Font Awesome
curl -o lib/fontawesome.min.css https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css

echo "Dependencies downloaded to lib/ directory"
echo "Update your HTML file to use local paths"
