import requests
import tldextract
import os
from dinamit import RUN_DIR
from dinamit.core.models import Domain, db
from dinamit.core.constants import DomainCategory
from pony.orm import db_session

FEED_REGISTRY = {}
extractor = tldextract.TLDExtract(cache_file=os.path.join(RUN_DIR, 'tld.cache'))


class MetaFeed(type):
    def __new__(meta, name, bases, class_dict):
        cls = type.__new__(meta, name, bases, class_dict)
        if name not in FEED_REGISTRY and name not in ('BaseFeed', 'TextFeed'):
            FEED_REGISTRY[name] = cls
        return cls


class BaseFeed(metaclass=MetaFeed):
    NAME = None
    SOURCE = None
    CATEGORY = None

    def __repr__(self):
        return self.NAME

    def run(self):
        self.pre_hook()
        content = self.fetch()
        items = self.split(content)
        for item in items:
            parsed = self.parse(item)
            if parsed is not None:
                target, category, is_sub = parsed
                self.save(target, category, is_sub)
        self.post_hook()

    def pre_hook(self):
        pass

    def post_hook(self):
        pass

    def split(self, content):
        raise NotImplementedError

    def fetch(self):
        raise NotImplementedError

    def parse(self, item):
        raise NotImplementedError

    @db_session
    def save(self, target, category, is_sub):
        d = db.Domain.select(lambda x: x.name == target).first()
        if not d:
            Domain(
                name=target, category=category, is_subdomain=is_sub
            )
            db.commit()
            return True
        return False


class TextFeed(BaseFeed):
    IGNORE_CHARS = (
        '#', '/'
    )

    def fetch(self):
        r = requests.get(self.SOURCE)
        if r.ok:
            return r.content.decode('utf-8')
        return None

    def split(self, content):
        return content.split('\n')

    def parse(self, item):
        clean_item = item.strip()
        if not clean_item:
            return None
        for ch in self.IGNORE_CHARS:
            if clean_item.startswith(ch):
                return None
        registered_domain = extractor(clean_item).registered_domain
        is_subdomain = registered_domain != clean_item
        returned_item = clean_item if is_subdomain else registered_domain
        return returned_item, self.CATEGORY, is_subdomain

