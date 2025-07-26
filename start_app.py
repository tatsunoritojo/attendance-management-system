#!/usr/bin/env python3
"""
Cross-platform startup script for Attendance Management System v3.4
Works on Windows, macOS, and Linux.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
import logging

# Configure logging with PyInstaller compatibility
def setup_safe_logging():
    """Setup logging that works in both development and PyInstaller environments"""
    try:
        # Ensure stdout/stderr exist
        if sys.stdout is None:
            sys.stdout = open(os.devnull, 'w')
        if sys.stderr is None:
            sys.stderr = open(os.devnull, 'w')
            
        # Configure basic logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            stream=sys.stdout
        )
    except Exception:
        # Fallback: disable logging if it fails
        logging.basicConfig(level=logging.CRITICAL)

setup_safe_logging()
logger = logging.getLogger(__name__)

def get_python_executable():
    """Get the appropriate Python executable."""
    # Try to use the current Python interpreter first
    return sys.executable

def check_requirements():
    """Check if all requirements are satisfied."""
    requirements_file = Path(__file__).parent / "requirements.txt"
    if not requirements_file.exists():
        print("Error: requirements.txt not found")
        return False
    
    try:
        import pkg_resources
        with open(requirements_file, 'r') as f:
            requirements = f.read().splitlines()
        
        # Filter out platform-specific requirements
        filtered_requirements = []
        for req in requirements:
            req = req.strip()
            if not req or req.startswith('#'):
                continue
            # Skip Windows-specific kivy dependencies on non-Windows platforms
            if platform.system() != 'Windows' and 'kivy_deps' in req:
                continue
            filtered_requirements.append(req)
        
        pkg_resources.require(filtered_requirements)
        return True
    except (ImportError, pkg_resources.DistributionNotFound, pkg_resources.VersionConflict) as e:
        print(f"Missing or incompatible requirement: {e}")
        return False

def install_requirements():
    """Install requirements if needed."""
    python_exe = get_python_executable()
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    print("Installing/updating dependencies...")
    try:
        subprocess.run([
            python_exe, "-m", "pip", "install", "-r", str(requirements_file)
        ], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install requirements: {e}")
        return False

def setup_environment():
    """Setup environment variables and configuration."""
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Check for .env file
    env_file = script_dir / ".env"
    env_template = script_dir / ".env.template"
    
    if not env_file.exists() and env_template.exists():
        print("Creating .env file from template...")
        try:
            env_file.write_text(env_template.read_text(encoding='utf-8'), encoding='utf-8')
            print("Please edit .env file with your configuration.")
            input("Press Enter after configuring .env file...")
        except Exception as e:
            print(f"Warning: Could not create .env file: {e}")
    
    # Load environment variables from .env file
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            print("Loaded environment variables from .env")
        except ImportError:
            print("Warning: python-dotenv not installed, .env file will be ignored")

def check_configuration():
    """Configuration check is disabled for standalone version."""
    return True

def main():
    """Main startup function."""
    print("=" * 60)
    print("Attendance Management System v3.4")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    print("=" * 60)
    
    # Setup environment
    setup_environment()
    
    # Check and install requirements
    if not check_requirements():
        print("Installing missing requirements...")
        if not install_requirements():
            print("Failed to install requirements. Please install manually:")
            print("  pip install -r requirements.txt")
            sys.exit(1)
    
    # Check configuration
    if not check_configuration():
        print("Please fix configuration issues before starting.")
        sys.exit(1)
    
    # Start the application
    print("Starting application...")
    python_exe = get_python_executable()
    
    try:
        # Use subprocess to properly handle cross-platform execution
        result = subprocess.run([
            python_exe, "-m", "src.attendance_app"
        ], cwd=Path(__file__).parent)
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()