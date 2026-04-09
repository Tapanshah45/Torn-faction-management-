from django.db import models
from torn.models import Member
class Alert(models.Model):
    SEVERITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    )
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=100)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium')
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)
    class Meta:
        indexes = [
            models.Index(fields=['member', 'resolved']),
        ]
    def __str__(self):
        return f"{self.alert_type} for {self.member.name} ({self.severity})"
