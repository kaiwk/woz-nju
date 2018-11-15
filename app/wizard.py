import json

from flask import (Blueprint, render_template, request, session, jsonify,
                   redirect, url_for, current_app, flash)

from .database import Task, db
from .utils import get_priority, get_all_areas, get_all_food_types, get_all_price_ranges, add_turn_count

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
            return redirect(url_for('main.select_task'))

        current_app.logger.info('task id: {}'.format(task_id))
        body = json.loads(task.body)
        desc = body['goal']['message']
        log = body['log']
        db.session.commit()

        food_types, price_ranges, areas = get_task_attr()
        if task.evaluate > 5:
            evaluate = 'high'
        else:
            evaluate = 'low'
        if len(body['log']) > 1:
            metadata = body['log'][-2]['metadata']
        else:
            metadata = {'inform': {}, 'request': []}

        return render_template('wizard.html',
                               desc=desc,
                               log=log,
                               food_types=food_types,
                               price_ranges=price_ranges,
                               areas=areas,
                               metadata=metadata,
                               evaluate=evaluate)

    elif request.method == 'POST':
        resp = request.form['sys_resp']
        is_over = request.form.get('is_over') is not None
        if resp.strip():
            task_id = session['task_id']
            task = Task.query.filter_by(id=task_id).one()
            body = json.loads(task.body)
            # save the wizard response and metadata
            body['log'][-1]['text'].append(request.form['sys_resp'])
            if session.get('metadata'):
                body['log'][-1]['metadata'] = session['metadata']
            else:
                flash('请先确认当前表单，点击finish')
                return redirect(url_for('wizard.index'))
            task.body = json.dumps(body, ensure_ascii=False)
            task.priority = get_priority(body)
            task.selected = False
            task.finished = is_over
            db.session.commit()
            session.pop('task_id')
            session.pop('metadata')
            add_turn_count()
            return redirect(url_for('main.index'))
        else:
            flash('回复内容不能为空哦')
            return redirect(url_for('wizard.index'))


@bp.route('update_metadata/', methods=['POST'])
def update_metadata():
    """
    This method will not save the metadata, and metadata will be saved until
    worker submit the whole form.
    """
    name = request.form['want_name']
    food_type = request.form['want_food_type']
    price_range = request.form['want_price_range']
    area = request.form['want_area']
    request_food_type = request.form.get('request_food_type') is not None
    request_price_range = request.form.get('request_price_range') is not None
    request_recom = request.form.get('request_recom') is not None
    request_phone = request.form.get('request_phone') is not None
    request_addr = request.form.get('request_addr') is not None

    evaluate = request.form['evaluate']

    metadata = {'inform': {}, 'request': []}

    # inform
    if name.strip():
        metadata['inform']['name'] = name.strip()
    if food_type.strip():
        metadata['inform']['food_type'] = food_type
    if price_range.strip():
        metadata['inform']['price_range'] = price_range
    if area.strip():
        metadata['inform']['area'] = area

    # request
    if request_food_type:
        metadata['request'].append('food_type')
    if request_price_range:
        metadata['request'].append('price_range')
    if request_recom:
        metadata['request'].append('recommends')
    if request_phone:
        metadata['request'].append('phone')
    if request_addr:
        metadata['request'].append('address')

    session['metadata'] = metadata

    # update
    if evaluate == 'high':
        evaluate = 10
    else:
        evaluate = 5
    task_id = session['task_id']
    task = Task.query.filter_by(id=task_id).one()
    if evaluate:
        current_app.logger.debug('change %s evaluate from %s to %s', task, task.evaluate, evaluate)
        task.evaluate = evaluate
    db.session.commit()

    return jsonify(metadata)


def get_task_attr():
    return list(get_all_food_types()), list(get_all_price_ranges()), list(get_all_areas())
