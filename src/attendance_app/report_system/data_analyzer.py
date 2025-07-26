from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd

from attendance_app.path_manager import get_asset_path, get_output_dir, get_base_dir

ATTENDANCE_HISTORY_FILE = get_output_dir() / "attendance_history.csv"
STUDENT_DATA_FILE = get_base_dir() / "src" / "attendance_app" / "assets" / "sample_data.csv"

def get_student_name_mapping() -> Dict[str, str]:
    """塾生番号から名前へのマッピングを取得"""
    if not STUDENT_DATA_FILE.exists():
        return {}
    df = pd.read_csv(STUDENT_DATA_FILE, dtype=str, encoding='utf-8')
    return pd.Series(df.StudentName.values, index=df.StudentID).to_dict()

def get_monthly_attendance_data(student_id: str, year: int, month: int) -> dict:
    """
    指定生徒の月次出席データを取得・分析
    """
    if not ATTENDANCE_HISTORY_FILE.exists():
        return {}

    name_mapping = get_student_name_mapping()
    student_name = name_mapping.get(student_id, "Unknown")

    try:
        df = pd.read_csv(ATTENDANCE_HISTORY_FILE, dtype=str, encoding='utf-8-sig')
        # 複数の日付フォーマットに対応してパース
        def parse_datetime_flexible(dt_str):
            if pd.isna(dt_str) or dt_str == '':
                return pd.NaT
            # 複数のフォーマットを試行
            formats = [
                '%Y/%m/%d %H:%M',
                '%Y/%m/%d %H:%M:%S', 
                '%Y/%m/%d %H:%M:%S.%f',
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d %H:%M'
            ]
            for fmt in formats:
                try:
                    return pd.to_datetime(dt_str, format=fmt)
                except:
                    continue
            # フォーマットが合わない場合は汎用パーサーを使用
            return pd.to_datetime(dt_str, errors='coerce')
        
        df['Entry_Time'] = df['Entry_Time'].apply(parse_datetime_flexible)
        df['Exit_Time'] = df['Exit_Time'].apply(parse_datetime_flexible)
    except Exception as e:
        print(f"Error reading attendance history CSV: {e}")
        return {}
    # Entry_Timeと StudentIDが有効で、Exit_Timeも有効な行のみ取得（完了した出席記録）
    df = df.dropna(subset=['Entry_Time', 'StudentID'])
    df = df[df['Exit_Time'].notna()]

    # Filter for the specific student and month
    student_df = df[(df['StudentID'] == student_id) & 
                    (df['Entry_Time'].dt.year == year) & 
                    (df['Entry_Time'].dt.month == month)].copy()

    if student_df.empty:
        return {"student_name": student_name, "attendance_count": 0, "daily_records": []}

    student_df['StayMinutes'] = (student_df['Exit_Time'] - student_df['Entry_Time']).dt.total_seconds() / 60

    daily_records = []
    for _, row in student_df.iterrows():
        daily_records.append({
            "date": row['Entry_Time'].strftime("%Y-%m-%d"),
            "entry_time": row['Entry_Time'].strftime("%H:%M"),
            "exit_time": row['Exit_Time'].strftime("%H:%M"),
            "stay_minutes": round(row['StayMinutes']),
            "mood": row.get('Mood', ''),
            "sleep_satisfaction": row.get('Sleep_Satisfaction', ''),
            "purpose": row.get('Purpose', '')
        })

    # Dummy data for distributions as they are not fully implemented in the new CSV structure
    mood_count = {"快晴": 0, "晴れ": 0, "くもり": 0}
    sleep_count = {"０％": 0, "２５％": 0, "５０％": 0, "７５％": 0, "１００％": 0}
    purpose_count = {"学ぶ": 0, "来る": 0}

    return {
        "student_name": student_name,
        "attendance_count": len(daily_records),
        "average_stay_minutes": round(student_df['StayMinutes'].mean(), 1),
        "daily_records": daily_records,
        "mood_distribution": mood_count,
        "sleep_stats": {"average_percentage": 0, "distribution": sleep_count},
        "purpose_distribution": purpose_count
    }

def get_all_students_list() -> List[dict]:
    """登録されている全生徒のリストを取得"""
    name_mapping = get_student_name_mapping()
    return [{"id": student_id, "name": name} for student_id, name in name_mapping.items()]

def get_students_with_attendance(year: int, month: int) -> List[dict]:
    """指定月に出席記録がある生徒のリストを取得"""
    if not ATTENDANCE_HISTORY_FILE.exists():
        return []

    try:
        df = pd.read_csv(ATTENDANCE_HISTORY_FILE, dtype=str, encoding='utf-8-sig')
        # 同じ日付パース関数を使用
        def parse_datetime_flexible(dt_str):
            if pd.isna(dt_str) or dt_str == '':
                return pd.NaT
            formats = [
                '%Y/%m/%d %H:%M',
                '%Y/%m/%d %H:%M:%S', 
                '%Y/%m/%d %H:%M:%S.%f',
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d %H:%M'
            ]
            for fmt in formats:
                try:
                    return pd.to_datetime(dt_str, format=fmt)
                except:
                    continue
            return pd.to_datetime(dt_str, errors='coerce')
        
        df['Entry_Time'] = df['Entry_Time'].apply(parse_datetime_flexible)
        df['Exit_Time'] = df['Exit_Time'].apply(parse_datetime_flexible)
    except Exception as e:
        print(f"Error reading attendance history CSV for student list: {e}")
        return []
    # 完了した出席記録のみ取得
    df = df.dropna(subset=['Entry_Time', 'StudentID'])
    df = df[df['Exit_Time'].notna()]

    monthly_df = df[(df['Entry_Time'].dt.year == year) & (df['Entry_Time'].dt.month == month)]
    students_with_attendance = monthly_df['StudentID'].unique()

    name_mapping = get_student_name_mapping()
    result = []
    for student_id in students_with_attendance:
        if student_id in name_mapping:
            result.append({"id": student_id, "name": name_mapping[student_id]})
    
    return result
