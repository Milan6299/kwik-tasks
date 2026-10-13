import argparse
import sqlite3
import sys

from kwik_tasks.cli.handlers import (
    handle_tag_add,
    handle_tag_list,
    handle_task_add,
    handle_task_done,
    handle_task_edit,
    handle_task_list,
)
from kwik_tasks.db.engine import get_connection

HANDLERS = {
    ("task", "add"): handle_task_add,
    ("task", "list"): handle_task_list,
    ("task", "edit"): handle_task_edit,
    ("task", "done"): handle_task_done,
    ("tag", "add"): handle_tag_add,
    ("tag", "list"): handle_tag_list,
}


def build_parser():
    parser = argparse.ArgumentParser(description="Kwik Tasks CLI")
    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    # Task commands
    task_parser = subparsers.add_parser(
        "task",
        help="Task operations",
    )
    task_sub = task_parser.add_subparsers(
        dest="subcommand",
        required=True,
    )

    # Create task
    add = task_sub.add_parser("add")
    add.add_argument("title", type=str)

    tag_group = add.add_mutually_exclusive_group(required=True)
    tag_group.add_argument("--tag-id", type=int)
    tag_group.add_argument("--tag", type=str)

    add.add_argument(
        "--due",
        type=str,
        help="ISO date (YYYY-MM-DD)",
    )

    # Edit task
    edit = task_sub.add_parser("edit")
    edit.add_argument("id", type=int)
    edit.add_argument("--title", type=str)
    edit.add_argument("--due", type=str)

    # List tasks
    task_sub.add_parser("list")

    # Mark task as done
    done = task_sub.add_parser("done")
    done.add_argument("id", type=int)

    # Tag commands
    tag_parser = subparsers.add_parser(
        "tag",
        help="Tag operations",
    )
    tag_sub = tag_parser.add_subparsers(
        dest="subcommand",
        required=True,
    )

    add_tag = tag_sub.add_parser("add")
    add_tag.add_argument("name", type=str)

    tag_sub.add_parser("list")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    handler = HANDLERS[(args.command, args.subcommand)]

    try:
        with get_connection() as cx:
            handler(cx, args)

    except sqlite3.Error:
        print("Database operation failed.", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
