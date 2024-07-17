from django.db import models

class Players(models.Model):
    name = models.CharField(max_length=100)
    team = models.CharField(max_length=100)
    picture = models.URLField(max_length=255)

    class Meta:
        verbose_name = "Player Data"  
        verbose_name_plural = "Player Data"  

    def __str__(self):
        return f"{self.name} ({self.team})"

