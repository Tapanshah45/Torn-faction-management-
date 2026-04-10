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
    'sync-organized-crimes-every-5-minutes': {
        'task': 'torn.tasks.sync_organized_crimes',
        'schedule': crontab(minute='*/5'),
    },
    'scan-chain-break-events-every-30-seconds': {
        'task': 'leadership.tasks.scan_chain_break_events',
        'schedule': 30.0,
    },
    'recalculate-reliability-scores-every-30-minutes': {
        'task': 'leadership.tasks.recalculate_reliability_scores',
        'schedule': crontab(minute='*/30'),
    },
    'purge-old-snapshots-daily': {
        'task': 'torn.tasks.purge_old_snapshots',
        'schedule': crontab(minute=0, hour=0),
    },
}
