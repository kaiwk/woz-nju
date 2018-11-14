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
        evaluate = task.evaluate
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
            desc = body['goal']['message']
            task.body = json.dumps(body, ensure_ascii=False)
            task.priority = get_priority(body)
            task.selected = False
            task.finished = is_over
            db.session.commit()
            session.pop('task_id')
            session.pop('metadata')
            add_turn_count()
            return render_template('wizard.html',
                                   desc=desc,
                                   log=body['log'])
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
    request_food_type = True if request.form['request_food_type'] == 'yes' else False
    request_price_range = True if request.form['request_price_range'] == 'yes' else False
    request_recom = True if request.form['request_recom'] == 'yes' else False
    request_phone = True if request.form['request_phone'] == 'yes' else False
    request_addr = True if request.form['request_addr'] == 'yes' else False

    evaluate = request.form['evaluate']

    metadata = {'inform': {}, 'request': []}

    # inform
    if name.strip():
        metadata['inform']['name'] = name
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

    # update evaluate
    task_id = session['task_id']
    task = Task.query.filter_by(id=task_id).one()
    evaluate = evaluate.strip()
    if evaluate:
        try:
            current_app.logger.debug('change %s evaluate from %s to %s', task, task.evaluate, evaluate)
            task.evaluate = int(evaluate)
        except ValueError:
            pass
    db.session.commit()

    return jsonify(metadata)


def get_task_attr():
    return list(get_all_food_types()), list(get_all_price_ranges()), list(get_all_areas())
