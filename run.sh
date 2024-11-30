#!/bin/bash

# Get the directory of the script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the script directory
cd "$DIR"

# Load environment variables from .env file
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Set additional environment variables
export NODE_OPTIONS=--openssl-legacy-provider
export PYTHONHTTPSVERIFY=0
export OPENSSL_CONF=/dev/null
export FLASK_ENV=development
export FLASK_DEBUG=1

# Install required packages if not already installed
pip install pymongo[srv] dnspython python-dotenv

# Run the Flask application
python3 app.py
