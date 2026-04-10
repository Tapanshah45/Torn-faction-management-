from rest_framework import viewsets, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Q
from .models import Member, Faction, ActivitySnapshot, OrganizedCrime
from .serializers import MemberSerializer, ActivitySnapshotSerializer, OrganizedCrimeSerializer
from .services import TornAPIService

class DashboardView(views.APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        service = TornAPIService()
        members_data = service.get_faction_members()
        
        # Try to get faction ID from API first
        faction_id = None
        if members_data and 'ID' in members_data:
            faction_id = members_data.get('ID')
            # Find the faction by torn_faction_id
            try:
                faction_obj = Faction.objects.get(torn_faction_id=faction_id)
                faction_id = faction_obj.id
            except Faction.DoesNotExist:
                faction_id = None
        
        # Fallback: get the most recent faction from the database
        if not faction_id:
            faction_obj = Faction.objects.order_by('-id').first()
            faction_id = faction_obj.id if faction_obj else None
        
        total_members = len(members_data.get('members', {})) if members_data else 0
        online_count = sum(1 for m in (members_data.get('members', {}) if members_data else {}).values() if m.get('last_action', {}).get('status') == 'Online')

        now = timezone.now()
        one_hour_ago = now - timedelta(hours=1)
        twenty_four_hours_ago = now - timedelta(hours=24)

        # Calculate active members filtered by faction (1h and 24h)
        if faction_id:
            active_1h = ActivitySnapshot.objects.filter(
                member__faction_id=faction_id,
                timestamp__gte=one_hour_ago
            ).values_list('member_id', flat=True).distinct().count()
            
            active_24h = ActivitySnapshot.objects.filter(
                member__faction_id=faction_id,
                timestamp__gte=twenty_four_hours_ago
            ).values_list('member_id', flat=True).distinct().count()
            
            inactive_members = Member.objects.filter(
                faction_id=faction_id,
                status='Inactive'
            ).count()
            
            ongoing_ocs = OrganizedCrime.objects.filter(
                member__faction_id=faction_id,
                timestamp__gte=twenty_four_hours_ago
            ).count()
        else:
            active_1h = active_24h = inactive_members = ongoing_ocs = 0

        # Get current chain info
        chain_data = service.get_chain_data()
        current_chain = chain_data.get('chain', {}).get('chain_id', 'None') if chain_data else 'None'

        # Get active war
        active_war = 'None'
        if members_data and 'ID' in members_data:
            try:
                war_data = service.get_war_data(faction_id=members_data.get('ID'))
                if war_data and 'rankedwars' in war_data:
                    wars = war_data.get('rankedwars', {})
                    if isinstance(wars, dict):
                        for war_id, war_info in wars.items():
                            if isinstance(war_info, dict) and war_info.get('status') == 'Active':
                                active_war = war_id
                                break
            except Exception:
                pass

        # Calculate respect gained today
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        respect_today = 0
        try:
            from leadership.models import RankedWarPayout
            recent_payouts = RankedWarPayout.objects.filter(created_at__gte=today_start)
            if recent_payouts:
                respect_today = int(sum(float(p.total_pool) for p in recent_payouts))
        except Exception:
            respect_today = 0

        return Response({
            "total_members": total_members,
            "online_members": online_count,
            "active_1h": active_1h,
            "active_24h": active_24h,
            "current_chain": current_chain,
            "active_war": active_war,
            "respect_today": respect_today,
            "inactive_members": inactive_members,
            "ongoing_ocs": ongoing_ocs
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

        # Exclude inactive members from the active roster
        queryset = queryset.exclude(status='Inactive')

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
