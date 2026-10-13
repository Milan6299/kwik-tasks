import sys

from kwik_tasks.cli.display import display_tags, display_tasks
from kwik_tasks.tasks.tag import create_tag, get_tag, list_tags
from kwik_tasks.tasks.task import (
    create_task,
    create_task_with_tag,
    list_tasks,
    record_occurrence,
    update_task,
)


def handle_task_add(cx, args):
    if args.tag is not None:
        task = create_task_with_tag(
            cx,
            title=args.title,
            tag_name=args.tag,
            due_date=args.due,
        )
    else:
        task = create_task(
            cx,
            args.title,
            args.tag_id,
            due_date=args.due,
        )

    print("Created task:")
    print(f"[{task['id']}] {task['title']} - <{task['tag']}>")


def handle_task_list(cx, args):
    tasks = list_tasks(cx)
    if not tasks:
        print("No tasks found!")
        return
    display_tasks(tasks)


def handle_task_edit(cx, args):
    fields = {}

    if args.title is not None:
        fields["title"] = args.title

    if args.due is not None:
        fields["due_date"] = args.due

    if not fields:
        print("No fields provided to update", file=sys.stderr)
        return

    if update_task(cx, args.id, **fields):
        print(f"Updated task {args.id}")
    else:
        print(f"Failed to update task {args.id}", file=sys.stderr)


def handle_task_done(cx, args):
    if record_occurrence(cx, args.id, "completed"):
        print(f"Marked task {args.id} as done")
    else:
        print(f"Failed to mark task {args.id} as done", file=sys.stderr)


def handle_tag_add(cx, args):
    tag = create_tag(cx, args.name)
    if tag is None:
        print("Unable to fetch tag!", file=sys.stderr)
        return

    print("Created tag:")
    display_tags([tag])


def handle_tag_list(cx, args):
    tags = list_tags(cx)
    if not tags:
        print("No tags found!")
        return
    display_tags(tags)
