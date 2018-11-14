import json
from flask import current_app, session


def add_turn_count():
    if session.get('turn_count'):
        session['turn_count'] += 1
    else:
        session['turn_count'] = 1


def get_all_tasks():
    with current_app.open_resource('static/kb/restaurant.json') as f:
        contents = f.read().decode('utf-8')
        tasks = json.loads(contents)
    return tasks


def get_priority(task_body):
    return len(task_body['log'])


def get_all_valid_full_slots_tasks():
    """
    A valid task means there is corresponding data entries in database.
    """
    tasks = get_all_tasks()
    valid_tasks = []
    for t in tasks:
        inform = dict()
        if t['name']:
            inform['name'] = t['name']
        if t['tag']:
            inform['food_type'] = t['tag']
        if t['price_range']:
            inform['price_range'] = t['price_range']
        if t['area']:
            inform['area'] = t['area']

        request = []
        if t['address']:
            request.append('地址')
        if t['phone']:
            request.append('电话')
        if t['recommends']:
            request.append('推荐菜')

        valid_tasks.append({
            'goal': {
                'message': '',
                'restaurant': {
                    'request': request,
                    'inform': inform
                }
            },
        })

    return valid_tasks


def get_all_areas():
    v_tasks = get_all_valid_full_slots_tasks()
    areas = set()
    for t in v_tasks:
        rest = t['goal']['restaurant']
        area = rest['inform']['area']
        areas.add(area)
    return areas


def get_all_food_types():
    v_tasks = get_all_valid_full_slots_tasks()
    food_types = set()
    for t in v_tasks:
        rest = t['goal']['restaurant']
        food_type = rest['inform']['food_type']
        food_types.add(food_type)
    return food_types


def get_all_price_ranges():
    v_tasks = get_all_valid_full_slots_tasks()
    price_ranges = set()
    for t in v_tasks:
        rest = t['goal']['restaurant']
        price_range = rest['inform']['price_range']
        price_ranges.add(price_range)
    return price_ranges
