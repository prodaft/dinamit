from flask import Blueprint, render_template, request
from flask_login import current_user, login_required
from dinamit import PANEL_TEMPLATE_DIR
from dinamit.panel.helpers import redirect_with_flash
from dinamit.core.models import db
from pony.orm import desc
from uuid import uuid4
from dinamit.panel.forms.asset import CreateForm

asset = Blueprint(
    'asset', __name__, template_folder=PANEL_TEMPLATE_DIR, url_prefix='/asset'
)


def create_verification_hash():
    return str(uuid4())


@asset.route('/index', methods=['GET'])
@login_required
def index():
    assets = current_user.assets.order_by(desc(db.Asset.created_at))
    return render_template('asset/index.html', assets=assets)


@asset.route('/verify/<string:verification_hash>', methods=['GET'])
def verify(verification_hash):
    item = db.Asset.select(lambda a: a.verification_hash == verification_hash).first()
    if not item:
        return 'Verification hash is not valid.'

    if item.ip != request.remote_addr:
        return 'You have to visit this link from defined ip address.'

    item.is_verified = True
    item.verification_hash = ''
    db.commit()
    return 'Asset verified.'


@asset.route('/create', methods=['POST'])
@login_required
def create():
    form = CreateForm(request.form)
    if request.method == 'POST' and form.validate():
        item = db.Asset.select(lambda a: a.ip == form.ip.data).first()
        if item:
            return redirect_with_flash(
                'Asset already exists', 'warning', 'asset.index'
            )

        current_user.assets.create(
            name=form.name.data, ip=form.ip.data, is_verified=False, verification_hash=create_verification_hash()
        )
        db.commit()
        return redirect_with_flash(
            'Asset created', 'success', 'asset.index'
        )

    return redirect_with_flash(
        'Error happened', 'danger', 'asset.index'
    )


@asset.route('/delete/<int:pk>', methods=['POST'])
@login_required
def delete(pk):
    item = current_user.assets.select(lambda a: a.id == pk).first()
    if not item:
        return redirect_with_flash(
            'Asset does not exists', 'warning', 'asset.index'
        )
    item.delete()
    db.commit()
    return redirect_with_flash(
        'Asset deleted', 'success', 'asset.index'
    )
