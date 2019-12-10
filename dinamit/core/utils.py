from codecs import encode, decode
from babel import dates
from celery import Celery


def create_rule_hash(src, dst):
    return decode(encode(encode('{}-{}'.format(src, dst), 'utf-8'), 'hex'), 'utf-8')


def convert_datetime(dt):
    return dates.format_datetime(dt)


def make_celery(a):
    celery = Celery(a.import_name)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with a.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery
