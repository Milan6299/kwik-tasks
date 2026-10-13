import sqlite3
from contextlib import contextmanager
from pathlib import Path

db_path = Path().cwd()


@contextmanager
def get_connection():
    cx = sqlite3.connect(db_path / "test.db")
    cx.row_factory = sqlite3.Row
    cx.execute("PRAGMA foreign_keys = ON")
    try:
        yield cx
        cx.commit()
    except Exception as e:
        cx.rollback()
        print("DB Error:")
        print(e)
        raise
    finally:
        cx.close()


with get_connection() as cx:
    cx.execute("PRAGMA foreign_keys = ON")

    cx.executescript("""
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
                CHECK(name = lower(name))
        );

        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            tag_id INTEGER NOT NULL REFERENCES tags(id),
            start_date TEXT NOT NULL DEFAULT (date('now')),
            due_date TEXT,
            priority INTEGER NOT NULL DEFAULT 3
                CHECK (priority BETWEEN 1 AND 3),
            recurrence_days INTEGER
                CHECK (recurrence_days IS NULL OR recurrence_days > 0),
            active INTEGER NOT NULL DEFAULT 1
                CHECK (active IN (0, 1)),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            deleted_at TEXT
        );

        CREATE TABLE IF NOT EXISTS task_events (
            id INTEGER PRIMARY KEY,
            task_id INTEGER NOT NULL REFERENCES tasks(id),
            action TEXT NOT NULL
                CHECK (action IN ('completed', 'skipped')),
            occurrence_date TEXT NOT NULL,
            recorded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (task_id, occurrence_date)
        );

        CREATE INDEX IF NOT EXISTS idx_tasks_due
            ON tasks(active, due_date);

        CREATE INDEX IF NOT EXISTS idx_events_task
            ON task_events(task_id, action);
    """)
