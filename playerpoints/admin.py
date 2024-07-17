from django.contrib import admin
from .models import Players

class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'team', 'picture') 

admin.site.register(Players, PlayerAdmin)
