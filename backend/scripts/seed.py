import os
import sys
import django

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import User
from torn.models import Faction, Member, ChainLog, WarLog, OrganizedCrime
from django.utils import timezone

def run():
    print("Seeding database...")

    # Create superuser
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'adminpass', role='admin')
        print("Created admin user.")

    # Create Faction
    faction, _ = Faction.objects.get_or_create(
        torn_faction_id=12345,
        defaults={'name': 'The Vanguard', 'total_respect': 1500000, 'leader_name': 'AlphaLead'}
    )

    # Create Members
    members_data = [
        {'id': 1001, 'name': 'AlphaLead', 'level': 100, 'rank': 'Leader', 'status': 'Online'},
        {'id': 1002, 'name': 'BravoCo', 'level': 85, 'rank': 'Co-Leader', 'status': 'Offline'},
        {'id': 1003, 'name': 'CharlieHit', 'level': 50, 'rank': 'Member', 'status': 'Online'},
    ]

    for md in members_data:
        m, _ = Member.objects.update_or_create(
            torn_player_id=md['id'],
            defaults={
                'name': md['name'],
                'level': md['level'],
                'faction_rank': md['rank'],
                'status': md['status'],
                'faction': faction,
                'last_action': timezone.now()
            }
        )

        # Create Chain Logs
        ChainLog.objects.get_or_create(member=m, hits=15, respect_gain=45.5, chain_id="9999")

        # Create War Logs
        WarLog.objects.get_or_create(member=m, attacks_won=10, attacks_lost=2, assists=5, respect_gain=30.0)

        # Create OC
        OrganizedCrime.objects.get_or_create(member=m, crime_name='Political Assassination', role='Shooter', success=True)

    print("Seed complete.")

if __name__ == '__main__':
    run()
