from flask import Blueprint, render_template

bp = Blueprint('online_help', __name__,
               static_folder='static',
               template_folder='templates')


@bp.route('/help')
def video_help():
    return render_template('online_help.html')

