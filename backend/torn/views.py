from rest_framework import viewsets, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Member, ActivitySnapshot, OrganizedCrime
from .serializers import MemberSerializer, ActivitySnapshotSerializer, OrganizedCrimeSerializer
from .services import TornAPIService

class DashboardView(views.APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        service = TornAPIService()
        members_data = service.get_faction_members()
        total_members = len(members_data.get('members', {})) if members_data else 0
        online_count = sum(1 for m in (members_data.get('members', {}) if members_data else {}).values() if m.get('last_action', {}).get('status') == 'Online')

        return Response({
            "total_members": total_members,
            "online_members": online_count,
            "active_1h": "N/A",
            "active_24h": "N/A",
            "current_chain": "Active",
            "active_war": "None",
            "respect_today": 0,
            "inactive_members": 0,
            "ongoing_ocs": 0
        })

class LiveChainView(views.APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        service = TornAPIService()
        data = service.get_chain_data()
        return Response(data.get('chain', {}) if data else {})

class WarAnalyticsView(views.APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        service = TornAPIService()
        data = service.get_war_data()
        return Response(data if data else {})

class MemberViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = MemberSerializer

    def get_queryset(self):
        service = TornAPIService()
        data = service.get_faction_members()
        faction_id = data.get('ID') if data else None

        queryset = Member.objects.all()
        if faction_id:
            queryset = queryset.filter(faction__torn_faction_id=faction_id)

        return queryset.order_by('name')

class OrganizedCrimeViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrganizedCrimeSerializer

    def get_queryset(self):
        service = TornAPIService()
        data = service.get_faction_members()
        faction_id = data.get('ID') if data else None

        queryset = OrganizedCrime.objects.select_related('member', 'member__faction').order_by('-timestamp')
        if faction_id:
            queryset = queryset.filter(member__faction__torn_faction_id=faction_id)
        else:
            queryset = queryset.none()

        return queryset

class AnalyticsHistoryView(views.APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response({"history": []})
