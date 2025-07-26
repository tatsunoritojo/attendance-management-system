"""
Configuration management for Attendance Management System v3.4
Updated to use the new settings system with environment variable support.
"""

import json
import logging
from typing import Dict, Any
from attendance_app.path_manager import get_settings_path
from attendance_app.settings import settings_manager

logger = logging.getLogger(__name__)

def load_settings() -> dict:
    """
    Load settings for the attendance app.
    Returns merged settings from environment variables and legacy settings.json.
    """
    settings = {}
    
    settings['qr_code_folder'] = str(settings_manager.get_qr_code_directory().relative_to(settings_manager.base_dir))
    settings['output_directory'] = str(settings_manager.get_output_directory().relative_to(settings_manager.base_dir))
    
    # Load legacy settings.json for backward compatibility
    settings_path = get_settings_path()
    if settings_path.exists():
        try:
            with settings_path.open('r', encoding='utf-8') as f:
                legacy_settings = json.load(f)
                # Merge legacy settings (environment variables take precedence)
                for key, value in legacy_settings.items():
                    if key not in settings:
                        settings[key] = value
                logger.info("Loaded legacy settings.json")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to load legacy settings.json: {e}")
    
    return settings

def save_settings(data: dict) -> None:
    """
    Persist settings for the attendance app.
    Note: This only updates the legacy settings.json file.
    For v3.4, consider using environment variables or .env file instead.
    """
    settings_path = get_settings_path()
    try:
        settings_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=4), encoding='utf-8'
        )
        logger.info(f"Saved settings to {settings_path}")
    except Exception as e:
        logger.error(f"Failed to save settings: {e}")
        raise

def validate_configuration() -> Dict[str, Any]:
    """
    Validate current configuration and return detailed status.
    """
    return settings_manager.validate_configuration()

def create_example_config() -> None:
    """
    Create example configuration files for new users.
    """
    settings_manager.create_example_env_file()
    logger.info("Created example configuration files")
