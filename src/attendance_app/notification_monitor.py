import json
from pathlib import Path
from typing import Callable

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from attendance_app.config import NOTIFICATION_DIR


class NotificationHandler(FileSystemEventHandler):
    def __init__(self, callback: Callable[[dict, Path], None]):
        super().__init__()
        self.callback = callback

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.json'):
            path = Path(event.src_path)
            try:
                data = json.loads(path.read_text(encoding='utf-8'))
                self.callback(data, path)
            except Exception as e:
                print(f'Failed to process notification {path}: {e}')


def start_monitor(callback: Callable[[dict, Path], None]) -> Observer:
    NOTIFICATION_DIR.mkdir(exist_ok=True)
    event_handler = NotificationHandler(callback)
    observer = Observer()
    observer.schedule(event_handler, str(NOTIFICATION_DIR), recursive=False)
    observer.start()
    return observer