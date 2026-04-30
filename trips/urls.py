"""
URL configuration for trips application.
Public + Admin routes.
"""

from django.urls import path
from . import views, admin_views

urlpatterns = [
    # ========== DEBUG ==========
    path('debug/', views.debug_env, name='debug_env'),
    
    # ========== PUBLIC PAGES ==========
    path('', views.index, name='index'),
    path('trips/', views.trips_list, name='trips_list'),
    path('trips/<int:trip_id>/', views.trip_detail, name='trip_detail'),
    path('accommodations/', views.accommodations_list, name='accommodations_list'),
    path('guides/', views.guides_list, name='guides_list'),
    path('events/', views.events_list, name='events_list'),
    path('book/', views.book_trip, name='book_trip'),
    path('booking/success/', views.booking_success, name='booking_success'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # ========== ADMIN AUTHENTICATION ==========
    path('admin-login/', admin_views.admin_login, name='admin_login'),
    path('admin-logout/', admin_views.admin_logout, name='admin_logout'),
    
    # ========== ADMIN PANEL ==========
    path('admin-panel/dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/itinerary/', admin_views.itinerary_view, name='admin_itinerary'),
    
    # Trips (Horizontal Fragmentation)
    path('admin-panel/trips/', admin_views.trips_list, name='admin_trips_list'),
    
    # Tourists (Vertical Fragmentation)
    path('admin-panel/tourists/', admin_views.tourists_list, name='admin_tourists_list'),
    
    # Bookings (Mixed Fragmentation)
    path('admin-panel/bookings/', admin_views.bookings_list, name='admin_bookings_list'),
    
    # Guides (Horizontal Fragmentation)
    path('admin-panel/guides/', admin_views.guides_list, name='admin_guides_list'),
    
    # Accommodations (Horizontal Fragmentation)
    path('admin-panel/accommodations/', admin_views.accommodations_list, name='admin_accommodations_list'),
    
    # Events (Horizontal Fragmentation)
    path('admin-panel/events/', admin_views.events_list, name='admin_events_list'),
]
