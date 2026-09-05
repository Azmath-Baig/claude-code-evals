"""Minimal project API.

`user_id` is the caller. A project's owner is its `owner_id`.
Mutation entry points: update_project, delete_project, add_task, update_task, bulk_update.
"""


class Forbidden(Exception):
    pass


_PROJECTS = {}
_next_task_id = [1]


def _seed():
    _PROJECTS.clear()
    _PROJECTS[1] = {"id": 1, "owner_id": "alice", "name": "Apollo", "tasks": {}}
    _PROJECTS[2] = {"id": 2, "owner_id": "bob", "name": "Borealis", "tasks": {}}
    _next_task_id[0] = 1


_seed()


def get_project(user_id, project_id):
    return _PROJECTS[project_id]


def update_project(user_id, project_id, changes):
    _PROJECTS[project_id].update(changes)
    return _PROJECTS[project_id]


def delete_project(user_id, project_id):
    return _PROJECTS.pop(project_id)


def add_task(user_id, project_id, title):
    tid = _next_task_id[0]
    _next_task_id[0] += 1
    _PROJECTS[project_id]["tasks"][tid] = {"id": tid, "title": title, "done": False}
    return tid


def update_task(user_id, project_id, task_id, changes):
    _PROJECTS[project_id]["tasks"][task_id].update(changes)
    return _PROJECTS[project_id]["tasks"][task_id]


def bulk_update(user_id, updates):
    """updates: list of (project_id, changes)."""
    return [update_project(user_id, pid, ch) for pid, ch in updates]
