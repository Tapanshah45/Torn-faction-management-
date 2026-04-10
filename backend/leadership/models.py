from django.conf import settings
from django.db import models

from torn.models import Member


class PayoutCalculation(models.Model):
    PAYOUT_MODE_CHOICES = (
        ('hits', 'Total Hits'),
        ('respect', 'Respect Gained'),
    )

    total_pool = models.DecimalField(max_digits=16, decimal_places=2)
    faction_cut = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    payout_mode = models.CharField(max_length=20, choices=PAYOUT_MODE_CHOICES)
    bonus_config = models.JSONField(default=dict, blank=True)
    exclusion_rules = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payout_calculations')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Payout {self.id} - {self.payout_mode}'


class PayoutDistribution(models.Model):
    payout_calculation = models.ForeignKey(PayoutCalculation, on_delete=models.CASCADE, related_name='distributions')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='payout_distributions')
    contribution_value = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    share_percentage = models.DecimalField(max_digits=7, decimal_places=4, default=0)
    final_payout = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    is_excluded = models.BooleanField(default=False)

    class Meta:
        ordering = ['-final_payout', 'member__name']


class ChainAssignment(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='chain_assignments')
    assigned_slot_time = models.DateTimeField()
    chain_id = models.CharField(max_length=255)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['assigned_slot_time']
        indexes = [
            models.Index(fields=['chain_id', 'completed']),
        ]


class ChainBreakEvent(models.Model):
    chain_id = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    last_hit_time = models.DateTimeField(blank=True, null=True)
    expected_next_hit_by = models.DateTimeField(blank=True, null=True)
    suspected_member = models.ForeignKey(Member, on_delete=models.SET_NULL, blank=True, null=True, related_name='suspected_chain_breaks')
    slot_assignee = models.ForeignKey(Member, on_delete=models.SET_NULL, blank=True, null=True, related_name='assigned_chain_breaks')
    reason = models.CharField(max_length=255)
    chain_broken = models.BooleanField(default=False)
    time_remaining = models.IntegerField(blank=True, null=True)
    last_hitter_name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['chain_id', '-timestamp']),
        ]


class ReliabilityScore(models.Model):
    RISK_LEVEL_CHOICES = (
        ('highly_reliable', 'Highly Reliable'),
        ('stable', 'Stable'),
        ('at_risk', 'At Risk'),
        ('high_kick_risk', 'High Kick Risk'),
    )

    member = models.OneToOneField(Member, on_delete=models.CASCADE, related_name='reliability_score')
    activity_score = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    chain_score = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    war_score = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    oc_score = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    final_score = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    risk_level = models.CharField(max_length=32, choices=RISK_LEVEL_CHOICES, default='high_kick_risk')
    details = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-final_score', 'member__name']


class RankedWarPayout(models.Model):
    PAYOUT_MODE_CHOICES = (
        ('hits', 'Total Hits'),
        ('respect', 'Total Respect'),
    )

    war_id = models.CharField(max_length=64, db_index=True)
    total_pool = models.DecimalField(max_digits=16, decimal_places=2)
    faction_cut = models.DecimalField(max_digits=5, decimal_places=2)
    payout_mode = models.CharField(max_length=20, choices=PAYOUT_MODE_CHOICES)
    distributable_pool = models.DecimalField(max_digits=16, decimal_places=2)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ranked_war_payouts')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class RankedWarPayoutMember(models.Model):
    payout = models.ForeignKey(RankedWarPayout, on_delete=models.CASCADE, related_name='members')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='ranked_war_payout_rows')
    total_hits = models.IntegerField(default=0)
    total_respect = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    contribution_percentage = models.DecimalField(max_digits=7, decimal_places=4, default=0)
    payout_amount = models.DecimalField(max_digits=16, decimal_places=2, default=0)

    class Meta:
        ordering = ['-payout_amount', 'member__name']
        unique_together = ('payout', 'member')
