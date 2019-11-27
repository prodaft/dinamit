import os
import json
from codecs import encode, decode

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.abspath(os.path.join(ROOT_DIR, os.pardir))
RUN_DIR = os.path.join(PARENT_DIR, 'run')
if not os.path.isdir(RUN_DIR):
    os.mkdir(RUN_DIR)

SECRET_KEY_PATH = os.path.join(RUN_DIR, '.secret')
if not os.path.isfile(SECRET_KEY_PATH):
    SECRET_KEY = decode(encode(os.urandom(256), 'hex'), 'utf-8')
    with open(SECRET_KEY_PATH, 'w') as fp:
        fp.write(SECRET_KEY)
else:
    with open(SECRET_KEY_PATH, 'r') as fp:
        SECRET_KEY = fp.read()

PANEL_DIR = os.path.join(ROOT_DIR, 'panel')
PANEL_TEMPLATE_DIR = os.path.join(PANEL_DIR, 'templates')
CURRENT_VERSION = open(os.path.join(ROOT_DIR, '.version')).read().strip()
GLOBAL_SETTINGS = json.loads(open(os.path.join(PARENT_DIR, 'settings.json')).read())
