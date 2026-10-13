from tabulate import tabulate


def parse_priority(priority: int):
    # if priority not in (1, 2, 3):
    #     raise ValueError("Priority Value invalid!")
    #     return
    pmap = {1: "high", 2: "med", 3: "low"}
    return pmap.get(priority, "")


def display_tags(tags):
    rows = [[tag["id"], tag["name"]] for tag in tags]
    print(
        tabulate(
            rows,
            headers=["ID", "Tag"],
            tablefmt="simple_outline",
        )
    )


def display_tasks(tasks):
    rows = [
        [
            task["id"],
            task["title"],
            task["tag"],
            parse_priority(task["priority"]),
            task["due_date"] or "",
        ]
        for task in tasks
    ]

    print(
        tabulate(
            rows,
            headers=["ID", "Title", "Tag", "Priority", "Due Date"],
            tablefmt="simple_outline",
        )
    )
