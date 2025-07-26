import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any


def sanitize_filename(filename: str) -> str:
    """
    ファイル名から無効な文字を除去してWindows互換にする
    """
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '')
    return filename.strip()


def get_current_month_year() -> tuple:
    """現在の年月を取得"""
    now = datetime.now()
    return now.year, now.month


def format_file_size(size_bytes: int) -> str:
    """ファイルサイズを人間が読みやすい形式に変換"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def get_report_file_info(file_path: str) -> Dict[str, Any]:
    """レポートファイルの情報を取得"""
    path = Path(file_path)
    
    if not path.exists():
        return None
    
    stat = path.stat()
    
    return {
        "name": path.name,
        "size": stat.st_size,
        "size_formatted": format_file_size(stat.st_size),
        "created": datetime.fromtimestamp(stat.st_ctime),
        "modified": datetime.fromtimestamp(stat.st_mtime),
        "full_path": str(path.absolute())
    }


def list_generated_reports(reports_dir: str = None) -> List[Dict[str, Any]]:
    """生成されたレポートファイルのリストを取得"""
    if reports_dir is None:
        from attendance_app.path_manager import get_output_dir
        reports_dir = get_output_dir()
    else:
        reports_dir = Path(reports_dir)
    
    if not reports_dir.exists():
        return []
    
    reports = []
    # PDFとExcelファイルの両方を取得
    for pattern in ["*.pdf", "*.xlsx"]:
        for file_path in reports_dir.glob(pattern):
            info = get_report_file_info(str(file_path))
            if info:
                reports.append(info)
    
    # 作成日時でソート（新しい順）
    reports.sort(key=lambda x: x["created"], reverse=True)
    
    return reports


def cleanup_old_reports(days_to_keep: int = 30) -> int:
    """古いレポートファイルを削除"""
    from attendance_app.path_manager import get_output_dir
    reports_dir = get_output_dir()
    
    if not reports_dir.exists():
        return 0
    
    cutoff_date = datetime.now() - timedelta(days=days_to_keep)
    deleted_count = 0
    
    for pattern in ["*.pdf", "*.xlsx"]:
        for file_path in reports_dir.glob(pattern):
            stat = file_path.stat()
            if datetime.fromtimestamp(stat.st_mtime) < cutoff_date:
                try:
                    file_path.unlink()
                    deleted_count += 1
                    print(f"削除: {file_path.name}")
                except Exception as e:
                    print(f"削除失敗: {file_path.name} - {e}")
    
    return deleted_count


def validate_date_range(year: int, month: int) -> bool:
    """年月の妥当性をチェック"""
    if year < 2000 or year > 2100:
        return False
    if month < 1 or month > 12:
        return False
    return True


def get_month_name_japanese(month: int) -> str:
    """月の日本語名を取得"""
    month_names = {
        1: "1月", 2: "2月", 3: "3月", 4: "4月", 5: "5月", 6: "6月",
        7: "7月", 8: "8月", 9: "9月", 10: "10月", 11: "11月", 12: "12月"
    }
    return month_names.get(month, f"{month}月")


def create_progress_callback(total_items: int):
    """進捗表示用のコールバック関数を作成"""
    def progress_callback(current_item: int, description: str = ""):
        percentage = (current_item / total_items) * 100
        print(f"進捗: {current_item}/{total_items} ({percentage:.1f}%) {description}")
    
    return progress_callback


def log_report_generation(student_id: str, student_name: str, year: int, month: int, 
                         success: bool, error_message: str = None):
    """レポート生成のログを記録"""
    from attendance_app.path_manager import get_output_dir
    log_dir = get_output_dir().parent / "output"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / "report_generation.log"
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "SUCCESS" if success else "ERROR"
    
    log_entry = f"[{timestamp}] {status} - {student_name} ({student_id}) - {year}/{month:02d}"
    if error_message:
        log_entry += f" - {error_message}"
    
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
    except Exception as e:
        print(f"ログの書き込みに失敗しました: {e}")


def get_system_info() -> Dict[str, Any]:
    """システム情報を取得"""
    import platform
    import sys
    
    return {
        "platform": platform.platform(),
        "python_version": sys.version,
        "working_directory": os.getcwd(),
        "timestamp": datetime.now().isoformat()
    }


def print_system_info():
    """システム情報を表示"""
    info = get_system_info()
    print("=== システム情報 ===")
    for key, value in info.items():
        print(f"{key}: {value}")
    print("=" * 20)


if __name__ == "__main__":
    # ユーティリティ関数のテスト
    print("ユーティリティ関数のテストを開始します...")
    
    # システム情報の表示
    print_system_info()
    
    # 現在の年月を取得
    year, month = get_current_month_year()
    print(f"現在の年月: {year}年{get_month_name_japanese(month)}")
    
    # 生成されたレポートのリストを取得
    reports = list_generated_reports()
    print(f"生成されたレポート数: {len(reports)}")
    
    for report in reports[:3]:  # 最初の3件を表示
        print(f"- {report['name']} ({report['size_formatted']}) - {report['created']}")