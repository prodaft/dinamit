from flask import flash, redirect, url_for, render_template
from dinamit.core.models import db


def render_with_flash(template_name, msg, category, **kwargs):
    if isinstance(msg, dict):
        for n, m in msg.items():
            flash(
                '{}: {}'.format(n, ', '.join(m)), category
            )
    else:
        flash(msg, category)
    context = {}
    context.update(kwargs)
    return render_template(template_name, **context)


def redirect_with_flash(msg, category, path, flag=True):
    if flag:
        flash(msg, category)
    return redirect(url_for(path))


def create_super_user(email, password, first_name='', last_name=''):
    client = db.Client.get(email=email, password=password, first_name=first_name, last_name=last_name)
    if not client:
        db.Client(email=email, password=password, first_name=first_name, last_name=last_name)
        db.commit()
        return True
    else:
        return False
