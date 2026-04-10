#!/usr/bin/env python
"""
Test script to validate dashboard features:
- active_1h: Members active in last 1 hour
- active_24h: Members active in last 24 hours
- current_chain: Current chain ID
- active_war: Active war ID
- respect_today: Respect gained today
- inactive_members: Count of inactive members
- ongoing_ocs: Organized crimes in last 24 hours
"""

import os
import sys
import django

sys.path.append(os.path.join(os.path.dirname(__file__), '.'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from torn.models import Member, Faction, ActivitySnapshot, OrganizedCrime
from leadership.models import RankedWarPayout

User = get_user_model()

def cleanup_test_data():
    """Remove test data from previous runs"""
    User.objects.filter(username='test_leader').delete()
    Member.objects.filter(torn_player_id__in=[9001, 9002, 9003, 9004]).delete()
    Faction.objects.filter(torn_faction_id=99999).delete()
    OrganizedCrime.objects.filter(crime_name__in=['Fraud Ring', 'Political Assassination']).delete()
    RankedWarPayout.objects.filter(war_id='test-war-001').delete()
    print("✓ Cleaned up previous test data")

def create_test_faction_and_members():
    """Create test faction and members with varied activity"""
    from torn.models import ActivitySnapshot
    
    faction = Faction.objects.create(
        torn_faction_id=99999,
        name='Test Faction for Dashboard',
        total_respect=100000
    )
    
    now = timezone.now()
    
    # Member 1: Active in last 1 hour
    member1 = Member.objects.create(
        faction=faction,
        torn_player_id=9001,
        name='ActiveMember1h',
        level=100,
        faction_rank='Admin',
        status='Online',
        last_action=now - timedelta(minutes=30)
    )
    # Create snapshot within 1h
    snap1 = ActivitySnapshot.objects.create(
        member=member1,
        online_status='online',
        chain_hits=5,
        respect=100,
        war_hits=10
    )
    ActivitySnapshot.objects.filter(id=snap1.id).update(timestamp=now - timedelta(minutes=30))
    
    # Member 2: Active in 24h but not in 1h
    member2 = Member.objects.create(
        faction=faction,
        torn_player_id=9002,
        name='ActiveMember24h',
        level=95,
        faction_rank='Member',
        status='Offline',
        last_action=now - timedelta(hours=5)
    )
    # Create snapshot OUTSIDE 1h but within 24h
    snap2 = ActivitySnapshot.objects.create(
        member=member2,
        online_status='offline',
        chain_hits=3,
        respect=50,
        war_hits=5
    )
    ActivitySnapshot.objects.filter(id=snap2.id).update(timestamp=now - timedelta(hours=5))
    
    # Member 3: Inactive (no activity in 24h)
    member3 = Member.objects.create(
        faction=faction,
        torn_player_id=9003,
        name='Inactive Member',
        level=80,
        faction_rank='Member',
        status='Inactive',
        last_action=now - timedelta(hours=48)
    )
    
    # Member 4: Just inactive status marker
    member4 = Member.objects.create(
        faction=faction,
        torn_player_id=9004,
        name='MarkedInactive',
        level=75,
        faction_rank='Member',
        status='Inactive',
        last_action=now - timedelta(hours=72)
    )
    
    print(f"✓ Created test faction: {faction.name} (ID: {faction.torn_faction_id})")
    print(f"  - Member 1 (9001): Active 30 min ago (snapshot timestamped 30 min ago)")
    print(f"  - Member 2 (9002): Active 5 hours ago (snapshot timestamped 5 hours ago)")
    print(f"  - Member 3 (9003): Inactive, 48 hours ago (no recent activity)")
    print(f"  - Member 4 (9004): Marked Inactive, 72 hours ago (no recent activity)")
    
    return faction, [member1, member2, member3, member4]

def create_test_ocs(faction, members):
    """Create test organized crimes"""
    now = timezone.now()
    twenty_four_hours_ago = now - timedelta(hours=24)
    
    # Recent OC (within 24h)
    oc1 = OrganizedCrime.objects.create(
        member=members[0],
        crime_name='Fraud Ring',
        role='Setter',
        success=True
    )
    
    # Another recent OC
    oc2 = OrganizedCrime.objects.create(
        member=members[1],
        crime_name='Political Assassination',
        role='Shooter',
        success=True
    )
    
    print(f"✓ Created {2} organized crimes in last 24 hours")
    
    return [oc1, oc2]

def create_test_war_payout(faction, now):
    """Create test war payout for respect_today calculation"""
    from django.contrib.auth import get_user_model
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    User = get_user_model()
    admin_user = User.objects.filter(username='test_leader').first()
    
    payout = RankedWarPayout.objects.create(
        war_id='test-war-001',
        payout_mode='hits',
        total_pool=5000000,
        faction_cut=10,
        distributable_pool=4500000,
        created_by=admin_user
    )
    
    print(f"✓ Created test payout: {payout.total_pool} respect pool")
    
    return payout

def run_dashboard_test():
    """Test the dashboard API endpoint"""
    # Create admin user
    user = User.objects.create_user(
        username='test_leader',
        password='testpass',
        role='leader'
    )
    
    # Create test data
    faction, members = create_test_faction_and_members()
    ocs = create_test_ocs(faction, members)
    now = timezone.now()
    payout = create_test_war_payout(faction, now)
    
    # Verify data was created
    print("\n" + "="*60)
    print("DATA VERIFICATION")
    print("="*60)
    print(f"Faction in DB: {faction.id} - {faction.name}")
    print(f"Members in faction: {faction.members.count()}")
    print(f"Activity Snapshots in faction: {ActivitySnapshot.objects.filter(member__faction=faction).count()}")
    print(f"OCs in faction: {ocs}" )
    
    # Make API request
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get('/api/dashboard/')
    
    print("\n" + "="*60)
    print("DASHBOARD API RESPONSE")
    print("="*60)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Status 200 OK\n")
        print(f"Total Members:      {data['total_members']}")
        print(f"Online Members:     {data['online_members']}")
        print(f"Active (1h):        {data['active_1h']} (expected: 1)")
        print(f"Active (24h):       {data['active_24h']} (expected: 2)")
        print(f"Current Chain:      {data['current_chain']}")
        print(f"Active War:         {data['active_war']}")
        print(f"Respect Today:      {data['respect_today']}")
        print(f"Inactive Members:   {data['inactive_members']} (expected: 2)")
        print(f"Ongoing OCs:        {data['ongoing_ocs']} (expected: 2)")
        
        # Validation
        print("\n" + "="*60)
        print("VALIDATION RESULTS")
        print("="*60)
        
        tests = [
            ("active_1h == 1", data['active_1h'] == 1),
            ("active_24h == 2", data['active_24h'] == 2),
            ("inactive_members >= 2", data['inactive_members'] >= 2),
            ("ongoing_ocs == 2", data['ongoing_ocs'] == 2),
            ("respect_today > 0", data['respect_today'] > 0),
        ]
        
        passed = 0
        for test_name, result in tests:
            status = "✓" if result else "✗"
            print(f"{status} {test_name}")
            if result:
                passed += 1
        
        print(f"\n{passed}/{len(tests)} tests passed")
        
    else:
        print(f"✗ Status {response.status_code}: {response.content}")
        return False
    
    # Cleanup
    cleanup_test_data()
    return True

if __name__ == '__main__':
    print("Testing Dashboard Features...")
    print("="*60)
    cleanup_test_data()
    success = run_dashboard_test()
    sys.exit(0 if success else 1)
