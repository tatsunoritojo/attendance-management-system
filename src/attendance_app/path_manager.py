
"""
Path manager for Attendance Management System v3.4
Updated to use the new settings system with cross-platform support.
"""

import sys
import os
from pathlib import Path
from attendance_app.settings import settings_manager

def get_base_dir() -> Path:
    """
    実行環境（スクリプト or .exe）に応じてベースディレクトリの絶対パスを返す
    """
    return settings_manager.base_dir

# --- ベースディレクトリ ---
BASE_DIR = get_base_dir()

# --- 設定ファイル ---
def get_settings_path() -> Path:
    """settings.jsonのパスを返す（レガシー互換性のため）"""
    return BASE_DIR / 'settings.json'

def get_service_account_path() -> Path:
    """
    DEPRECATED: サービスアカウント機能は使用されていません。
    下位互換性のためにダミーパスを返します。
    """
    return BASE_DIR / 'service_account.json'

# --- アセット ---
def get_asset_path(relative_path: str) -> Path:
    """
    assetsフォルダ内の指定されたリソースへの絶対パスを返す
    """
    return BASE_DIR / "assets" / relative_path

def get_font_path(font_name: str) -> Path:
    """フォントファイルへのパスを返す"""
    return settings_manager.get_font_path(font_name)

def get_image_path(image_name: str) -> Path:
    """画像ファイルへのパスを返す"""
    return settings_manager.get_image_path(image_name)

def get_sound_path(sound_name: str) -> Path:
    """音声ファイルへのパスを返す"""
    return BASE_DIR / "assets" / "sounds" / sound_name

def get_template_path(template_name: str) -> Path:
    """テンプレートファイルへのパスを返す"""
    return settings_manager.get_asset_path(template_name)

# --- 出力先 ---
def get_output_dir() -> Path:
    """
    レポートなどの出力先ディレクトリのパスを返す。
    """
    return settings_manager.get_output_directory()

def get_qr_code_dir() -> Path:
    """
    QRコードを保存するローカルディレクトリのパスを返す。
    """
    return settings_manager.get_qr_code_directory()
