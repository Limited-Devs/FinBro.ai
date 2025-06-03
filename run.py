#!/usr/bin/env python3
"""
Simple script to build frontend and run the full stack app
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, cwd=None):
    """Run a command and return success status"""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("🚀 Building and starting full stack application...")
    
    # Check if directories exist
    if not (Path("frontend").exists() and Path("backend").exists()):
        print("❌ Error: Please run this script from the root directory containing 'frontend' and 'backend' folders!")
        return
    
    # Build frontend
    print("\n📦 Building React frontend...")
    if not run_command("npm run build", cwd="frontend"):
        print("❌ Frontend build failed!")
        return
    
    print("✅ Frontend built successfully!")
    
    # Start backend server
    print("\n🔧 Starting Flask server on http://localhost:5000...")
    print("Press Ctrl+C to stop the server\n")
    
    try:
        subprocess.run([sys.executable, "app.py"], cwd="backend")
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped!")

if __name__ == "__main__":
    main()