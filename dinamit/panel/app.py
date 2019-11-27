from flask import Flask, render_template, request, flash, redirect, url_for
from flask_login import LoginManager, login_required, logout_user, login_user, current_user
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt
from datetime import datetime
from pony.orm import desc
from dinamit import CURRENT_VERSION, GLOBAL_SETTINGS, SECRET_KEY
from dinamit.core.models import db
from dinamit.core.utils import convert_datetime
from dinamit.panel.views import asset, rule, policy, profile

app = Flask(__name__)
app.config.update(dict(
    DEBUG=GLOBAL_SETTINGS['debug'],
    SECRET_KEY=SECRET_KEY,
    SESSION_TYPE='filesystem',
    PONY={
        'provider': 'postgres',
        'host': GLOBAL_SETTINGS['database']['host'],
        'user': GLOBAL_SETTINGS['database']['user'],
        'password': GLOBAL_SETTINGS['database']['password'],
        'database': GLOBAL_SETTINGS['database']['name']
    }
))
csrf = CSRFProtect(app)
bcrypt = Bcrypt(app)
app.register_blueprint(asset)
app.register_blueprint(rule)
app.register_blueprint(policy)
app.register_blueprint(profile)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


@app.context_processor
def inject_state():
    return dict(
        current_version=CURRENT_VERSION,
        current_mode=GLOBAL_SETTINGS.get('mode', 'dev'),
        current_user=current_user
    )


@login_manager.user_loader
def load_user(user_id):
    return db.Client.get(id=user_id)


@app.template_filter('datetime')
def _jinja2_filter_datetime(value):
    return convert_datetime(value)


@app.route('/', methods=['GET'])
@login_required
def homepage():
    recent_queries = current_user.queries.order_by(desc(db.Query.created_at))[:4]
    query_count = current_user.queries.count()
    return render_template('index.html', **locals())


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        possible_user = db.Client.get(email=email)

        if possible_user and bcrypt.check_password_hash(possible_user.password, password):
            possible_user.last_login = datetime.now()
            login_user(possible_user)
            return redirect(url_for('homepage'))

        flash('Login error', 'danger')
        return redirect(url_for('login'))
    else:
        return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out', 'success')
    return redirect(url_for('login'))
