from django.contrib import admin
from .models import TeamData

class TeamDataAdmin(admin.ModelAdmin):
    list_display = ('team_name', 'team_input', 'abbreviation', 'logo')  # Columns to display
    search_fields = ('team_name', 'team_input')  # Fields to search by

admin.site.register(TeamData, TeamDataAdmin)
