import json
from datetime import datetime
from pathlib import Path

HISTORY_FILE = Path("print_history.json")


def _load_history():
    if HISTORY_FILE.exists():
        try:
            with HISTORY_FILE.open('r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return []


def add_record(student_id: str, student_name: str, result: str, error: str | None = None):
    history = _load_history()
    history.append({
        'timestamp': datetime.now().isoformat(),
        'studentId': student_id,
        'studentName': student_name,
        'result': result,
        'error': error or ''
    })
    with HISTORY_FILE.open('w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)