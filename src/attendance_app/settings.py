"""
Settings management for Attendance Management System v3.4
Handles environment variables, configuration files, and cross-platform settings.
"""

import os
import platform
from pathlib import Path
from typing import Optional, List, Dict, Any
from pydantic import Field, validator
from pydantic_settings import BaseSettings
import json
import logging

logger = logging.getLogger(__name__)

class AppSettings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Local Storage Paths
    qr_code_folder: str = Field("assets/images/塾生QRコード", env="QR_CODE_FOLDER")
    output_directory: str = Field("output/reports", env="OUTPUT_DIRECTORY")
    
    # Printer Configuration
    printer_executable: Optional[str] = Field(None, env="PRINTER_EXECUTABLE")
    
    # Application Settings
    log_level: str = Field("INFO", env="LOG_LEVEL")
    debug_mode: bool = Field(False, env="DEBUG_MODE")
    
    # Database Configuration
    database_url: str = Field("sqlite:///attendance.db", env="DATABASE_URL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @validator('log_level')
    def validate_log_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'log_level must be one of {valid_levels}')
        return v.upper()

class PlatformConfig:
    """Platform-specific configuration and paths."""
    
    PRINTER_PATHS = {
        'Windows': [
            r"C:\Program Files (x86)\Brother\Ptedit54\ptedit54.exe",
            r"C:\Program Files\Brother\Ptedit54\ptedit54.exe",
            r"C:\Program Files (x86)\Brother\P-touch Editor 5.4\ptedit54.exe",
            r"C:\Program Files\Brother\P-touch Editor 5.4\ptedit54.exe",
            r"C:\Program Files (x86)\Brother\P-touch Editor\ptedit54.exe",
            r"C:\Program Files\Brother\P-touch Editor\ptedit54.exe",
        ],
        'Darwin': [  # macOS
            "/Applications/Brother P-touch Editor.app/Contents/MacOS/P-touch Editor",
            "/Applications/P-touch Editor.app/Contents/MacOS/P-touch Editor",
        ],
        'Linux': [
            "/usr/bin/ptouch-editor",
            "/usr/local/bin/ptouch-editor",
            "/opt/brother/ptouch/ptedit",
        ]
    }
    
    FONT_PATHS = {
        'Windows': [
            "C:/Windows/Fonts/msgothic.ttc",  # MS Gothic
            "C:/Windows/Fonts/meiryo.ttc",    # Meiryo
        ],
        'Darwin': [  # macOS
            "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
            "/Library/Fonts/ヒラギノ角ゴ ProN W3.ttc",
        ],
        'Linux': [
            "/usr/share/fonts/truetype/takao-gothic/TakaoPGothic.ttf",
            "/usr/share/fonts/opentype/noto/NotoCJK-Regular.ttc",
        ]
    }
    
    @classmethod
    def get_platform(cls) -> str:
        """Get current platform name."""
        return platform.system()
    
    @classmethod
    def get_printer_paths(cls) -> List[str]:
        """Get platform-specific printer executable paths."""
        return cls.PRINTER_PATHS.get(cls.get_platform(), [])
    
    @classmethod
    def find_printer_executable(cls, custom_path: Optional[str] = None) -> Optional[str]:
        """Find available printer executable."""
        if custom_path and Path(custom_path).exists():
            return custom_path
            
        for path in cls.get_printer_paths():
            if Path(path).exists():
                logger.info(f"Found printer executable: {path}")
                return path
        
        logger.warning("No printer executable found")
        return None
    
    @classmethod
    def get_font_paths(cls) -> List[str]:
        """Get platform-specific font paths."""
        return cls.FONT_PATHS.get(cls.get_platform(), [])
    
    @classmethod
    def find_japanese_font(cls, custom_font: Optional[str] = None) -> Optional[str]:
        """Find available Japanese font."""
        if custom_font and Path(custom_font).exists():
            return custom_font
            
        for font_path in cls.get_font_paths():
            if Path(font_path).exists():
                logger.info(f"Found Japanese font: {font_path}")
                return font_path
        
        logger.warning("No Japanese font found")
        return None

