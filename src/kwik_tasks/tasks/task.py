import sqlite3
from datetime import date, timedelta

from kwik_tasks.tasks.tag import create_tag, get_tag_id_by_name
from kwik_tasks.tasks.task_events import create_task_event


def create_task_with_tag(
    cx: sqlite3.Connection,
    title: str,
    tag_name: str,
    start_date: str | None = None,
    due_date: str | None = None,
    priority: int = 3,
    recurrence_days: int | None = None,
):
    title = title.strip()
    if not title:
        raise ValueError("Title cannot be empty")

    start_date = start_date or date.today().isoformat()
    date.fromisoformat(start_date)

    if due_date is not None:
        date.fromisoformat(due_date)
        if due_date < start_date:
            raise ValueError("Due date cannot be earlier than start date")

    if priority not in (1, 2, 3):
        raise ValueError("Priority must be 1, 2, or 3")

    if recurrence_days is not None and recurrence_days < 1:
        raise ValueError("Recurrence must be at least 1 day")

    tag_id = get_tag_id_by_name(cx, tag_name)
    if tag_id is None:
        tag_id = create_tag(cx, tag_name)

    cur = cx.execute(
        """
        INSERT INTO tasks
            (title, tag_id, start_date, due_date, priority, recurrence_days)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (title, tag_id, start_date, due_date, priority, recurrence_days),
    )
    if cur.lastrowid is not None:
        return get_task(cx, cur.lastrowid)
    raise ValueError("Unable to create task!")


def create_task(
    cx: sqlite3.Connection,
    title: str,
    tag_id: int,
    start_date: str | None = None,
    due_date: str | None = None,
    priority: int = 2,
    recurrence_days: int | None = None,
):
    title = title.strip()
    if not title:
        raise ValueError("Title cannot be empty")

    start_date = start_date or date.today().isoformat()
    date.fromisoformat(start_date)

    if due_date is not None:
        date.fromisoformat(due_date)
        if due_date < start_date:
            raise ValueError("Due date cannot be earlier than start date")

    if priority not in (1, 2, 3):
        raise ValueError("Priority must be 1, 2, or 3")

    if recurrence_days is not None and recurrence_days < 1:
        raise ValueError("Recurrence must be at least 1 day")

    cur = cx.execute(
        """
        INSERT INTO tasks
            (title, tag_id, start_date, due_date, priority, recurrence_days)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (title, tag_id, start_date, due_date, priority, recurrence_days),
    )

    if cur.lastrowid is not None:
        return get_task(cx, cur.lastrowid)
    raise ValueError("Unable to create task!")


def get_task(cx: sqlite3.Connection, task_id: int):
    return cx.execute(
        """
        SELECT tasks.*, tags.name AS tag
        FROM tasks
        JOIN tags ON tags.id = tasks.tag_id
        WHERE tasks.id = ?
        """,
        (task_id,),
    ).fetchone()


def list_tasks(cx: sqlite3.Connection, include_deleted: bool = False):
    condition = (
        "" if include_deleted else "WHERE tasks.active = 1 AND tasks.deleted_at IS NULL"
    )

    return cx.execute(
        f"""
        SELECT tasks.*, tags.name AS tag
        FROM tasks
        JOIN tags ON tags.id = tasks.tag_id
        {condition}
        ORDER BY
            CASE WHEN recurrence_days IS NOT NULL THEN 0 ELSE 1 END,
            start_date ASC,
            priority ASC,
            tasks.id ASC
        """
    ).fetchall()


def update_task(cx: sqlite3.Connection, task_id: int, **fields) -> bool:
    allowed = {
        "title",
        "tag_id",
        "start_date",
        "due_date",
        "priority",
        "recurrence_days",
    }

    if not fields or not fields.keys() <= allowed:
        raise ValueError("Invalid or empty task fields")

    if "title" in fields:
        fields["title"] = fields["title"].strip()
        if not fields["title"]:
            raise ValueError("Title cannot be empty")

    if "start_date" in fields:
        date.fromisoformat(fields["start_date"])

    if "due_date" in fields and fields["due_date"] is not None:
        date.fromisoformat(fields["due_date"])

    # Fetch current values to check constraints if dates are being modified independently
    if "start_date" in fields or "due_date" in fields:
        current = get_task(cx, task_id)
        if current:
            s_date = fields.get("start_date", current["start_date"])
            d_date = fields.get("due_date", current["due_date"])
            if d_date is not None and d_date < s_date:
                raise ValueError("Due date cannot be earlier than start date")

    if "priority" in fields and fields["priority"] not in (1, 2, 3):
        raise ValueError("Priority must be 1, 2, or 3")

    if "recurrence_days" in fields:
        value = fields["recurrence_days"]
        if value is not None and value < 1:
            raise ValueError("Recurrence must be at least 1 day")

    assignments = ", ".join(f"{key} = ?" for key in fields)
    values = list(fields.values()) + [task_id]

    cur = cx.execute(
        f"""
        UPDATE tasks
        SET {assignments}
        WHERE id = ? AND deleted_at IS NULL
        """,
        values,
    )
    return cur.rowcount > 0


def delete_task(cx: sqlite3.Connection, task_id: int) -> bool:
    """Soft-delete a task."""
    cur = cx.execute(
        """
        UPDATE tasks
        SET active = 0, deleted_at = CURRENT_TIMESTAMP
        WHERE id = ? AND deleted_at IS NULL
        """,
        (task_id,),
    )
    return cur.rowcount > 0


def restore_task(cx: sqlite3.Connection, task_id: int) -> bool:
    cur = cx.execute(
        """
        UPDATE tasks
        SET active = 1, deleted_at = NULL
        WHERE id = ? AND deleted_at IS NOT NULL
        """,
        (task_id,),
    )
    return cur.rowcount > 0


def record_occurrence(cx: sqlite3.Connection, task_id: int, action: str) -> bool:
    """Complete or skip an occurrence and advance recurring tasks."""
    if action not in {"completed", "skipped"}:
        raise ValueError("Action must be 'completed' or 'skipped'")

    task = cx.execute(
        """
        SELECT start_date, recurrence_days
        FROM tasks
        WHERE id = ? AND active = 1 AND deleted_at IS NULL
        """,
        (task_id,),
    ).fetchone()

    if task is None:
        return False

    occurrence_date = task["start_date"]

    try:
        create_task_event(
            cx, task_id=task_id, action=action, occurrence_date=occurrence_date
        )
    except Exception as e:
        print(e)
        raise ValueError("Unable to create task event!")

    if task["recurrence_days"] is None:
        cx.execute(
            "UPDATE tasks SET active = 0 WHERE id = ?",
            (task_id,),
        )
    else:
        next_start = (
            date.fromisoformat(occurrence_date)
            + timedelta(days=task["recurrence_days"])
        ).isoformat()

        cx.execute(
            "UPDATE tasks SET start_date = ? WHERE id = ?",
            (next_start, task_id),
        )

    return True
