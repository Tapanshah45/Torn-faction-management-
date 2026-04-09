from django.db import models
class NotificationSettings(models.Model):
    discord_webhook_url = models.URLField(blank=True, null=True)
    telegram_bot_token = models.CharField(max_length=255, blank=True, null=True)
    telegram_chat_id = models.CharField(max_length=255, blank=True, null=True)
    notify_inactivity = models.BooleanField(default=False)
    notify_chain_drops = models.BooleanField(default=False)
    notify_war_hits = models.BooleanField(default=False)
    def __str__(self):
        return "Global Notification Settings"
