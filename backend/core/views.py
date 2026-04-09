from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Alert
from .serializers import AlertSerializer
class AlertViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Alert.objects.all().order_by('-created_at')
    serializer_class = AlertSerializer
