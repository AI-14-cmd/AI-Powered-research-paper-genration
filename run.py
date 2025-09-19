#!/usr/bin/env python3
"""
AI Research Paper Generator - Startup Script
Hackathon Project 2024
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app

if __name__ == '__main__':
    print("[STARTUP] AI Research Paper Generator")
    print("[FEATURES] Real Citations | Plagiarism Check | PDF Export")
    print("[ACCESS] http://localhost:5000")
    print("=" * 50)
    
    # Run the Flask application
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        threaded=True
    )