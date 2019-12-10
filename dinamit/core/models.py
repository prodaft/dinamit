from pony.orm import Required, Database, Set, Optional, Json
from flask_login import UserMixin
from datetime import datetime
from enum import Enum
from pony.orm.dbapiprovider import StrConverter
from dinamit.core.constants import DomainCategory, DomainAction
from flask import request, url_for

db = Database()


class EnumConverter(StrConverter):

    def validate(self, val, obj=None):
        if not isinstance(val, Enum):
            raise ValueError('Instance must be Enum type. Got: {}'.format(type(val)))
        return val

    def py2sql(self, val):
        return val.name

    def sql2py(self, val):
        return self.py_type[val]


class Client(db.Entity, UserMixin):
    first_name = Required(str)
    last_name = Required(str)
    email = Required(str, unique=True)
    password = Required(str)
    is_active = Required(bool, default=lambda: True)
    assets = Set('Asset')
    rules = Required(Json, default=lambda: {})
    policy = Required(Json, default=lambda: {})
    queries = Set('Query')
    created_at = Optional(datetime, default=lambda: datetime.now())
    last_login = Optional(datetime)

    @property
    def full_name(self):
        return '{} {}'.format(
            self.first_name, self.last_name
        )


class Asset(db.Entity):
    name = Required(str)
    ip = Required(str, unique=True)
    is_verified = Required(bool, default=lambda: True)
    verification_hash = Optional(str)
    client = Required(Client)
    queries = Set('Query')
    created_at = Required(datetime, default=lambda: datetime.now())

    @property
    def get_verification_url(self):
        return '{}{}'.format(
            request.host, url_for('asset.verify', verification_hash=self.verification_hash)
        )


class Domain(db.Entity):
    name = Required(str)
    category = Required(DomainCategory)
    queries = Set('Query')
    include_subdomains = Required(bool, default=lambda: False)
    is_categorized = Required(bool, default=lambda: False)
    is_subdomain = Required(bool, default=lambda: False)
    created_at = Required(datetime, default=lambda: datetime.now())


class Query(db.Entity):
    domain = Optional(Domain)
    request = Required(str)
    dns_type = Required(str)
    action = Required(DomainAction)
    reason = Required(str)
    client = Required(Client)
    asset = Optional(Asset)
    created_at = Required(datetime, default=lambda: datetime.now())
