import json
import random
import datetime

from flask import Blueprint, session, redirect, url_for, current_app, g, render_template
from sqlalchemy import not_

from .database import Task, db
from .utils import get_all_valid_full_slots_tasks

bp = Blueprint('main', __name__,
               static_folder='static',
               template_folder='templates')


@bp.before_request
def init_global():
    g.inform_slots = ['name', 'food_type', 'price_range', 'area']
    g.informs = {
        'food_type': ['冒菜', '黄焖鸡', '鸡蛋饼', '烧烤', '食堂', '砂锅', '面条', '炸鸡',
                      '臭豆腐', '螺蛳粉', '串串', '麻辣烫', '老鸭粉丝汤', '包子', '水饺',
                      '牛肉汤', '鱿鱼', '骨头饭', '铁板饭', '咖啡', '兰州拉面', '板栗', '汤包',
                      '烤冷面', '煎饼', '中餐', '锅盔', '米线', '馄饨', '灌饼', '蛋包饭', '手抓饼', '豆浆', '盐水鸭'],
        'price_range': ['昂贵', '中等', '便宜'],
        'area': ['陶谷新村', '青岛路', '北京西路', '双龙巷', '珠江路', '军区总院',
                 '小粉桥', '中山路', '湖南路', '汉口路', '天津路', '鼓楼街', '金银街']
    }
    g.slot_chinese = {
        'name': '餐厅名字',
        'food_type': '食物类型',
        'price_range': '价格',
        'area': '所在地区'
    }
    g.msg_inform_funcs = {
        'name': want_name,
        'food_type': want_food_type,
        'price_range': want_price_range,
        'area': want_area
    }


@bp.route('/select_task')
def select_task():

    reset_task_selected()

    task = db.session.query(Task).with_for_update()\
        .filter(not_(Task.selected) & not_(Task.finished))\
        .order_by(Task.priority.desc())\
        .first()

    if task is None:
        task = Task(body=get_task())
        db.session.add(task)

    task.selected = True
    db.session.commit()

    session['task_id'] = task.id
    session.permanent = True

    body = json.loads(task.body)
    log = body['log']

    if not log or ('metadata' in log[-1]):
        current_app.logger.info('Redirect to user index.')
        return redirect(url_for('user.index'))
    current_app.logger.info('Redirect to wizard index.')
    return redirect(url_for('wizard.index'))


def get_task():
    """
    Get task with json format
    :return: task json string
    :rtype: str
    """
    valid_chance = 0.35
    if random.uniform(0, 1) > valid_chance:
        task = get_valid_task()
    else:
        task = get_invalid_task()
    return json.dumps(task, ensure_ascii=False)


def extract_from_full(task):
    """
    Extract task from task object with full slot-values
    :param task: task with full slot-values
    :return: task
    :rtype: task
    """
    rest = task['goal']['restaurant']
    all_requests = rest['request']
    all_informs = rest['inform']

    # get slots
    key_list = list(all_informs.keys())
    inform_slots = [key_list[i] for i in sorted(random.sample(range(len(key_list)), 3))]
    if len(all_requests) > 1:
        request_slots = random.sample(all_requests, 2)
    else:
        request_slots = all_requests
    informs = {k: all_informs[k] for k in inform_slots}

    # get messages
    msg = _get_msg(all_informs, inform_slots, request_slots)

    return _get_task(informs, request_slots, msg)


def get_valid_task():
    """
    :return: task
    :rtype: dict
    """
    valid_tasks = get_all_valid_full_slots_tasks()
    task = random.choice(valid_tasks)
    return extract_from_full(task)


def get_invalid_task():
    """
    An invalid task means there is NOT corresponding data entries in database.
    :return: task
    :rtype: dict
    """
    valid_tasks = get_all_valid_full_slots_tasks()
    task = random.choice(valid_tasks)
    valid_tasks.remove(task)

    task = extract_from_full(task)

    info = task['goal']['restaurant']['inform']
    request_slots = task['goal']['restaurant']['request']

    # modify one of the slots, so that there isn't corresponding entry in database
    for no_match_slot in random.sample(['food_type', 'price_range', 'area'], 3):
        if no_match_slot in info:
            valid_value = info[no_match_slot]
            if not exist_match_task(info, no_match_slot, valid_value, valid_tasks):
                msg = _get_msg(info, info.keys(), request_slots)
                task['goal']['message'] = msg + f'，如果没有找到符合的餐厅，尝试把{g.slot_chinese[no_match_slot]}' \
                                                f'的值换成<b>{valid_value}</b>，用户会再次询问'
                return task
            # recover original value
            info[no_match_slot] = valid_value

    # if there isn't any invalid task, return the valid task
    return task


def exist_match_task(task_informs, no_match_slot, valid_value, valid_tasks):
    """
    This function will modify 'task_informs'
    :param task_informs:
    :param no_match_slot:
    :return:
    """
    random.shuffle(g.informs[no_match_slot])
    for v in g.informs[no_match_slot]:
        if v == valid_value:
            continue
        task_informs[no_match_slot] = v
        for t in valid_tasks:
            current_app.logger.debug(task_informs)
            current_app.logger.debug(t['goal']['restaurant']['inform'])
            valid_inform = t['goal']['restaurant']['inform']
            is_match = True
            for slot, value in task_informs.items():
                if value != valid_inform[slot]:
                    is_match = False
                    break
            if is_match:
                return True
    return False


def _get_msg(all_informs, inform_slots, request_slots):
    msg = '场景：用户正在寻找一家餐厅'
    for i in inform_slots:
        msg += ('，' + g.msg_inform_funcs[i](all_informs[i]))
    msg += ('，' + ensure_requests(request_slots))
    return msg


def _get_task(informs, request_slots, msg):
    """
    :param informs: informs slot values
    :type informs: dict
    :param request_slots: request slots
    :type request_slots: list
    :param msg:
    :return:
    """
    return {
        'goal': {
            'message': msg,
            'restaurant': {
                'inform': informs,
                'request': request_slots
            }
        },
        'log': []
    }


def reset_task_selected():
    current_time = datetime.datetime.utcnow()
    one_hour_ago = current_time - datetime.timedelta(minutes=30)
    tasks = db.session.query(Task).with_for_update() \
        .filter((Task.updated_at < one_hour_ago) & Task.selected)

    for task in tasks:
        task.selected = False


def want_name(name):
    return f'餐厅的名字是<b>{name}</b>'


def want_food_type(ftype):
    return f'餐厅提供的食物类型为<b>{ftype}</b>'


def want_price_range(price_range):
    return f'餐厅的价格为<b>{price_range}</b>'


def want_area(area):
    return f'餐厅的所在地区在<b>{area}</b>附近'


def ensure_requests(req):
    return '确保用户得到餐厅的<b>{}</b>'.format('、'.join(req))


@bp.route('/')
def index():
    return render_template('main.html')
