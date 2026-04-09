from rest_framework import serializers
from .models import Alert
from torn.serializers import MemberSerializer
class AlertSerializer(serializers.ModelSerializer):
    member_detail = MemberSerializer(source='member', read_only=True)
    class Meta:
        model = Alert
        fields = '__all__'
