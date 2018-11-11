import json

from flask import (Blueprint, render_template, request, session, jsonify,
                   redirect, url_for, current_app, flash)

from .database import Task, db
from .utils import get_all_tasks, get_priority

bp = Blueprint('wizard', __name__,
               static_folder='static',
               template_folder='templates')


@bp.route('wizard/', methods=['GET', 'POST'])
def index():

    if request.method == 'GET':
        if session.get('task_id'):
            task_id = session['task_id']
            task = Task.query.filter_by(id=task_id).one()
        else:
            return redirect(url_for('main.index'))

        current_app.logger.info('task id: {}'.format(task_id))
        body = json.loads(task.body)
        log = body['log']
        db.session.commit()

        food_types, price_ranges, rates = get_task_attr()

        return render_template('wizard.html',
                               log=log,
                               food_types=food_types,
                               price_ranges=price_ranges,
                               rates=rates)

    elif request.method == 'POST':
        resp = request.form['sys_resp']
        is_over = request.form.get('is_over') is not None
        if resp.strip():
            task_id = session['task_id']
            task = Task.query.filter_by(id=task_id).one()
            body = json.loads(task.body)
            # save the wizard response and metadata
            body['log'][-1]['text'].append(request.form['sys_resp'])
            body['log'][-1]['metadata'] = session['metadata']
            task.body = json.dumps(body, ensure_ascii=False)
            task.priority = get_priority(body)
            task.selected = False
            task.finished = is_over
            db.session.commit()
            session.clear()
            return render_template('wizard.html', log=body['log'])
        else:
            flash('回复内容不能为空哦')
            return redirect(url_for('wizard.index'))


@bp.route('update_metadata/', methods=['POST'])
def update_metadata():
    """
    This method will not save the metadata, and metadata will be saved until
    worker submit the whole form.
    """
    food_type = request.form['want_food_type']
    price_range = request.form['want_price_range']
    rate = request.form['want_rate']
    request_food_type = True if request.form['request_food_type'] == 'yes' else False
    request_price_range = True if request.form['request_price_range'] == 'yes' else False
    request_recom = True if request.form['request_recom'] == 'yes' else False
    request_phone = True if request.form['request_phone'] == 'yes' else False
    request_addr = True if request.form['request_addr'] == 'yes' else False

    metadata = {'inform': {}, 'request': []}

    # inform
    if food_type.strip():
        metadata['inform']['food_type'] = food_type
    if price_range.strip():
        metadata['inform']['price_range'] = price_range
    if rate.strip():
        metadata['inform']['rate'] = rate

    # request
    if request_food_type:
        metadata['request'].append('food_type')
    if request_price_range:
        metadata['request'].append('price_range')
    if request_recom:
        metadata['request'].append('recommendation')
    if request_phone:
        metadata['request'].append('phone')
    if request_addr:
        metadata['request'].append('address')

    session['metadata'] = metadata
    return jsonify(metadata)


def get_task_attr():
    tasks = get_all_tasks()
    food_types = list(set([t['tag'] for t in tasks]))
    price_ranges = list(set([t['price_range'] for t in tasks]))
    rates = ['高', '不关心']
    return food_types, price_ranges, rates
