#!/usr/bin/env python3
"""
VAL Scoreboard Tracker Web Application Launcher
"""

import os
import sys
import webbrowser
import time
from threading import Timer

def open_browser():
    """Open the web browser to the application URL after a short delay"""
    webbrowser.open('http://localhost:5000')

def main():
    """Main function to start the web application"""
    print("=" * 60)
    print("VAL Scoreboard Tracker - Web Application")
    print("=" * 60)
    print()
    
    # Check if we're in the correct directory
    if not os.path.exists('app.py'):
        print("Error: app.py not found in current directory.")
        print("Please run this script from the VALScoreboardTracker directory.")
        input("Press Enter to exit...")
        return
    
    # Check for required dependencies
    try:
        import flask
        import cv2
        import pytesseract
        print("✓ All required dependencies found")
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("\nPlease install required packages:")
        print("pip install -r requirements.txt")
        input("Press Enter to exit...")
        return
    
    # Import and run the Flask app
    try:
        from app import app, setup_tesseract
        
        print("✓ Initializing Tesseract OCR...")
        if not setup_tesseract():
            print("⚠ Warning: Tesseract OCR setup failed. Some features may not work.")
        else:
            print("✓ Tesseract OCR initialized successfully")
        
        print("\nStarting web server...")
        print("📱 Web interface will be available at: http://localhost:5000")
        print("🌐 Opening browser automatically in 2 seconds...")
        print("\nPress Ctrl+C to stop the server")
        print("-" * 60)
        
        # Open browser after 2 seconds
        Timer(2.0, open_browser).start()
        
        # Start the Flask development server
        app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        input("Press Enter to exit...")

if __name__ == '__main__':
    main()