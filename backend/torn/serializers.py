from rest_framework import serializers
from .models import Faction, Member, ActivitySnapshot, ChainLog, WarLog, OrganizedCrime
class FactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faction
        fields = '__all__'
class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = '__all__'
class ActivitySnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivitySnapshot
        fields = '__all__'
class ChainLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChainLog
        fields = '__all__'
class WarLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = WarLog
        fields = '__all__'
class OrganizedCrimeSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source='member.name', read_only=True)
    class Meta:
        model = OrganizedCrime
        fields = '__all__'
