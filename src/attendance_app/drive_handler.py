

import io
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# Kivyアプリ内の他モジュールから設定を読み込む
from attendance_app.config import load_settings
from attendance_app.path_manager import get_service_account_path, get_qr_code_dir

# スコープの定義 (読み取り専用)
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

def get_drive_service():
    """
    DEPRECATED: Google Drive機能は使用されていません。
    このアプリケーションはローカルファイルのみを使用します。
    """
    raise RuntimeError("Google Drive機能は無効化されています。このアプリケーションはローカルファイルのみを使用します。")

def get_qr_download_path():
    """設定ファイルからQRコードのローカル保存パスを取得し、フォルダを確実に作成する"""
    return get_qr_code_dir()


def list_qr_files_from_drive():
    """
    DEPRECATED: Google Drive機能は無効化されています。
    QRコードはローカルassetsフォルダから読み込まれます。
    """
    raise RuntimeError("Google Drive機能は無効化されています。QRコードはローカルassetsフォルダから読み込まれます。")

def download_file_from_drive(file_id, file_name):
    """
    DEPRECATED: Google Drive機能は無効化されています。
    ファイルはローカルassetsフォルダから読み込まれます。
    """
    raise RuntimeError("Google Drive機能は無効化されています。ファイルはローカルassetsフォルダから読み込まれます。")

