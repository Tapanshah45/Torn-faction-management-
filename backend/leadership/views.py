from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from torn.models import Member

from .models import ChainAssignment, ChainBreakEvent, RankedWarPayout, ReliabilityScore
from .serializers import (
    ChainAssignmentSerializer,
    ChainBreakEventSerializer,
    RankedWarContributionSerializer,
    RankedWarListSerializer,
    RankedWarPayoutCalculateSerializer,
    RankedWarPayoutSerializer,
    ReliabilityScoreSerializer,
)
from .services import ReliabilityScoringService, generate_rw_payout
from .services.payout_service import RankedWarPayoutError, RankedWarPayoutService


class PayoutCalculateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RankedWarPayoutCalculateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            result = generate_rw_payout(created_by=request.user, **serializer.validated_data)
        except RankedWarPayoutError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        payload = RankedWarPayoutSerializer(result.payout, context={'request': request}).data
        return Response(payload, status=status.HTTP_201_CREATED)


class PayoutHistoryView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RankedWarPayoutSerializer
    queryset = RankedWarPayout.objects.prefetch_related('members', 'members__member', 'created_by').all()


class PayoutDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RankedWarPayoutSerializer
    queryset = RankedWarPayout.objects.prefetch_related('members', 'members__member', 'created_by').all()


class RankedWarListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wars = RankedWarPayoutService().list_ranked_wars()
        serializer = RankedWarListSerializer(wars, many=True)
        return Response(serializer.data)


class WarContributionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, war_id: str):
        service = RankedWarPayoutService()
        try:
            rows = service.get_war_contributions(war_id)
        except RankedWarPayoutError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_404_NOT_FOUND)

        serializer = RankedWarContributionSerializer(rows, many=True)
        return Response({'war_id': war_id, 'members': serializer.data})


class ChainBreakEventListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChainBreakEventSerializer
    queryset = ChainBreakEvent.objects.select_related('suspected_member', 'slot_assignee').all()


class ChainLiveStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        latest = ChainBreakEvent.objects.order_by('-timestamp').first()
        return Response({
            'latest_event': ChainBreakEventSerializer(latest).data if latest else None,
            'chain_id': latest.chain_id if latest else None,
            'chain_broken': latest.chain_broken if latest else False,
        })


class ChainAssignSlotView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        member = get_object_or_404(Member, pk=request.data.get('member_id'))
        payload = request.data.copy()
        payload['member'] = member.id
        serializer = ChainAssignmentSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        assignment = ChainAssignment.objects.create(
            member=member,
            assigned_slot_time=serializer.validated_data['assigned_slot_time'],
            chain_id=serializer.validated_data['chain_id'],
            completed=serializer.validated_data.get('completed', False),
            completed_at=serializer.validated_data.get('completed_at'),
        )
        return Response(ChainAssignmentSerializer(assignment).data, status=status.HTTP_201_CREATED)


class ReliabilityListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReliabilityScoreSerializer
    
    def get_queryset(self):
        # Only show reliability scores for active members (not marked Inactive)
        return ReliabilityScore.objects.select_related('member').exclude(member__status='Inactive')


class ReliabilityDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReliabilityScoreSerializer
    queryset = ReliabilityScore.objects.select_related('member').all()
    lookup_field = 'member_id'
    lookup_url_kwarg = 'member_id'

    def get_object(self):
        member = get_object_or_404(Member, pk=self.kwargs['member_id'])
        score, _ = ReliabilityScore.objects.get_or_create(member=member)
        return score
