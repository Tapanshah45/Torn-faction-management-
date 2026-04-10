from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from django.db.models import Sum
from django.utils import timezone

from torn.models import ActivitySnapshot, ChainLog, Member, OrganizedCrime, WarLog

from ..models import ChainAssignment, ReliabilityScore


def _quantize(value: Decimal) -> Decimal:
    return value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def _risk_level(final_score: Decimal) -> str:
    score = float(final_score)
    if score >= 80:
        return 'highly_reliable'
    if score >= 60:
        return 'stable'
    if score >= 40:
        return 'at_risk'
    return 'high_kick_risk'


class ReliabilityScoringService:
    def recalculate_member(self, member: Member) -> ReliabilityScore:
        now = timezone.now()
        last_action = member.last_action or ActivitySnapshot.objects.filter(member=member).order_by('-timestamp').values_list('timestamp', flat=True).first()
        if last_action:
            inactive_hours = max((now - last_action).total_seconds() / 3600, 0)
        else:
            inactive_hours = 999

        if inactive_hours < 6:
            activity_score = Decimal('100')
        elif inactive_hours < 24:
            activity_score = Decimal('70')
        elif inactive_hours < 72:
            activity_score = Decimal('40')
        else:
            activity_score = Decimal('20')

        assignments = ChainAssignment.objects.filter(member=member)
        chain_completed = assignments.filter(completed=True).count()
        chain_expected = assignments.count() or max(ChainLog.objects.filter(member=member).aggregate(total=Sum('hits')).get('total') or 0, 1)
        chain_score = Decimal(chain_completed * 100 / chain_expected) if chain_expected else Decimal('0')

        war_rows = WarLog.objects.filter(member=member)
        war_success = war_rows.aggregate(total=Sum('attacks_won'))['total'] or 0
        war_lost = war_rows.aggregate(total=Sum('attacks_lost'))['total'] or 0
        war_assists = war_rows.aggregate(total=Sum('assists'))['total'] or 0
        war_attempts = war_success + war_lost + war_assists
        war_score = Decimal(war_success * 100 / war_attempts) if war_attempts else Decimal('0')

        oc_total = OrganizedCrime.objects.filter(member=member).count()
        oc_success = OrganizedCrime.objects.filter(member=member, success=True).count()
        oc_score = Decimal(oc_success * 100 / oc_total) if oc_total else Decimal('0')

        final_score = (
            activity_score * Decimal('0.30') +
            chain_score * Decimal('0.30') +
            war_score * Decimal('0.20') +
            oc_score * Decimal('0.20')
        )
        risk_level = _risk_level(final_score)

        score, _ = ReliabilityScore.objects.update_or_create(
            member=member,
            defaults={
                'activity_score': _quantize(activity_score),
                'chain_score': _quantize(chain_score),
                'war_score': _quantize(war_score),
                'oc_score': _quantize(oc_score),
                'final_score': _quantize(final_score),
                'risk_level': risk_level,
                'details': {
                    'inactive_hours': round(inactive_hours, 2),
                    'chain_completed': chain_completed,
                    'chain_expected': chain_expected,
                    'war_success': war_success,
                    'war_attempts': war_attempts,
                    'oc_success': oc_success,
                    'oc_total': oc_total,
                },
            },
        )
        return score

    def recalculate_all(self) -> list[ReliabilityScore]:
        return [self.recalculate_member(member) for member in Member.objects.all()]
