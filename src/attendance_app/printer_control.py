"""
Printer control for Attendance Management System v3.4
Cross-platform printer support with improved error handling.
"""

import subprocess
from pathlib import Path
import os
import csv
import tempfile
import time
import platform
import logging
from typing import Optional
from attendance_app.settings import settings_manager
from attendance_app.path_manager import get_asset_path

logger = logging.getLogger(__name__)

class PrinterError(Exception):
    """Printer-related errors."""
    pass

class PrinterManager:
    """Cross-platform printer management."""
    
    def __init__(self):
        self.platform = platform.system()
        self.printer_path = settings_manager.get_printer_executable()
        self.label_template = get_asset_path('qr_text_template.lbx')
    
    def get_ptouch_editor_path(self) -> Optional[str]:
        """Get P-touch Editor path with cross-platform support."""
        return self.printer_path
    
    def validate_printer_setup(self) -> bool:
        """Validate printer setup and requirements."""
        if not self.printer_path:
            logger.error("No printer executable found")
            return False
        
        if not Path(self.printer_path).exists():
            logger.error(f"Printer executable not found: {self.printer_path}")
            return False
        
        if not self.label_template.exists():
            logger.error(f"Label template not found: {self.label_template}")
            return False
        
        return True
    
    def print_windows(self, student_id: str, student_name: str, csv_file: Path) -> None:
        """Print using Brother P-touch Editor on Windows."""
        cmd = [
            self.printer_path,
            str(self.label_template),
            f'/D:{csv_file}',
            '/R:1',
            '/FIT',
            '/S',
            '/P',
        ]
        
        logger.info(f"Windows print command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=30)
            logger.info("Windows printing completed successfully")
            logger.debug(f"Stdout: {result.stdout}")
        except subprocess.TimeoutExpired:
            raise PrinterError("Printer command timed out")
        except subprocess.CalledProcessError as e:
            logger.error(f"Windows printing failed: {e}")
            raise PrinterError(f"Printing failed: {e.stderr}")
    
    def print_macos(self, student_id: str, student_name: str, csv_file: Path) -> None:
        """Print using Brother P-touch Editor on macOS."""
        # macOS specific implementation
        cmd = [
            'open', '-a', self.printer_path,
            str(self.label_template)
        ]
        
        logger.info(f"macOS print command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=30)
            logger.info("macOS printing completed successfully")
        except subprocess.TimeoutExpired:
            raise PrinterError("Printer command timed out")
        except subprocess.CalledProcessError as e:
            logger.error(f"macOS printing failed: {e}")
            raise PrinterError(f"Printing failed: {e.stderr}")
    
    def print_linux(self, student_id: str, student_name: str, csv_file: Path) -> None:
        """Print using available printer on Linux."""
        # Linux implementation - could use CUPS or other printer systems
        if 'ptouch' in self.printer_path.lower():
            cmd = [self.printer_path, '--text', f'{student_name}\n{student_id}']
        else:
            # Fallback to generic printing
            cmd = ['lp', '-d', 'default', str(csv_file)]
        
        logger.info(f"Linux print command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=30)
            logger.info("Linux printing completed successfully")
        except subprocess.TimeoutExpired:
            raise PrinterError("Printer command timed out")
        except subprocess.CalledProcessError as e:
            logger.error(f"Linux printing failed: {e}")
            raise PrinterError(f"Printing failed: {e.stderr}")
    
    def print_label(self, student_id: str, student_name: str) -> None:
        """Print label with cross-platform support."""
        if not self.validate_printer_setup():
            raise PrinterError("Printer setup validation failed")
        
        # Prepare CSV data file
        csv_file = get_asset_path('sample_data.csv')
        
        if not csv_file.exists():
            raise PrinterError(f"CSV data file not found: {csv_file}")
        
        logger.info(f"Printing label for {student_name} (ID: {student_id})")
        logger.info(f"Platform: {self.platform}")
        logger.info(f"Printer: {self.printer_path}")
        logger.info(f"Template: {self.label_template}")
        logger.info(f"CSV file: {csv_file}")
        
        try:
            if self.platform == 'Windows':
                self.print_windows(student_id, student_name, csv_file)
            elif self.platform == 'Darwin':
                self.print_macos(student_id, student_name, csv_file)
            elif self.platform == 'Linux':
                self.print_linux(student_id, student_name, csv_file)
            else:
                raise PrinterError(f"Unsupported platform: {self.platform}")
        
        except Exception as e:
            logger.error(f"Printing failed: {e}")
            raise PrinterError(f"Printing failed: {e}")

# Global printer manager instance
printer_manager = PrinterManager()

# Legacy compatibility functions
def get_ptouch_editor_path():
    """Legacy function for compatibility."""
    return printer_manager.get_ptouch_editor_path()

LABEL_TEMPLATE = str(printer_manager.label_template)

def print_label(student_id: str, student_name: str) -> None:
    """
    Print QR code label using cross-platform printer support.
    Legacy compatibility function that delegates to PrinterManager.
    """
    printer_manager.print_label(student_id, student_name)