from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Faction, Member, ActivitySnapshot, OrganizedCrime
from .services import TornAPIService
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import logging

logger = logging.getLogger(__name__)


def _iter_crimes(crimes_payload):
    if isinstance(crimes_payload, dict):
        return crimes_payload.values()
    if isinstance(crimes_payload, list):
        return crimes_payload
    return []


def _iter_participants(crime_payload):
    participants = crime_payload.get('participants') or crime_payload.get('slots') or crime_payload.get('members') or []
    if isinstance(participants, dict):
        return participants.values()
    if isinstance(participants, list):
        return participants
    return []


def _extract_player_id(participant):
    if not isinstance(participant, dict):
        return None

    user_value = participant.get('user')
    candidates = [
        participant.get('user_id'),
        participant.get('userID'),
        participant.get('player_id'),
        participant.get('ID'),
        participant.get('id'),
        user_value.get('ID') if isinstance(user_value, dict) else user_value,
    ]
    for candidate in candidates:
        if candidate in (None, ''):
            continue
        try:
            return int(candidate)
        except (TypeError, ValueError):
            continue
    return None


def _extract_crime_success(crime_payload):
    if 'success' in crime_payload:
        return bool(crime_payload.get('success'))
    result = str(crime_payload.get('result', '')).lower()
    if result:
        return 'success' in result
    return False

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
            live_member_ids = set()
            for player_id, member_data in data['members'].items():
                player_id_int = int(player_id)
                live_member_ids.add(player_id_int)
                member, _ = Member.objects.update_or_create(
                    torn_player_id=player_id_int,
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

            # Keep local DB aligned with current faction roster from Torn.
            Member.objects.filter(faction=faction).exclude(
                torn_player_id__in=live_member_ids
            ).update(status='Inactive')
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
def sync_organized_crimes():
    service = TornAPIService()
    try:
        members_data = service.get_faction_members()
        if not members_data or 'ID' not in members_data:
            logger.warning('Skipping OC sync: live faction not available.')
            return {'synced': 0, 'reason': 'no_live_faction'}

        faction_id = members_data['ID']
        faction = Faction.objects.filter(torn_faction_id=faction_id).first()
        if not faction:
            logger.warning('Skipping OC sync: no local faction row for live faction id %s.', faction_id)
            return {'synced': 0, 'reason': 'no_local_faction'}

        member_map = {
            member.torn_player_id: member
            for member in Member.objects.filter(faction=faction)
        }

        crimes_data = service.get_organized_crimes_data() or {}
        if 'crimes' not in crimes_data:
            logger.warning('Skipping OC sync: crimes payload missing.')
            return {'synced': 0, 'reason': 'no_crimes_payload'}

        rows_to_create = []
        for crime in _iter_crimes(crimes_data.get('crimes')):
            if not isinstance(crime, dict):
                continue
            crime_name = crime.get('crime_name') or crime.get('name') or 'Unknown Crime'
            success = _extract_crime_success(crime)

            for participant in _iter_participants(crime):
                player_id = _extract_player_id(participant)
                if not player_id:
                    continue
                member = member_map.get(player_id)
                if not member:
                    continue

                role = 'Unknown'
                if isinstance(participant, dict):
                    role = participant.get('position') or participant.get('role') or participant.get('name') or 'Unknown'

                rows_to_create.append(OrganizedCrime(
                    member=member,
                    crime_name=crime_name,
                    role=role,
                    success=success,
                ))

        # Keep tracker aligned with current faction OCs and avoid duplicate drift.
        OrganizedCrime.objects.filter(member__faction=faction).delete()
        if rows_to_create:
            OrganizedCrime.objects.bulk_create(rows_to_create)

        return {'synced': len(rows_to_create), 'faction_id': faction_id}
    except Exception as e:
        logger.error(f"Error syncing organized crimes: {str(e)}")
        return {'synced': 0, 'error': str(e)}

@shared_task
def purge_old_snapshots():
    cutoff = timezone.now() - timedelta(days=90)
    deleted, _ = ActivitySnapshot.objects.filter(timestamp__lt=cutoff).delete()
    logger.info(f"Purged {deleted} old activity snapshots.")
