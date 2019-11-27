from flask import Flask, render_template, request
from dinamit.core.models import db
from dinamit import RUN_DIR
import tldextract
import os

app = Flask(__name__)
extractor = tldextract.TLDExtract(cache_file=os.path.join(RUN_DIR, 'tld.cache'))


@app.route('/')
def homepage():
    host_name = request.headers.get('Host', None)
    domain_name = extractor(host_name).registered_domain
    domain = db.Domain.select(lambda d: d.name == domain_name).first()
    if domain:
        category = domain.category
    else:
        category = 'Uncategorized'
    return render_template('index.html', **locals())
