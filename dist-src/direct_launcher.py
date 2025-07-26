#!/usr/bin/env python3
"""
Direct launcher for PyInstaller - bypasses start_app.py checks
"""

import sys
import os
import logging
from pathlib import Path

# Fix logging for PyInstaller environment
def setup_logging():
    """Configure logging for PyInstaller environment"""
    try:
        # Redirect stdout/stderr if they're None (common in PyInstaller)
        if sys.stdout is None:
            sys.stdout = open(os.devnull, 'w')
        if sys.stderr is None:
            sys.stderr = open(os.devnull, 'w')
            
        # Configure logging to use file output instead of console
        log_file = Path(__file__).parent / 'app.log'
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(str(log_file), encoding='utf-8'),
                logging.StreamHandler(sys.stdout) if sys.stdout else logging.NullHandler()
            ]
        )
        logging.getLogger().info("Logging configured for PyInstaller environment")
    except Exception as e:
        # Fallback to basic logging if above fails
        logging.basicConfig(level=logging.WARNING)

# Setup logging before any other imports
setup_logging()

# Change to the correct directory
script_dir = Path(__file__).parent
os.chdir(script_dir)

# Add src to path for imports
sys.path.insert(0, str(script_dir / 'src'))

# Direct import and launch
from attendance_app.main import AttendanceApp

if __name__ == "__main__":
    try:
        logging.getLogger().info("Starting Attendance Management System")
        
        # Import test before running app
        logging.getLogger().info("Testing imports...")
        from attendance_app.config import load_settings
        from attendance_app.spreadsheet import get_student_name
        logging.getLogger().info("All imports successful")
        
        # Create app instance
        logging.getLogger().info("Creating app instance...")
        app = AttendanceApp()
        logging.getLogger().info("App instance created successfully")
        
        # Run app
        logging.getLogger().info("Starting app.run()...")
        app.run()
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logging.getLogger().error(f"Application error: {e}")
        logging.getLogger().error(f"Full traceback: {error_details}")
        
        # Show error in a basic way if GUI fails
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Application Error", 
                f"Application failed to start:\n\n{e}\n\nCheck app.log for details")
        except:
            print(f"CRITICAL ERROR: {e}")
            print(f"Full traceback:\n{error_details}")
            
        # Also write to a crash log file
        try:
            with open('crash.log', 'w') as f:
                f.write(f"Crash at: {Path(__file__).parent}\n")
                f.write(f"Error: {e}\n")
                f.write(f"Full traceback:\n{error_details}\n")
        except:
            pass
            
        sys.exit(1)