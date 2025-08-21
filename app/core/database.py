import sqlite3
import json
from datetime import datetime
from typing import List, Optional
from app.models.example import CustomExample


class ExampleDatabase:
    def __init__(self, db_path: str = "examples.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize the database and create tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS custom_examples (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    rfc_version TEXT NOT NULL,
                    raw_message TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            conn.commit()
    
    def create_example(self, name: str, description: Optional[str], rfc_version: str, raw_message: str) -> CustomExample:
        """Create a new custom example"""
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO custom_examples (name, description, rfc_version, raw_message, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, description, rfc_version, raw_message, now, now))
            
            example_id = cursor.lastrowid
            conn.commit()
            
            return CustomExample(
                id=example_id,
                name=name,
                description=description,
                rfc_version=rfc_version,
                raw_message=raw_message,
                created_at=datetime.fromisoformat(now),
                updated_at=datetime.fromisoformat(now)
            )
    
    def get_examples(self, rfc_version: Optional[str] = None) -> List[CustomExample]:
        """Get all custom examples, optionally filtered by RFC version"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if rfc_version:
                cursor.execute("""
                    SELECT id, name, description, rfc_version, raw_message, created_at, updated_at
                    FROM custom_examples
                    WHERE rfc_version = ?
                    ORDER BY created_at DESC
                """, (rfc_version,))
            else:
                cursor.execute("""
                    SELECT id, name, description, rfc_version, raw_message, created_at, updated_at
                    FROM custom_examples
                    ORDER BY created_at DESC
                """)
            
            examples = []
            for row in cursor.fetchall():
                examples.append(CustomExample(
                    id=row[0],
                    name=row[1],
                    description=row[2],
                    rfc_version=row[3],
                    raw_message=row[4],
                    created_at=datetime.fromisoformat(row[5]),
                    updated_at=datetime.fromisoformat(row[6])
                ))
            
            return examples
    
    def get_example(self, example_id: int) -> Optional[CustomExample]:
        """Get a specific example by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, description, rfc_version, raw_message, created_at, updated_at
                FROM custom_examples
                WHERE id = ?
            """, (example_id,))
            
            row = cursor.fetchone()
            if row:
                return CustomExample(
                    id=row[0],
                    name=row[1],
                    description=row[2],
                    rfc_version=row[3],
                    raw_message=row[4],
                    created_at=datetime.fromisoformat(row[5]),
                    updated_at=datetime.fromisoformat(row[6])
                )
            return None
    
    def update_example(self, example_id: int, name: Optional[str] = None, 
                      description: Optional[str] = None, rfc_version: Optional[str] = None,
                      raw_message: Optional[str] = None) -> Optional[CustomExample]:
        """Update an existing example"""
        existing = self.get_example(example_id)
        if not existing:
            return None
        
        # Use existing values if not provided
        new_name = name if name is not None else existing.name
        new_description = description if description is not None else existing.description
        new_rfc_version = rfc_version if rfc_version is not None else existing.rfc_version
        new_raw_message = raw_message if raw_message is not None else existing.raw_message
        new_updated_at = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE custom_examples
                SET name = ?, description = ?, rfc_version = ?, raw_message = ?, updated_at = ?
                WHERE id = ?
            """, (new_name, new_description, new_rfc_version, new_raw_message, new_updated_at, example_id))
            conn.commit()
            
            return self.get_example(example_id)
    
    def delete_example(self, example_id: int) -> bool:
        """Delete an example by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM custom_examples WHERE id = ?", (example_id,))
            conn.commit()
            return cursor.rowcount > 0


# Global database instance
example_db = ExampleDatabase()