#!/usr/bin/env python3
"""
FinBro.ai Backend Server

Production-grade Flask application with:
- Layered architecture (routes → services → repositories)
- Input validation with Pydantic
- Structured logging
- Rate limiting
- Comprehensive health checks

Usage:
    python app.py                    # Development mode
    FLASK_ENV=production python app.py  # Production mode
"""
import os
import sys

# Ensure the app package is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def main():
    """Run the Flask application."""
    from app import create_app
    
    # Get environment
    env = os.getenv('FLASK_ENV', 'development')
    debug = env == 'development'
    
    # Create and run app
    app = create_app(env)
    
    print(f"\n🚀 FinBro.ai Backend v2.0.0")
    print(f"📍 Environment: {env}")
    print(f"🔧 Debug mode: {debug}")
    print(f"🌐 Running on: http://localhost:5000")
    print(f"📊 Health check: http://localhost:5000/api/health")
    print(f"\nPress Ctrl+C to stop\n")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=debug,
        threaded=True
    )


if __name__ == '__main__':
    main()