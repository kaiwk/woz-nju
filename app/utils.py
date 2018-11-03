import json
from flask import current_app


def get_tasks():
    with current_app.open_resource('static/kb/restaurant.json') as f:
        contents = f.read().decode('utf-8')
        tasks = json.loads(contents)
    return tasks
