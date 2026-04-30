"""
Admin configuration for trips application.
"""

from django.contrib import admin
from .models import TripCache, GuideCache, AccommodationCache, EventCache


@admin.register(TripCache)
class TripCacheAdmin(admin.ModelAdmin):
    list_display = ('trip_id', 'region', 'start_date', 'end_date')
    list_filter = ('region', 'start_date')
    search_fields = ('trip_id', 'region')
    readonly_fields = ('created_at',)


@admin.register(GuideCache)
class GuideCacheAdmin(admin.ModelAdmin):
    list_display = ('name', 'region', 'languages')
    list_filter = ('region',)
    search_fields = ('name', 'guide_id')
    readonly_fields = ('created_at',)


@admin.register(AccommodationCache)
class AccommodationCacheAdmin(admin.ModelAdmin):
    list_display = ('name', 'region', 'rating')
    list_filter = ('region', 'rating')
    search_fields = ('name', 'hotel_id')
    readonly_fields = ('created_at',)


@admin.register(EventCache)
class EventCacheAdmin(admin.ModelAdmin):
    list_display = ('name', 'region', 'event_date', 'event_type')
    list_filter = ('region', 'event_date', 'event_type')
    search_fields = ('name', 'event_id')
    readonly_fields = ('created_at',)
