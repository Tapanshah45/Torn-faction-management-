from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DashboardView, LiveChainView, WarAnalyticsView, MemberViewSet, AnalyticsHistoryView, OrganizedCrimeViewSet
router = DefaultRouter()
router.register(r'members', MemberViewSet, basename='member')
router.register(r'organized-crimes', OrganizedCrimeViewSet, basename='organized-crime')
urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('chains/live/', LiveChainView.as_view(), name='live-chain'),
    path('wars/', WarAnalyticsView.as_view(), name='wars'),
    path('analytics/history/', AnalyticsHistoryView.as_view(), name='analytics-history'),
]
