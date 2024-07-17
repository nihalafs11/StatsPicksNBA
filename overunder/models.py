from django.db import models

class TeamData(models.Model):
    team_name = models.CharField(max_length=100, unique=True)
    team_input = models.CharField(max_length=100, unique=True)
    abbreviation = models.CharField(max_length=100, unique=True)
    logo = models.CharField(max_length=255)  # Assuming you'll store the path to the SVG file

    class Meta:
        verbose_name = "Team Data"  # Singular name for the model
        verbose_name_plural = "Team Data"  # Plural name for the model

    def __str__(self):
        return self.team_name

