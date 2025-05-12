from django.contrib import admin
from .models import Major

@admin.register(Major)
class MajorAdmin(admin.ModelAdmin):
    list_display = ['name']
    filter_horizontal = ['members']