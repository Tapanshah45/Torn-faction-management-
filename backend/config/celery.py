import os
from celery import Celery
from celery.schedules import crontab
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
app = Celery('torn_faction')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
app.conf.beat_schedule = {
    'take-activity-snapshots-every-5-minutes': {
        'task': 'torn.tasks.take_activity_snapshots',
        'schedule': crontab(minute='*/5'),
    },
    'sync-live-chains-every-30-seconds': {
        'task': 'torn.tasks.sync_live_chain_data',
        'schedule': 30.0,
    },
    'purge-old-snapshots-daily': {
        'task': 'torn.tasks.purge_old_snapshots',
        'schedule': crontab(minute=0, hour=0),
    },
}
