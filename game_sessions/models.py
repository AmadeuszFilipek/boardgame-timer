import time
from django.db import models

class GameSession(models.Model):
    slug = models.CharField(max_length=100, unique=True)
    version = models.FloatField(default=time.time)
    timer_type = models.CharField(max_length=50)
    seconds = models.IntegerField()
    auto_pass = models.BooleanField(default=False)
    active_player_name = models.CharField(max_length=100, null=True, blank=True)
    any_timer_active = models.BooleanField(default=False)

    def __str__(self):
        return self.slug

class Player(models.Model):
    game_session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='players')
    name = models.CharField(max_length=100)
    player_id = models.IntegerField()
    timer_state = models.JSONField()

    def __str__(self):
        return f"{self.name} in {self.game_session.slug}"
