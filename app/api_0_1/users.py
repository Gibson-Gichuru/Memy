from flask import current_app, url_for, jsonify
from ..models import User, Permission

from .decorators import permission_required
from . import api
from .authentication import auth


@api.route('/user<int:id>')
@auth.login_required
def get_user(id):

	user = User.query.get_or_404(id)

	return jsonify(user.to_json())


