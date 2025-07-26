"""
Offline storage support for Attendance Management System v3.4
SQLite-based local storage for attendance records when online sync fails.
"""

import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from contextlib import contextmanager

from attendance_app.settings import settings_manager

logger = logging.getLogger(__name__)

class OfflineStorage:
    """SQLite-based offline storage for attendance records."""
    
    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            db_path = settings_manager.base_dir / "attendance_offline.db"
        
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the SQLite database with required tables."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Attendance records table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS attendance_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_id TEXT NOT NULL,
                        student_name TEXT NOT NULL,
                        entry_time TEXT NOT NULL,
                        exit_time TEXT,
                        responses TEXT,
                        synced BOOLEAN DEFAULT FALSE,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                ''')
                
                # Sync log table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS sync_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        action TEXT NOT NULL,
                        status TEXT NOT NULL,
                        message TEXT,
                        record_count INTEGER
                    )
                ''')
                
                conn.commit()
                logger.info(f"Offline database initialized: {self.db_path}")
                
        except Exception as e:
            logger.error(f"Failed to initialize offline database: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Get database connection with proper error handling."""
        conn = None
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row  # Enable dict-like row access
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def save_attendance_record(self, student_id: str, student_name: str, 
                             entry_time: str, responses: Dict[str, Any] = None) -> int:
        """Save an attendance record to offline storage."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                now = datetime.now().isoformat()
                responses_json = json.dumps(responses) if responses else None
                
                cursor.execute('''
                    INSERT INTO attendance_records 
                    (student_id, student_name, entry_time, responses, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (student_id, student_name, entry_time, responses_json, now, now))
                
                record_id = cursor.lastrowid
                conn.commit()
                
                logger.info(f"Saved offline attendance record: {record_id} for {student_name}")
                return record_id
                
        except Exception as e:
            logger.error(f"Failed to save offline attendance record: {e}")
            raise
    
    def update_exit_time(self, student_id: str, exit_time: str) -> bool:
        """Update exit time for the most recent unfinished record."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Find the most recent record without exit time for this student
                cursor.execute('''
                    SELECT id FROM attendance_records 
                    WHERE student_id = ? AND exit_time IS NULL 
                    ORDER BY entry_time DESC LIMIT 1
                ''', (student_id,))
                
                row = cursor.fetchone()
                if not row:
                    logger.warning(f"No unfinished record found for student {student_id}")
                    return False
                
                # Update the exit time
                now = datetime.now().isoformat()
                cursor.execute('''
                    UPDATE attendance_records 
                    SET exit_time = ?, updated_at = ?
                    WHERE id = ?
                ''', (exit_time, now, row['id']))
                
                conn.commit()
                logger.info(f"Updated exit time for offline record {row['id']}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to update exit time: {e}")
            return False
    
    def update_responses(self, student_id: str, responses: Dict[str, Any]) -> bool:
        """Update responses for the most recent record."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Find the most recent record for this student
                cursor.execute('''
                    SELECT id, responses FROM attendance_records 
                    WHERE student_id = ? 
                    ORDER BY entry_time DESC LIMIT 1
                ''', (student_id,))
                
                row = cursor.fetchone()
                if not row:
                    logger.warning(f"No record found for student {student_id}")
                    return False
                
                # Merge responses
                existing_responses = json.loads(row['responses']) if row['responses'] else {}
                existing_responses.update(responses)
                
                # Update the record
                now = datetime.now().isoformat()
                cursor.execute('''
                    UPDATE attendance_records 
                    SET responses = ?, updated_at = ?
                    WHERE id = ?
                ''', (json.dumps(existing_responses), now, row['id']))
                
                conn.commit()
                logger.info(f"Updated responses for offline record {row['id']}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to update responses: {e}")
            return False
    
    def get_unsynced_records(self) -> List[Dict[str, Any]]:
        """Get all unsynced records for cloud synchronization."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM attendance_records 
                    WHERE synced = FALSE 
                    ORDER BY entry_time ASC
                ''')
                
                records = []
                for row in cursor.fetchall():
                    record = dict(row)
                    if record['responses']:
                        record['responses'] = json.loads(record['responses'])
                    records.append(record)
                
                logger.info(f"Found {len(records)} unsynced records")
                return records
                
        except Exception as e:
            logger.error(f"Failed to get unsynced records: {e}")
            return []
    
    def mark_records_synced(self, record_ids: List[int]) -> bool:
        """Mark records as synced after successful cloud upload."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                placeholders = ','.join('?' * len(record_ids))
                cursor.execute(f'''
                    UPDATE attendance_records 
                    SET synced = TRUE, updated_at = ?
                    WHERE id IN ({placeholders})
                ''', [datetime.now().isoformat()] + record_ids)
                
                conn.commit()
                logger.info(f"Marked {len(record_ids)} records as synced")
                return True
                
        except Exception as e:
            logger.error(f"Failed to mark records as synced: {e}")
            return False
    
    def log_sync_attempt(self, action: str, status: str, message: str = None, record_count: int = 0):
        """Log synchronization attempts."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO sync_log (timestamp, action, status, message, record_count)
                    VALUES (?, ?, ?, ?, ?)
                ''', (datetime.now().isoformat(), action, status, message, record_count))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to log sync attempt: {e}")
    
    def get_recent_records(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent attendance records for display."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM attendance_records 
                    ORDER BY entry_time DESC 
                    LIMIT ?
                ''', (limit,))
                
                records = []
                for row in cursor.fetchall():
                    record = dict(row)
                    if record['responses']:
                        record['responses'] = json.loads(record['responses'])
                    records.append(record)
                
                return records
                
        except Exception as e:
            logger.error(f"Failed to get recent records: {e}")
            return []
    
    def cleanup_old_records(self, days: int = 30) -> int:
        """Clean up old synced records to save space."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cutoff_date = datetime.now().replace(day=datetime.now().day - days).isoformat()
                
                cursor.execute('''
                    DELETE FROM attendance_records 
                    WHERE synced = TRUE AND created_at < ?
                ''', (cutoff_date,))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                logger.info(f"Cleaned up {deleted_count} old records")
                return deleted_count
                
        except Exception as e:
            logger.error(f"Failed to cleanup old records: {e}")
            return 0

# Global offline storage instance
offline_storage = OfflineStorage()