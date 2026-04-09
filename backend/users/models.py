from django.db import models
from django.contrib.auth.models import AbstractUser
class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('leader', 'Leader'),
        ('co-leader', 'Co-Leader'),
        ('officer', 'Officer'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='officer')
    def is_admin_or_leader(self):
        return self.role in ['admin', 'leader']
    def is_management(self):
        return self.role in ['admin', 'leader', 'co-leader']
