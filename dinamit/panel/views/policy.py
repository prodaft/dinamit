from flask import Blueprint, render_template, request
from flask_login import current_user, login_required
from dinamit import PANEL_TEMPLATE_DIR
from dinamit.core.models import db
from dinamit.core.utils import create_rule_hash
from dinamit.panel.forms.rule import CreateForm
from dinamit.panel.helpers import redirect_with_flash

policy = Blueprint(
    'policy', __name__, template_folder=PANEL_TEMPLATE_DIR, url_prefix='/policy'
)


@policy.route('/index', methods=['GET'])
@login_required
def index():
    return render_template('policy/index.html')


@policy.route('/update', methods=['POST'])
@login_required
def update():
    return render_template('policy/index.html')
