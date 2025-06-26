#!/usr/bin/env python3
"""
Run the Streamlit Travel Booking Assistant
"""

import subprocess
import sys
import os

def run_app(test_mode=False):
    """Run the Streamlit application."""
    try:
        # Change to the directory containing the app
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        print(f"🚀 Starting Travel Booking Assistant...")
        print(f"📁 Working directory: {os.getcwd()}")
        
        # Check if files exist
        app_file = "test_app.py" if test_mode else "app.py"
        if not os.path.exists(app_file):
            print(f"❌ Error: {app_file} not found in {os.getcwd()}")
            return
        
        print(f"✅ Found {app_file}")
        
        # Run streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", app_file,
            "--server.address", "localhost",
            "--server.port", "8501",
            "--theme.base", "light"
        ])
    except KeyboardInterrupt:
        print("\nApplication stopped by user")
    except Exception as e:
        print(f"Error running app: {e}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="Run test app")
    args = parser.parse_args()
    
    run_app(test_mode=args.test)