from rest_framework import serializers

from torn.serializers import MemberSerializer

from .models import (
    ChainAssignment,
    ChainBreakEvent,
    RankedWarPayout,
    RankedWarPayoutMember,
    ReliabilityScore,
)


class RankedWarPayoutCalculateSerializer(serializers.Serializer):
    war_id = serializers.CharField(max_length=64)
    total_pool = serializers.DecimalField(max_digits=16, decimal_places=2)
    faction_cut = serializers.DecimalField(max_digits=5, decimal_places=2)
    payout_mode = serializers.ChoiceField(choices=RankedWarPayout.PAYOUT_MODE_CHOICES)

    def validate_total_pool(self, value):
        if value <= 0:
            raise serializers.ValidationError('Total pool must be greater than zero.')
        return value

    def validate_faction_cut(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError('Faction cut must be between 0 and 100.')
        return value


class RankedWarPayoutMemberSerializer(serializers.ModelSerializer):
    member_detail = MemberSerializer(source='member', read_only=True)
    name = serializers.CharField(source='member.name', read_only=True)
    hits = serializers.IntegerField(source='total_hits', read_only=True)
    respect = serializers.DecimalField(source='total_respect', max_digits=12, decimal_places=2, read_only=True)
    share_percent = serializers.DecimalField(source='contribution_percentage', max_digits=7, decimal_places=4, read_only=True)
    payout = serializers.DecimalField(source='payout_amount', max_digits=16, decimal_places=2, read_only=True)

    class Meta:
        model = RankedWarPayoutMember
        fields = (
            'id',
            'member',
            'member_detail',
            'name',
            'hits',
            'respect',
            'share_percent',
            'payout',
            'total_hits',
            'total_respect',
            'contribution_percentage',
            'payout_amount',
        )


class RankedWarPayoutSerializer(serializers.ModelSerializer):
    members = RankedWarPayoutMemberSerializer(many=True, read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    mode = serializers.CharField(source='payout_mode', read_only=True)

    class Meta:
        model = RankedWarPayout
        fields = (
            'id',
            'war_id',
            'mode',
            'total_pool',
            'faction_cut',
            'distributable_pool',
            'payout_mode',
            'created_by',
            'created_by_username',
            'created_at',
            'members',
        )


class RankedWarContributionSerializer(serializers.Serializer):
    member_id = serializers.IntegerField()
    member_name = serializers.CharField()
    total_hits = serializers.IntegerField()
    total_respect = serializers.DecimalField(max_digits=12, decimal_places=2)


class RankedWarListSerializer(serializers.Serializer):
    war_id = serializers.CharField()
    participants = serializers.IntegerField()
    total_hits = serializers.IntegerField()
    total_respect = serializers.DecimalField(max_digits=12, decimal_places=2)
    is_active = serializers.BooleanField()
    last_timestamp = serializers.DateTimeField(allow_null=True)


class ChainAssignmentSerializer(serializers.ModelSerializer):
    member_detail = MemberSerializer(source='member', read_only=True)

    class Meta:
        model = ChainAssignment
        fields = ('id', 'member', 'member_detail', 'assigned_slot_time', 'chain_id', 'completed', 'completed_at')


class ChainBreakEventSerializer(serializers.ModelSerializer):
    suspected_member_detail = MemberSerializer(source='suspected_member', read_only=True)
    slot_assignee_detail = MemberSerializer(source='slot_assignee', read_only=True)

    class Meta:
        model = ChainBreakEvent
        fields = ('id', 'chain_id', 'timestamp', 'last_hit_time', 'expected_next_hit_by', 'suspected_member', 'suspected_member_detail', 'slot_assignee', 'slot_assignee_detail', 'reason', 'chain_broken', 'time_remaining', 'last_hitter_name')


class ReliabilityScoreSerializer(serializers.ModelSerializer):
    member_detail = MemberSerializer(source='member', read_only=True)

    class Meta:
        model = ReliabilityScore
        fields = ('id', 'member', 'member_detail', 'activity_score', 'chain_score', 'war_score', 'oc_score', 'final_score', 'risk_level', 'details', 'updated_at')
