from django.urls import path

from .views import (
    ChainAssignSlotView,
    ChainBreakEventListView,
    ChainLiveStatusView,
    PayoutCalculateView,
    PayoutDetailView,
    PayoutHistoryView,
    RankedWarListView,
    ReliabilityDetailView,
    ReliabilityListView,
    WarContributionView,
)

urlpatterns = [
    path('payouts/wars', RankedWarListView.as_view(), name='payout-wars'),
    path('payouts/calculate', PayoutCalculateView.as_view(), name='payout-calculate'),
    path('payouts/history', PayoutHistoryView.as_view(), name='payout-history'),
    path('payouts/war-contributions/<str:war_id>', WarContributionView.as_view(), name='payout-war-contributions'),
    path('payouts/<int:pk>', PayoutDetailView.as_view(), name='payout-detail'),
    path('chains/break-events', ChainBreakEventListView.as_view(), name='chain-break-events'),
    path('chains/live-status', ChainLiveStatusView.as_view(), name='chain-live-status'),
    path('chains/assign-slot', ChainAssignSlotView.as_view(), name='chain-assign-slot'),
    path('reliability', ReliabilityListView.as_view(), name='reliability-list'),
    path('reliability/<int:member_id>', ReliabilityDetailView.as_view(), name='reliability-detail'),
]
