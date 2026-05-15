from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('event/<int:pk>/', views.event_detail, name='event_detail'),
    path('create-event/', views.create_event, name='create_event'),
    path('safety-guide/', views.safety_guide, name='safety_guide'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/saved-location/<int:pk>/delete/', views.delete_saved_location, name='delete_saved_location'),
    path('map/', views.events_map, name='events_map'),
    path('api/events/', views.events_api, name='events_api'),
    path('statistics/', views.statistics_view, name='statistics'),
    path('notifications/', views.notifications_view, name='notifications'),
]
