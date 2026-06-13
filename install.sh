#!/bin/bash

# Exit on error
set -e

echo "🏥 HMS Installation Helper"
echo "============================="

# 1. Check Python
if ! command -v python3 &> /dev/null
then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# 2. Create Virtual Environment
echo "📦 Setting up Python Virtual Environment (venv)..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# 3. Install Dependencies
echo "📥 Installing required python packages..."
pip install --upgrade pip
pip install mysql-connector-python flask

# 4. Handle .env configuration
if [ ! -f .env ]; then
    echo "⚙️ Creating configuration .env file from template..."
    cp .env.example .env
    echo "✅ .env file created. Please update it with your MySQL credentials."
else
    echo "ℹ️ .env file already exists. Skipping copy."
fi

echo "============================="
echo "🎉 Setup complete!"
echo "To run the Web App: source venv/bin/activate && python3 web_app.py"
echo "To run the Desktop App: source venv/bin/activate && python3 app.py"