class SettingsManager:
    """Centralized settings management."""
    
    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or self._get_base_dir()
        self.settings = AppSettings()
        self.platform_config = PlatformConfig()
        self._legacy_settings = None
        
        # Load legacy settings if they exist
        self._load_legacy_settings()
        
        # Setup logging
        self._setup_logging()
    
    def _get_base_dir(self) -> Path:
        """Get application base directory."""
        import sys
        if getattr(sys, 'frozen', False):
            # PyInstaller executable
            return Path(sys.executable).parent
        else:
            # Development environment
            return Path(__file__).resolve().parents[2]
    
    def _load_legacy_settings(self):
        """Load settings from legacy settings.json for backward compatibility."""
        legacy_path = self.base_dir / "settings.json"
        if legacy_path.exists():
            try:
                with open(legacy_path, 'r', encoding='utf-8') as f:
                    self._legacy_settings = json.load(f)
                logger.info("Loaded legacy settings.json")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to load legacy settings.json: {e}")
    
    def _setup_logging(self):
        """Setup application logging."""
        logging.basicConfig(
            level=getattr(logging, self.settings.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(self.base_dir / 'attendance.log', encoding='utf-8')
            ]
        )
    
    def get_absolute_path(self, relative_path: str) -> Path:
        """Convert relative path to absolute path based on base directory."""
        path = Path(relative_path)
        if path.is_absolute():
            return path
        return self.base_dir / relative_path
    
    def get_printer_executable(self) -> Optional[str]:
        """Get printer executable path."""
        custom_path = self.settings.printer_executable
        if self._legacy_settings and not custom_path:
            custom_path = self._legacy_settings.get('ptouch_editor_path')
        return self.platform_config.find_printer_executable(custom_path)
    
    def get_output_directory(self) -> Path:
        """Get output directory path."""
        path = self.get_absolute_path(self.settings.output_directory)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def get_qr_code_directory(self) -> Path:
        """Get QR code directory path."""
        folder = self.settings.qr_code_folder
        if self._legacy_settings and not self.settings.qr_code_folder:
            folder = self._legacy_settings.get('qr_code_folder', folder)
        
        path = self.get_absolute_path(folder)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def get_asset_path(self, relative_path: str) -> Path:
        """Get asset file path."""
        return self.get_absolute_path(f"assets/{relative_path}")
    
    def get_font_path(self, font_name: str) -> Path:
        """Get font file path."""
        return self.get_asset_path(f"fonts/{font_name}")
    
    def get_image_path(self, image_name: str) -> Path:
        """Get image file path."""
        return self.get_asset_path(f"images/{image_name}")
    
    def find_available_font(self) -> Optional[str]:
        """Find available Japanese font."""
        # Try custom font first
        custom_font_path = self.get_font_path("UDDigiKyokashoN-R.ttc")
        if custom_font_path.exists():
            return str(custom_font_path)
        
        # Try system fonts
        return self.platform_config.find_japanese_font()
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate current configuration and return status."""
        status = {
            'printer_executable': False,
            'japanese_font': False,
            'directories': True
        }
        
        # Check printer executable
        status['printer_executable'] = bool(self.get_printer_executable())
        
        # Check Japanese font
        status['japanese_font'] = bool(self.find_available_font())
        
        return status
    
    def create_example_env_file(self):
        """Create example .env file with current settings."""
        env_path = self.base_dir / ".env.example"
        content = f"""# Attendance Management System v3.4 Environment Configuration
# Copy this file to .env and configure your settings

# Local Storage Paths
QR_CODE_FOLDER={self.settings.qr_code_folder}
OUTPUT_DIRECTORY={self.settings.output_directory}

# Printer Configuration (leave empty for auto-detection)
PRINTER_EXECUTABLE={self.settings.printer_executable or ''}

# Application Settings
LOG_LEVEL={self.settings.log_level}
DEBUG_MODE={str(self.settings.debug_mode).lower()}

# Database Configuration (for offline support)
DATABASE_URL={self.settings.database_url}
"""
        env_path.write_text(content, encoding='utf-8')
        logger.info(f"Created example environment file: {env_path}")

# Global settings instance
settings_manager = SettingsManager()