from celery import shared_task
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .serializers import ChainBreakEventSerializer, ReliabilityScoreSerializer
from torn.services import TornAPIService

from .services import ChainBreakDetectionService, ReliabilityScoringService


@shared_task
def scan_chain_break_events():
    service = TornAPIService()
    chain_data = service.get_chain_data().get('chain', {})
    detection = ChainBreakDetectionService()
    event = detection.evaluate(chain_data)
    if event:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'live_updates',
            {
                'type': 'send_update',
                'data': {
                    'type': 'chain_break',
                    'payload': ChainBreakEventSerializer(event).data,
                },
            },
        )
    return {'created': bool(event), 'chain_id': getattr(event, 'chain_id', None)}


@shared_task
def recalculate_reliability_scores():
    service = ReliabilityScoringService()
    scores = service.recalculate_all()
    channel_layer = get_channel_layer()
    if scores:
        async_to_sync(channel_layer.group_send)(
            'live_updates',
            {
                'type': 'send_update',
                'data': {
                    'type': 'reliability_refresh',
                    'payload': ReliabilityScoreSerializer(scores, many=True).data,
                },
            },
        )
    return {'updated': len(scores)}
