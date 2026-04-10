from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from torn.models import ActivitySnapshot, ChainLog, Faction, Member, OrganizedCrime, WarLog

from .models import ChainAssignment, ChainBreakEvent, RankedWarPayout, RankedWarPayoutMember, ReliabilityScore
from .services import ChainBreakDetectionService, ReliabilityScoringService
from .services.payout_service import RankedWarPayoutService


User = get_user_model()


class LeadershipApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='leader', password='pass', role='leader')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.faction = Faction.objects.create(torn_faction_id=123, name='Test Faction')
        self.member_one = Member.objects.create(
            faction=self.faction,
            torn_player_id=1001,
            name='Alpha',
            level=100,
            faction_rank='Leader',
            status='Online',
            last_action=timezone.now() - timedelta(hours=2),
        )
        self.member_two = Member.objects.create(
            faction=self.faction,
            torn_player_id=1002,
            name='Bravo',
            level=90,
            faction_rank='Member',
            status='Offline',
            last_action=timezone.now() - timedelta(hours=30),
        )
        ActivitySnapshot.objects.create(member=self.member_one, online_status='online')
        ActivitySnapshot.objects.create(member=self.member_two, online_status='offline')
        ChainLog.objects.create(member=self.member_one, hits=8, respect_gain=20, chain_id='chain-1')
        ChainLog.objects.create(member=self.member_two, hits=2, respect_gain=5, chain_id='chain-1')
        WarLog.objects.create(member=self.member_one, war_id='rw-101', attacks_won=100, attacks_lost=10, assists=1, respect_gain=Decimal('500.00'))
        WarLog.objects.create(member=self.member_two, war_id='rw-101', attacks_won=50, attacks_lost=3, assists=1, respect_gain=Decimal('250.00'))
        OrganizedCrime.objects.create(member=self.member_one, crime_name='OC 1', role='Shooter', success=True)
        OrganizedCrime.objects.create(member=self.member_two, crime_name='OC 2', role='Driver', success=False)

    def test_calculate_payouts_by_hits(self):
        response = self.client.post(
            '/api/payouts/calculate',
            {
                'war_id': 'rw-101',
                'total_pool': '1000.00',
                'faction_cut': '10.00',
                'payout_mode': 'hits',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(RankedWarPayout.objects.count(), 1)
        self.assertEqual(len(response.data['members']), 2)
        self.assertEqual(response.data['distributable_pool'], '900.00')

    def test_calculate_payouts_by_respect(self):
        response = self.client.post(
            '/api/payouts/calculate',
            {
                'war_id': 'rw-101',
                'total_pool': '600000000.00',
                'faction_cut': '10.00',
                'payout_mode': 'respect',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        rows = sorted(response.data['members'], key=lambda row: row['name'])
        self.assertEqual(rows[0]['name'], 'Alpha')
        self.assertEqual(Decimal(rows[0]['payout']), Decimal('360000000.00'))
        self.assertEqual(rows[1]['name'], 'Bravo')
        self.assertEqual(Decimal(rows[1]['payout']), Decimal('180000000.00'))

    def test_war_contributions_endpoint(self):
        response = self.client.get('/api/payouts/war-contributions/rw-101')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['war_id'], 'rw-101')
        self.assertEqual(len(response.data['members']), 2)

    def test_reliability_list(self):
        ReliabilityScoringService().recalculate_all()
        response = self.client.get('/api/reliability')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_chain_slot_assignment(self):
        response = self.client.post(
            '/api/chains/assign-slot',
            {
                'member_id': self.member_one.id,
                'assigned_slot_time': timezone.now().isoformat(),
                'chain_id': 'chain-1',
                'completed': False,
            },
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(ChainAssignment.objects.count(), 1)


class LeadershipServiceTests(TestCase):
    def setUp(self):
        self.faction = Faction.objects.create(torn_faction_id=456, name='Service Faction')
        self.member = Member.objects.create(
            faction=self.faction,
            torn_player_id=2001,
            name='ServiceMember',
            level=100,
            faction_rank='Leader',
            status='Online',
            last_action=timezone.now() - timedelta(hours=1),
        )

    def test_chain_break_detection_creates_event(self):
        ChainAssignment.objects.create(
            member=self.member,
            assigned_slot_time=timezone.now() - timedelta(seconds=40),
            chain_id='chain-x',
            completed=False,
        )
        event = ChainBreakDetectionService().evaluate({'chain_id': 'chain-x', 'time_remaining': 15, 'last_hit_member': 'ServiceMember'})
        self.assertIsNotNone(event)
        self.assertTrue(ChainBreakEvent.objects.filter(chain_id='chain-x').exists())

    def test_reliability_scoring_creates_score(self):
        score = ReliabilityScoringService().recalculate_member(self.member)
        self.assertTrue(ReliabilityScore.objects.filter(member=self.member).exists())
        self.assertGreaterEqual(float(score.final_score), 0)


class RankedWarPayoutServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='leader2', password='pass', role='leader')
        self.faction = Faction.objects.create(torn_faction_id=789, name='Payout Faction')
        self.member_one = Member.objects.create(
            faction=self.faction,
            torn_player_id=3001,
            name='A',
            level=80,
            faction_rank='Member',
            status='Online',
        )
        self.member_two = Member.objects.create(
            faction=self.faction,
            torn_player_id=3002,
            name='B',
            level=78,
            faction_rank='Member',
            status='Online',
        )
        WarLog.objects.create(member=self.member_one, war_id='rw-202', attacks_won=100, respect_gain=Decimal('500.00'))
        WarLog.objects.create(member=self.member_two, war_id='rw-202', attacks_won=50, respect_gain=Decimal('250.00'))

    def test_aggregation_logic(self):
        rows = RankedWarPayoutService().get_war_contributions('rw-202')
        self.assertEqual(len(rows), 2)
        first = rows[0]
        self.assertIn(first.member_name, {'A', 'B'})

    def test_faction_cut_calculation(self):
        result = RankedWarPayoutService().generate_rw_payout(
            war_id='rw-202',
            total_pool=Decimal('600000000.00'),
            faction_cut=Decimal('10.00'),
            payout_mode='hits',
            created_by=self.user,
        )
        self.assertEqual(result.payout.distributable_pool, Decimal('540000000.00'))

    def test_payout_distribution_by_hits(self):
        RankedWarPayoutService().generate_rw_payout(
            war_id='rw-202',
            total_pool=Decimal('600000000.00'),
            faction_cut=Decimal('10.00'),
            payout_mode='hits',
            created_by=self.user,
        )
        rows = RankedWarPayoutMember.objects.order_by('member__name')
        self.assertEqual(rows.count(), 2)
        self.assertEqual(rows[0].member.name, 'A')
        self.assertEqual(rows[0].payout_amount, Decimal('360000000.00'))
        self.assertEqual(rows[1].member.name, 'B')
        self.assertEqual(rows[1].payout_amount, Decimal('180000000.00'))
