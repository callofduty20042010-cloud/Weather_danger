from django.contrib import admin
from .models import Comment, DangerNotification, EventForecast, EventTimelineItem, Profile, SafetySignal, SavedLocation, WeatherEvent

class EventTimelineInline(admin.TabularInline):
    model = EventTimelineItem
    extra = 1


class EventForecastInline(admin.TabularInline):
    model = EventForecast
    extra = 1


@admin.register(WeatherEvent)
class WeatherEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_type', 'danger_level', 'status', 'credibility_score', 'region', 'latitude', 'longitude', 'created_at')
    list_filter = ('event_type', 'danger_level', 'status', 'created_at')
    search_fields = ('title', 'description', 'region')
    inlines = [EventTimelineInline, EventForecastInline]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'location_text', 'created_at')
    search_fields = ('user__username', 'event__title', 'text', 'location_text')
    list_filter = ('created_at',)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'nickname', 'city', 'country', 'preferred_language')
    search_fields = ('user__username', 'nickname', 'city', 'country')


@admin.register(SavedLocation)
class SavedLocationAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'location_type', 'address', 'latitude', 'longitude')
    list_filter = ('location_type',)
    search_fields = ('user__username', 'name', 'address')


@admin.register(SafetySignal)
class SafetySignalAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'signal_type', 'location_text', 'created_at')
    list_filter = ('signal_type', 'created_at')
    search_fields = ('user__username', 'event__title', 'message', 'location_text')

@admin.register(DangerNotification)
class DangerNotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'distance_km', 'is_read', 'shown_as_popup', 'created_at')
    list_filter = ('is_read', 'shown_as_popup', 'created_at')
    search_fields = ('user__username', 'event__title', 'message')
