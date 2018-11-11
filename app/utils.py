import json
from flask import current_app


def get_all_tasks():
    with current_app.open_resource('static/kb/restaurant.json') as f:
        contents = f.read().decode('utf-8')
        tasks = json.loads(contents)
    return tasks


def get_priority(task_body):
    return len(task_body['log'])
