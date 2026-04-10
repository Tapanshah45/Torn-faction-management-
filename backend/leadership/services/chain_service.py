from __future__ import annotations

from datetime import timedelta
from typing import Any

from django.utils import timezone

from core.models import Alert
from torn.models import Member

from ..models import ChainAssignment, ChainBreakEvent


class ChainBreakDetectionService:
    def _extract_time_remaining(self, chain_data: dict[str, Any]) -> int | None:
        candidates = [chain_data.get('time_remaining'), chain_data.get('timeout'), chain_data.get('timer'), chain_data.get('time_left')]
        for candidate in candidates:
            if candidate is None:
                continue
            if isinstance(candidate, (int, float)):
                return int(candidate)
            if isinstance(candidate, str) and ':' in candidate:
                parts = candidate.split(':')
                if len(parts) == 2:
                    minutes, seconds = parts
                    return int(minutes) * 60 + int(seconds)
            try:
                return int(candidate)
            except (TypeError, ValueError):
                continue
        return None

    def evaluate(self, chain_data: dict[str, Any], *, chain_id: str | None = None) -> ChainBreakEvent | None:
        if not chain_data:
            return None

        chain_id = chain_id or str(chain_data.get('ID') or chain_data.get('chain_id') or 'live')
        time_remaining = self._extract_time_remaining(chain_data)
        last_hit_time = chain_data.get('last_hit_time') or chain_data.get('timestamp')
        last_hitter_name = chain_data.get('last_hit_name') or chain_data.get('last_hitter') or chain_data.get('last_hit_member')
        suspected_member = None
        slot_assignee = None
        expected_next_hit_by = None

        if time_remaining is not None:
            expected_next_hit_by = timezone.now() + timedelta(seconds=time_remaining)

        if time_remaining is not None and time_remaining <= 0:
            alert_reason = 'Chain broken: timeout exceeded'
        elif time_remaining is not None and time_remaining < 20:
            alert_reason = f'Chain critical: {time_remaining} sec remaining'
        else:
            return None

        latest_event = ChainBreakEvent.objects.filter(chain_id=chain_id).order_by('-timestamp').first()
        if latest_event:
            duplicate_window = (timezone.now() - latest_event.timestamp).total_seconds() < 30
            same_state = latest_event.chain_broken == (time_remaining is not None and time_remaining <= 0)
            same_reason = latest_event.reason == alert_reason and latest_event.time_remaining == time_remaining
            if duplicate_window and same_state and same_reason:
                return None

        if chain_data.get('suspected_member_id'):
            suspected_member = Member.objects.filter(id=chain_data['suspected_member_id']).first()
        elif chain_data.get('suspected_member_name'):
            suspected_member = Member.objects.filter(name=chain_data['suspected_member_name']).first()

        assignment = ChainAssignment.objects.filter(chain_id=chain_id, completed=False).select_related('member').order_by('assigned_slot_time').first()
        if assignment:
            slot_assignee = assignment.member
            if not suspected_member:
                suspected_member = assignment.member

        event = ChainBreakEvent.objects.create(
            chain_id=chain_id,
            last_hit_time=last_hit_time if hasattr(last_hit_time, 'tzinfo') else None,
            expected_next_hit_by=expected_next_hit_by,
            suspected_member=suspected_member,
            slot_assignee=slot_assignee,
            reason=alert_reason,
            chain_broken=time_remaining is not None and time_remaining <= 0,
            time_remaining=time_remaining,
            last_hitter_name=str(last_hitter_name) if last_hitter_name else None,
        )

        if slot_assignee:
            Alert.objects.create(member=slot_assignee, alert_type='chain_break', severity='critical')
        elif suspected_member:
            Alert.objects.create(member=suspected_member, alert_type='chain_break', severity='high')

        return event
