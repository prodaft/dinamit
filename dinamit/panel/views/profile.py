from flask import Blueprint, render_template, request
from flask_login import current_user, login_required
from dinamit import PANEL_TEMPLATE_DIR
from dinamit.panel.helpers import redirect_with_flash
from dinamit.core.models import db
from dinamit.panel.forms.profile import UpdateForm

profile = Blueprint(
    'profile', __name__, template_folder=PANEL_TEMPLATE_DIR, url_prefix='/profile'
)


@profile.route('/index', methods=['GET'])
@login_required
def index():
    return render_template('profile/index.html')


@profile.route('/update', methods=['POST'])
@login_required
def update():
    form = UpdateForm(request.form)
    if request.method == 'POST' and form.validate():
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data

        exists_email = db.Client.select(lambda c: c.email == email).first()

        if email != current_user.email and exists_email:
            return redirect_with_flash(
                'Email already exists', 'warning', 'profile.index'
            )

        current_user.first_name = first_name
        current_user.last_name = last_name
        current_user.email = email
        db.commit()
        return redirect_with_flash(
            'Profile updated', 'success', 'profile.index'
        )

    return redirect_with_flash(
        'Error happened', 'danger', 'profile.index'
    )
