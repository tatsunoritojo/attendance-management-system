"""
Font management module for Attendance Management System v3.4
Handles font registration and fallback logic independently from main.py
"""

import logging
from pathlib import Path
from kivy.core.text import LabelBase
from attendance_app.settings import settings_manager
from attendance_app.path_manager import get_font_path

logger = logging.getLogger(__name__)

def register_font() -> tuple[bool, str]:
    """
    クロスプラットフォーム対応のフォント登録。
    Returns: (success, font_name)
    """
    # カスタムフォントを試行
    custom_font_path = get_font_path("UDDigiKyokashoN-R.ttc")
    if custom_font_path.exists():
        try:
            LabelBase.register(name="UDDigiKyokashoN-R", fn_regular=str(custom_font_path))
            logger.info(f"Custom font registered: {custom_font_path}")
            return True, "UDDigiKyokashoN-R"
        except Exception as e:
            logger.warning(f"Failed to register custom font: {e}")
    
    # システムフォントを試行
    system_font = settings_manager.find_available_font()
    if system_font:
        try:
            font_name = "SystemJapanese"
            LabelBase.register(name=font_name, fn_regular=system_font)
            logger.info(f"System font registered: {system_font}")
            return True, font_name
        except Exception as e:
            logger.warning(f"Failed to register system font: {e}")
    
    # フォールバック
    logger.warning("No Japanese font found, using default Roboto")
    return False, "Roboto"