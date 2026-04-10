from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Faction, Member, OrganizedCrime
from .tasks import sync_organized_crimes


User = get_user_model()


class OrganizedCrimeViewSetTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='pass', role='leader')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.live_faction = Faction.objects.create(torn_faction_id=54815, name='Live Faction')
        self.stale_faction = Faction.objects.create(torn_faction_id=12345, name='Stale Faction')

        self.live_member = Member.objects.create(
            faction=self.live_faction,
            torn_player_id=9001,
            name='Live Member',
            level=90,
            faction_rank='Member',
        )
        self.stale_member = Member.objects.create(
            faction=self.stale_faction,
            torn_player_id=9002,
            name='Stale Member',
            level=75,
            faction_rank='Member',
        )

        OrganizedCrime.objects.create(member=self.live_member, crime_name='Live OC', role='Hacker', success=True)
        OrganizedCrime.objects.create(member=self.stale_member, crime_name='Stale OC', role='Driver', success=False)

    @patch('torn.views.TornAPIService.get_faction_members')
    def test_returns_only_live_faction_crimes(self, mocked_faction_members):
        mocked_faction_members.return_value = {'ID': self.live_faction.torn_faction_id}

        response = self.client.get('/api/organized-crimes/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['crime_name'], 'Live OC')
        self.assertEqual(response.data[0]['member_name'], 'Live Member')

    @patch('torn.views.TornAPIService.get_faction_members')
    def test_returns_empty_when_live_faction_unavailable(self, mocked_faction_members):
        mocked_faction_members.return_value = {}

        response = self.client.get('/api/organized-crimes/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)


class OrganizedCrimeSyncTaskTests(TestCase):
    def setUp(self):
        self.faction = Faction.objects.create(torn_faction_id=54815, name='Live Faction')
        self.member = Member.objects.create(
            faction=self.faction,
            torn_player_id=1001,
            name='Alpha',
            level=90,
            faction_rank='Member',
        )

    @patch('torn.tasks.TornAPIService.get_organized_crimes_data')
    @patch('torn.tasks.TornAPIService.get_faction_members')
    def test_sync_organized_crimes_creates_rows(self, mocked_faction_members, mocked_crimes_data):
        mocked_faction_members.return_value = {'ID': 54815}
        mocked_crimes_data.return_value = {
            'crimes': {
                '11': {
                    'crime_name': 'Political Assassination',
                    'success': True,
                    'participants': [
                        {'user_id': 1001, 'position': 'Sniper'},
                    ],
                },
            },
        }

        result = sync_organized_crimes()

        self.assertEqual(result['synced'], 1)
        self.assertEqual(OrganizedCrime.objects.count(), 1)
        row = OrganizedCrime.objects.first()
        self.assertEqual(row.crime_name, 'Political Assassination')
        self.assertEqual(row.role, 'Sniper')
        self.assertTrue(row.success)

    @patch('torn.tasks.TornAPIService.get_organized_crimes_data')
    @patch('torn.tasks.TornAPIService.get_faction_members')
    def test_sync_organized_crimes_replaces_stale_rows(self, mocked_faction_members, mocked_crimes_data):
        OrganizedCrime.objects.create(member=self.member, crime_name='Old Crime', role='Old Role', success=False)

        mocked_faction_members.return_value = {'ID': 54815}
        mocked_crimes_data.return_value = {
            'crimes': {
                '12': {
                    'name': 'Cyber Heist',
                    'result': 'success',
                    'slots': {
                        'a': {'user': {'ID': 1001}, 'role': 'Hacker'},
                    },
                },
            },
        }

        result = sync_organized_crimes()

        self.assertEqual(result['synced'], 1)
        self.assertEqual(OrganizedCrime.objects.count(), 1)
        row = OrganizedCrime.objects.first()
        self.assertEqual(row.crime_name, 'Cyber Heist')
        self.assertEqual(row.role, 'Hacker')
        self.assertTrue(row.success)
