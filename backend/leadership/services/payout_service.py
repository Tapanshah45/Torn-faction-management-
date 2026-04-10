from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from django.db.models import Count, DecimalField, Max, Sum, Value
from django.db.models.functions import Coalesce
from django.utils import timezone

from torn.models import WarLog

from ..models import RankedWarPayout, RankedWarPayoutMember


class RankedWarPayoutError(Exception):
    pass


def _quantize(value: Decimal) -> Decimal:
    return value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


@dataclass
class RankedWarContributionRow:
    member_id: int
    member_name: str
    total_hits: int
    total_respect: Decimal


@dataclass
class RankedWarPayoutResult:
    payout: RankedWarPayout
    rows: list[RankedWarPayoutMember]


class RankedWarPayoutService:
    PAYOUT_MODES = {'hits', 'respect'}

    def get_war_contributions(self, war_id: str) -> list[RankedWarContributionRow]:
        war_id = str(war_id).strip()
        if not war_id:
            raise RankedWarPayoutError('war_id is required.')

        aggregated = (
            WarLog.objects
            .filter(war_id=war_id)
            .values('member_id', 'member__name')
            .annotate(
                total_hits=Coalesce(Sum('attacks_won'), Value(0)),
                total_respect=Coalesce(Sum('respect_gain'), Value(0), output_field=DecimalField(max_digits=12, decimal_places=2)),
            )
            .order_by('-total_hits', '-total_respect', 'member__name')
        )

        rows = [
            RankedWarContributionRow(
                member_id=row['member_id'],
                member_name=row['member__name'],
                total_hits=int(row['total_hits'] or 0),
                total_respect=Decimal(str(row['total_respect'] or 0)),
            )
            for row in aggregated
            if (row['total_hits'] or 0) > 0 or Decimal(str(row['total_respect'] or 0)) > 0
        ]

        if not rows:
            raise RankedWarPayoutError('No Ranked War contribution data found for this war.')

        return rows

    def list_ranked_wars(self) -> list[dict[str, Any]]:
        wars = list(
            WarLog.objects
            .exclude(war_id__isnull=True)
            .exclude(war_id='')
            .values('war_id')
            .annotate(
                participants=Count('member', distinct=True),
                total_hits=Coalesce(Sum('attacks_won'), Value(0)),
                total_respect=Coalesce(Sum('respect_gain'), Value(0), output_field=DecimalField(max_digits=12, decimal_places=2)),
                last_timestamp=Max('timestamp'),
            )
            .order_by('-last_timestamp')
        )

        now = timezone.now()
        payload: list[dict[str, Any]] = []
        for war in wars:
            war_id = war['war_id']
            last_timestamp = war['last_timestamp']
            payload.append({
                'war_id': war_id,
                'participants': int(war['participants'] or 0),
                'total_hits': int(war['total_hits'] or 0),
                'total_respect': Decimal(str(war['total_respect'] or 0)),
                'is_active': bool(last_timestamp and (now - last_timestamp).total_seconds() < 24 * 3600),
                'last_timestamp': last_timestamp,
            })

        if payload:
            payload[0]['is_active'] = True
            for item in payload[1:]:
                item['is_active'] = False
        return payload

    def generate_rw_payout(self, *, war_id: str, total_pool: Decimal, faction_cut: Decimal, payout_mode: str, created_by: Any) -> RankedWarPayoutResult:
        if total_pool <= 0:
            raise RankedWarPayoutError('Total pool must be greater than zero.')
        if faction_cut < 0 or faction_cut > 100:
            raise RankedWarPayoutError('Faction cut must be between 0 and 100.')
        if payout_mode not in self.PAYOUT_MODES:
            raise RankedWarPayoutError('Invalid payout mode.')

        contributions = self.get_war_contributions(war_id=war_id)
        distributable_pool = _quantize(total_pool - (total_pool * faction_cut / Decimal('100')))

        basis_total = sum(
            (Decimal(row.total_hits) if payout_mode == 'hits' else row.total_respect)
            for row in contributions
        )
        if basis_total <= 0:
            raise RankedWarPayoutError('No usable contribution data found for selected payout mode.')

        payout = RankedWarPayout.objects.create(
            war_id=str(war_id),
            total_pool=total_pool,
            faction_cut=faction_cut,
            payout_mode=payout_mode,
            distributable_pool=distributable_pool,
            created_by=created_by,
        )

        rows: list[RankedWarPayoutMember] = []
        for row in contributions:
            basis_value = Decimal(row.total_hits) if payout_mode == 'hits' else row.total_respect
            contribution_percentage = (basis_value / basis_total) * Decimal('100')
            payout_amount = distributable_pool * (basis_value / basis_total)
            rows.append(RankedWarPayoutMember(
                payout=payout,
                member_id=row.member_id,
                total_hits=row.total_hits,
                total_respect=_quantize(row.total_respect),
                contribution_percentage=_quantize(contribution_percentage),
                payout_amount=_quantize(payout_amount),
            ))

        RankedWarPayoutMember.objects.bulk_create(rows)
        return RankedWarPayoutResult(payout=payout, rows=rows)


def generate_rw_payout(war_id, total_pool, faction_cut, payout_mode, created_by):
    service = RankedWarPayoutService()
    return service.generate_rw_payout(
        war_id=war_id,
        total_pool=total_pool,
        faction_cut=faction_cut,
        payout_mode=payout_mode,
        created_by=created_by,
    )
