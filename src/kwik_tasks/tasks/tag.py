import sqlite3


def normalize_tag(name: str) -> str:
    name = name.strip().lower()
    if not name:
        raise ValueError("Tag name cannot be empty")
    return name


def create_tag(cx: sqlite3.Connection, name: str):
    name = normalize_tag(name)

    cur = cx.execute(
        "INSERT INTO tags (name) VALUES (?)",
        (name,),
    )

    if cur.lastrowid is None:
        raise ValueError("Unable to create tag!")
    return get_tag(cx, cur.lastrowid)


def get_tag(cx: sqlite3.Connection, tag_id: int):
    row = cx.execute(
        "SELECT * FROM tags WHERE id = ?",
        (tag_id,),
    ).fetchone()
    return row if row is not None else None


def get_tag_id_by_name(cx: sqlite3.Connection, tag_name: str):
    row = cx.execute(
        "SELECT * FROM tags WHERE name = ?",
        (tag_name,),
    ).fetchone()
    return row["id"] if row is not None else None


def get_or_create_tag(cx: sqlite3.Connection, name: str) -> int:
    name = normalize_tag(name)

    cx.execute(
        """INSERT INTO tags (name) VALUES (?)
            ON CONFLICT(name) DO NOTHING""",
        (name,),
    )
    row = cx.execute(
        "SELECT id FROM tags WHERE name = ?",
        (name,),
    ).fetchone()
    return row["id"]


def list_tags(cx: sqlite3.Connection):
    return cx.execute("SELECT * FROM tags ORDER BY id").fetchall()


def update_tag(cx: sqlite3.Connection, tag_id: int, name: str) -> bool:
    name = normalize_tag(name)

    cur = cx.execute(
        "UPDATE tags SET name = ? WHERE id = ?",
        (name, tag_id),
    )
    return cur.rowcount > 0


def delete_tag(cx: sqlite3.Connection, tag_id: int) -> bool:
    cur = cx.execute(
        "DELETE FROM tags WHERE id = ?",
        (tag_id,),
    )
    return cur.rowcount > 0
