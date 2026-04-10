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

    # Ensure admin user exists and has expected credentials for local setup.
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'role': 'admin',
            'is_staff': True,
            'is_superuser': True,
        },
    )
    admin_user.set_password('pass')
    admin_user.role = 'admin'
    admin_user.email = admin_user.email or 'admin@example.com'
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.save(update_fields=['password', 'role', 'email', 'is_staff', 'is_superuser'])
    if created:
        print("Created admin user.")
    else:
        print("Updated admin user password.")

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
        WarLog.objects.get_or_create(member=m, war_id='rw-seed-001', attacks_won=10, attacks_lost=2, assists=5, respect_gain=30.0)

        # Create OC
        OrganizedCrime.objects.get_or_create(member=m, crime_name='Political Assassination', role='Shooter', success=True)

    print("Seed complete.")

if __name__ == '__main__':
    run()
