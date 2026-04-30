"""
Django models for Cultural Trip application.
Note: Models are minimal since we're using raw Oracle queries via db.py
"""

from django.db import models


class TripCache(models.Model):
    """Cache metadata for trips - stores locally for reference only"""
    trip_id = models.IntegerField(unique=True)
    region = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Trip Caches"
    
    def __str__(self):
        return f"Trip {self.trip_id} - {self.region}"


class GuideCache(models.Model):
    """Cache metadata for guides - stores locally for reference only"""
    guide_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)
    region = models.CharField(max_length=50)
    languages = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Guide Caches"
    
    def __str__(self):
        return self.name


class AccommodationCache(models.Model):
    """Cache metadata for accommodations - stores locally for reference only"""
    hotel_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)
    region = models.CharField(max_length=50)
    rating = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Accommodation Caches"
    
    def __str__(self):
        return self.name


class EventCache(models.Model):
    """Cache metadata for cultural events - stores locally for reference only"""
    event_id = models.IntegerField(unique=True)
    region = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    event_date = models.DateField()
    event_type = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Event Caches"
    
    def __str__(self):
        return self.name
