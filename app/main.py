import json
import random
import datetime

from flask import Blueprint, session, redirect, url_for, current_app
from sqlalchemy import not_, func

from .database import Task, db
from .utils import get_tasks

bp = Blueprint('main', __name__,
               static_folder='static',
               template_folder='templates')


@bp.route('/')
def index():

    reset_task_selected()

    task = db.session.query(Task).with_for_update()\
        .filter(not_(Task.selected) & not_(Task.finished))\
        .order_by(func.rand())\
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


def reset_task_selected():
    current_time = datetime.datetime.utcnow()
    one_hour_ago = current_time - datetime.timedelta(hours=1, minutes=30)
    tasks = db.session.query(Task).with_for_update() \
        .filter((Task.updated_at < one_hour_ago) & Task.selected)

    for task in tasks:
        task.selected = False


def get_task():
    tasks = get_tasks()
    food_types = list(set([t['tag'] for t in tasks]))
    price_ranges = list(set([t['price_range'] for t in tasks]))
    rates = ['高', None]

    food_type = random.choice(food_types)
    price_range = random.choice(price_ranges)
    rate = random.choice(rates)

    requests = ['地址', '电话', '推荐菜']
    requests = random.sample(requests, 2)

    return json.dumps({
        'goal': {
            'message': want_food(food_type) + '，' +
                       want_price_range(price_range) + '，' +
                       want_rate(rate) + '，' +
                       ensure_requests(requests),
            'restaurant': {
                'inform': {
                    'food': food_type,
                    'price_range': price_range
                },
                'request': requests
            },
        },
        'log': []
    }, ensure_ascii=False)


def want_food(ftype):
    return '假设你正在寻找一家提供<b>{}</b>的餐厅'.format(ftype)


def want_price_range(price_range):
    return '餐厅的价格为<b>{}</b>'.format(price_range)


def want_rate(rate):
    if rate:
        return '你希望这家餐厅有<b>{}</b>用户评分'.format(rate)
    else:
        return '你不关心用户评分'


def ensure_requests(req):
    return '确保你得到餐厅的<b>{}</b>，若未找到符合条件的餐厅可以回复<b>结束语</b>离开对话'.format('、'.join(req))


