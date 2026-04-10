from django.db import models
class Faction(models.Model):
    torn_faction_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    total_respect = models.IntegerField(default=0)
    leader_name = models.CharField(max_length=255, blank=True, null=True)
    def __str__(self):
        return f"{self.name} [{self.torn_faction_id}]"

class Member(models.Model):
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE, related_name='members')
    torn_player_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    level = models.IntegerField(default=0)
    faction_rank = models.CharField(max_length=100)
    status = models.CharField(max_length=255, blank=True, null=True)
    last_action = models.DateTimeField(blank=True, null=True)
    class Meta:
        indexes = [
            models.Index(fields=['torn_player_id']),
            models.Index(fields=['faction']),
        ]
    def __str__(self):
        return f"{self.name} [{self.torn_player_id}]"

class ActivitySnapshot(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='snapshots')
    timestamp = models.DateTimeField(auto_now_add=True)
    online_status = models.CharField(max_length=50)
    chain_hits = models.IntegerField(default=0)
    respect = models.IntegerField(default=0)
    war_hits = models.IntegerField(default=0)
    class Meta:
        indexes = [
            models.Index(fields=['member', 'timestamp']),
            models.Index(fields=['timestamp']),
        ]

class ChainLog(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='chain_logs')
    timestamp = models.DateTimeField(auto_now_add=True)
    hits = models.IntegerField(default=0)
    respect_gain = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    chain_id = models.CharField(max_length=255, blank=True, null=True)
    class Meta:
        indexes = [
            models.Index(fields=['member', 'chain_id']),
        ]

class WarLog(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='war_logs')
    war_id = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    attacks_won = models.IntegerField(default=0)
    attacks_lost = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)
    respect_gain = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    class Meta:
        indexes = [
            models.Index(fields=['member']),
        ]

class OrganizedCrime(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='organized_crimes')
    crime_name = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    success = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    class Meta:
        indexes = [
            models.Index(fields=['member']),
        ]
