import hmac

from flask import Blueprint, request, current_app, jsonify

from git import Repo

bp = Blueprint('webhook', __name__)


@bp.route('/github', methods=['POST'])
def handle_github_hook():
    """Entry point for github webhook."""

    signature = request.headers.get('X-Hub-Signature')
    _, signature = signature.split('=')

    secret = current_app.config.get('GITHUB_SECRET').encode()

    hashhex = hmac.new(secret, request.data, digestmod='sha1').hexdigest()

    if hmac.compare_digest(hashhex, signature):
        repo = Repo(current_app.config.get('REPO_PATH'))
        origin = repo.remotes.origin
        origin.pull('--rebase')

        commit = request.json['after'][0:6]
        current_app.logger.info('Repository updated with commit {}'.format(commit))

    return jsonify({}, 200)
