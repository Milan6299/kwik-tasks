from datetime import date
import sqlite3


def create_task_event(
    cx: sqlite3.Connection,
    task_id: int,
    action: str,
    occurrence_date: str | None = None,
) -> int:
    if action not in {"completed", "skipped"}:
        raise ValueError("Action must be 'completed' or 'skipped'")

    occurrence_date = occurrence_date or date.today().isoformat()
    date.fromisoformat(occurrence_date)

    cur = cx.execute(
        """
        INSERT INTO task_events (task_id, action, occurrence_date)
        VALUES (?, ?, ?)
        """,
        (task_id, action, occurrence_date),
    )
    if cur.lastrowid is not None:
        return cur.lastrowid
    raise ValueError("Unable to create task event!")


def get_task_event(cx: sqlite3.Connection, event_id: int):
    return cx.execute(
        "SELECT * FROM task_events WHERE id = ?",
        (event_id,),
    ).fetchone()


def list_task_events(cx: sqlite3.Connection, task_id: int | None = None):
    if task_id is not None:
        return cx.execute(
            """
            SELECT * FROM task_events
            WHERE task_id = ?
            ORDER BY occurrence_date DESC, recorded_at DESC
            """,
            (task_id,),
        ).fetchall()
    
    return cx.execute(
        """
        SELECT * FROM task_events
        ORDER BY occurrence_date DESC, recorded_at DESC
        """
    ).fetchall()


def update_task_event(cx: sqlite3.Connection, event_id: int, **fields) -> bool:
    allowed = {"action", "occurrence_date"}

    if not fields or not fields.keys() <= allowed:
        raise ValueError("Invalid or empty task event fields")

    if "action" in fields:
        if fields["action"] not in {"completed", "skipped"}:
            raise ValueError("Action must be 'completed' or 'skipped'")

    if "occurrence_date" in fields:
        date.fromisoformat(fields["occurrence_date"])

    assignments = ", ".join(f"{key} = ?" for key in fields)
    values = list(fields.values()) + [event_id]

    cur = cx.execute(
        f"""
        UPDATE task_events
        SET {assignments}
        WHERE id = ?
        """,
        values,
    )
    return cur.rowcount > 0


def delete_task_event(cx: sqlite3.Connection, event_id: int) -> bool:
    cur = cx.execute(
        "DELETE FROM task_events WHERE id = ?",
        (event_id,),
    )
    return cur.rowcount > 0
