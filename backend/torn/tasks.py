from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Faction, Member, ActivitySnapshot
from .services import TornAPIService
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import logging

logger = logging.getLogger(__name__)

@shared_task
def take_activity_snapshots():
    service = TornAPIService()
    try:
        data = service.get_faction_members()
        if data and 'members' in data:
            faction, _ = Faction.objects.get_or_create(
                torn_faction_id=data.get('ID', 0),
                defaults={'name': data.get('name', 'Unknown')}
            )
            for player_id, member_data in data['members'].items():
                member, _ = Member.objects.update_or_create(
                    torn_player_id=player_id,
                    defaults={
                        'name': member_data.get('name'),
                        'level': member_data.get('level', 0),
                        'faction_rank': member_data.get('position'),
                        'status': member_data.get('status', {}).get('state'),
                        'faction': faction,
                    }
                )
                ActivitySnapshot.objects.create(
                    member=member,
                    online_status=member_data.get('last_action', {}).get('status', 'offline'),
                    chain_hits=0,
                    respect=0,
                    war_hits=0
                )
    except Exception as e:
        logger.error(f"Error taking snapshots: {str(e)}")

@shared_task
def sync_live_chain_data():
    service = TornAPIService()
    try:
        data = service.get_chain_data()
        if data and 'chain' in data:
            chain_info = data['chain']
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "live_updates",
                {
                    "type": "send_update",
                    "data": {
                        "type": "chain",
                        "payload": chain_info
                    }
                }
            )
    except Exception as e:
        logger.error(f"Error syncing chain data: {str(e)}")

@shared_task
def purge_old_snapshots():
    cutoff = timezone.now() - timedelta(days=90)
    deleted, _ = ActivitySnapshot.objects.filter(timestamp__lt=cutoff).delete()
    logger.info(f"Purged {deleted} old activity snapshots.")
