"""
Test suite for Cultural Trip application.
"""

from django.test import TestCase, Client
from django.urls import reverse
from .models import TripCache, GuideCache, AccommodationCache, EventCache
from datetime import datetime, timedelta


class TripsAppTestCase(TestCase):
    """Test cases for trips application"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = Client()
        
        # Create test data
        self.trip = TripCache.objects.create(
            trip_id=101,
            region='North',
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=7)
        )
        
        self.guide = GuideCache.objects.create(
            guide_id=301,
            name='Nasser Samir',
            region='North',
            languages='Arabic, French'
        )
        
        self.accommodation = AccommodationCache.objects.create(
            hotel_id=501,
            name='El Aurassi Hotel',
            region='North',
            rating=5.0
        )
        
        self.event = EventCache.objects.create(
            event_id=401,
            region='North',
            name='Timgad Festival',
            event_date=datetime.now(),
            event_type='Music'
        )
    
    def test_index_page_loads(self):
        """Test that index page loads successfully"""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
    
    def test_trips_list_page(self):
        """Test trips list page"""
        response = self.client.get(reverse('trips_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'trips/trips_list.html')
    
    def test_accommodations_list_page(self):
        """Test accommodations list page"""
        response = self.client.get(reverse('accommodations_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'trips/accommodations_list.html')
    
    def test_guides_list_page(self):
        """Test guides list page"""
        response = self.client.get(reverse('guides_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'trips/guides_list.html')
    
    def test_events_list_page(self):
        """Test events list page"""
        response = self.client.get(reverse('events_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'trips/events_list.html')
    
    def test_book_trip_page(self):
        """Test book trip page"""
        response = self.client.get(reverse('book_trip'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'trips/book_trip.html')
    
    def test_book_trip_post(self):
        """Test booking submission"""
        data = {
            'name': 'Ahmed Ali',
            'nationality': 'Algerian',
            'contact': '0550123456',
            'trip_id': 101,
            'amount': 90000.00,
            'terms': True
        }
        response = self.client.post(reverse('book_trip'), data)
        # Should redirect to booking success
        self.assertEqual(response.status_code, 302)
    
    def test_trip_models_creation(self):
        """Test that trip cache models are created correctly"""
        self.assertEqual(self.trip.trip_id, 101)
        self.assertEqual(self.trip.region, 'North')
        self.assertEqual(self.guide.name, 'Nasser Samir')
        self.assertEqual(self.accommodation.rating, 5.0)
        self.assertEqual(self.event.event_type, 'Music')
    
    def test_queryset_filters(self):
        """Test that querysets can be filtered by region"""
        north_trips = TripCache.objects.filter(region='North')
        self.assertEqual(north_trips.count(), 1)
        
        north_guides = GuideCache.objects.filter(region='North')
        self.assertEqual(north_guides.count(), 1)
