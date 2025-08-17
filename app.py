"""
Root app.py for Railway deployment
This file helps Railway detect the Python application and imports from backend
"""

import sys
import os

# Add backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import the main Flask app from backend
from backend.app import app

# For Railway deployment
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 