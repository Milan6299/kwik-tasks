import sqlite3
import sys

from kwik_tasks.db.engine import get_connection
from kwik_tasks.tasks.task import create_task_with_tag


def main() -> None:
    args = sys.argv[1:]

    title = args[0]
    tag = args[1]

    print("Hello from kwik-tasks!")

    print(title, "->", tag)
    with get_connection() as cx:
        try:
            result = create_task_with_tag(cx, title=title, tag_name=tag)
            print("Task added successfully!")
            print(dict(result))
        except sqlite3.IntegrityError as e:
            print(f"{tag} already exists!")
            print(e)
