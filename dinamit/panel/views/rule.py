from flask import Blueprint, render_template, request
from flask_login import current_user, login_required
from dinamit import PANEL_TEMPLATE_DIR
from dinamit.core.models import db
from dinamit.core.utils import create_rule_hash
from dinamit.panel.forms.rule import CreateForm
from dinamit.panel.helpers import redirect_with_flash

rule = Blueprint(
    'rule', __name__, template_folder=PANEL_TEMPLATE_DIR, url_prefix='/rule'
)


@rule.route('/index', methods=['GET'])
@login_required
def index():
    assets = current_user.assets.select(lambda a: a.is_verified)
    rules = current_user.rules.items()
    return render_template('rule/index.html', rules=rules, assets=assets)


@rule.route('/create', methods=['POST'])
@login_required
def create():
    form = CreateForm(request.form)
    if request.method == 'POST' and form.validate():
        source = form.source.data
        destination = form.destination.data
        action = form.action.data

        if source != '*':
            asset = current_user.assets.select(lambda a: a.id == source and a.is_verified).first()
            if not asset:
                return redirect_with_flash(
                    'Asset does not exists', 'danger', 'rule.index'
                )
            source = asset.ip

        rule_hash = create_rule_hash(source, destination)
        rules = current_user.rules
        rules[rule_hash] = {
            'source': source,
            'destination': destination,
            'action': action,
        }
        current_user.rules = rules
        db.commit()
        return redirect_with_flash(
            'Rule created', 'success', 'rule.index'
        )

    return redirect_with_flash(
        'Error happened', 'danger', 'rule.index'
    )


@rule.route('/delete/<string:k>', methods=['POST'])
@login_required
def delete(k):
    rules = current_user.rules
    if k not in rules:
        return redirect_with_flash(
            'Rule does not exists', 'warning', 'rule.index'
        )

    del rules[k]
    current_user.rules = rules
    db.commit()

    return redirect_with_flash(
        'Rule deleted', 'success', 'rule.index'
    )
