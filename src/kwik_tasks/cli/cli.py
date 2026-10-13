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


def build_parser():
    parser = argparse.ArgumentParser(description="Kwik Tasks CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ## Task commands
    add = subparsers.add_parser("add", help="Create a task")
    add.add_argument("title", help="Task name or title")
    add.add_argument("tag", help="Tag name")
    add.add_argument("--due", type=str, help="Date YYYY-MM-DD")
    add.add_argument(
        "-r",
        "--repeat",
        type=int,
        help="Repeat task every N day e.g 1,7,30",
    )
    add.add_argument(
        "-p", "--priority", type=int, help="integer - 1, 2, 3 -> high, med, low"
    )
    add.set_defaults(handler=handle_task_add)

    edit = subparsers.add_parser("edit", help="Edit a task")
    edit.add_argument("id", type=int)
    edit.add_argument("--title")
    edit.add_argument("--due")
    edit.set_defaults(handler=handle_task_edit)

    task_list = subparsers.add_parser("list", help="List tasks")
    list_group = task_list.add_mutually_exclusive_group(required=False)
    list_group.add_argument(
        "-a", "--all", action="store_true", help="List active tasks only"
    )
    list_group.add_argument(
        "-i", "--inactive", action="store_true", help="List inactive tasks only"
    )
    task_list.set_defaults(handler=handle_task_list)

    done = subparsers.add_parser("done", help="Complete a task")
    done.add_argument("id", type=int)
    done.set_defaults(handler=handle_task_done)

    # Tag command group
    tag_parser = subparsers.add_parser("tag", help="Tag operations")
    tag_sub = tag_parser.add_subparsers(
        dest="tag_action",
        required=True,
    )

    tag_add = tag_sub.add_parser("add", help="Create a tag")
    tag_add_group = tag_add.add_mutually_exclusive_group(required=True)
    tag_add_group.add_argument("name", nargs="?", help="Tag name, e.g. work, personal")
    tag_add_group.add_argument("-n", "--name", dest="name_option", help="Tag name")
    tag_add.set_defaults(handler=handle_tag_add)

    tag_list = tag_sub.add_parser("list", help="List tags")
    tag_list.set_defaults(handler=handle_tag_list)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    try:
        with get_connection() as cx:
            args.handler(cx, args)

    except sqlite3.Error:
        print("Database operation failed.", file=sys.stderr)
        raise SystemExit(1)
