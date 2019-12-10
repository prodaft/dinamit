from dinamit import GLOBAL_SETTINGS
from dinamit.core.utils import make_celery
from dinamit.panel.app import app
from dinamit.feeds.base import FEED_REGISTRY


celery = make_celery(app)
celery.conf.broker_url = GLOBAL_SETTINGS['broker']['uri']
celery.conf.result_backend = GLOBAL_SETTINGS['broker']['uri']
celery.conf.task_serializer = 'json'
celery.conf.result_serializer = 'json'
celery.conf.accept_content = ['json']
celery.conf.beat_schedule = {
    'daily-feed-update': {
        'task': 'dinamit.tasks.update_feeds',
        'schedule': 60.0
    },
}
celery.conf.timezone = 'UTC'


@celery.task
def update_feeds():
    for name, cls in FEED_REGISTRY.items():
        ins = cls()
        ins.run()

