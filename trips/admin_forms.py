"""
Django forms for admin CRUD operations.
"""

from django import forms
from datetime import date


class TripForm(forms.Form):
    """Form for creating/editing trips"""
    trip_id = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg'}),
        required=False,  # Auto-generate on create
        label='Trip ID'
    )
    trip_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg', 'placeholder': 'Trip name'}),
        label='Trip Name'
    )
    description = forms.CharField(
        max_length=500,
        widget=forms.Textarea(attrs={'class': 'w-full px-3 py-2 border rounded-lg', 'placeholder': 'Description', 'rows': 3}),
        required=False
    )
    region = forms.ChoiceField(
        choices=[('North', 'North'), ('South', 'South'), ('East', 'East')],
        widget=forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-lg'})
    )
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg', 'type': 'date'}),
        label='Start Date'
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg', 'type': 'date'}),
        label='End Date'
    )
    duration = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg'}),
        required=False
    )


class GuideForm(forms.Form):
    """Form for creating/editing guides"""
    guide_id = forms.IntegerField(required=False, label='Guide ID')
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg', 'placeholder': 'Full name'})
    )
    region = forms.ChoiceField(
        choices=[('North', 'North'), ('South', 'South'), ('East', 'East')],
        widget=forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-lg'})
    )
    languages = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg', 'placeholder': 'e.g., Arabic, French'}),
        required=False
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg'}),
        required=False
    )
    experience_years = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg'}),
        required=False,
        label='Years of Experience'
    )


class AccommodationForm(forms.Form):
    """Form for creating/editing accommodations"""
    accommodation_id = forms.IntegerField(required=False, label='Accommodation ID')
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg', 'placeholder': 'Hotel/Resort name'})
    )
    region = forms.ChoiceField(
        choices=[('North', 'North'), ('South', 'South'), ('East', 'East')],
        widget=forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-lg'})
    )
    rating = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg', 'min': 1, 'max': 5}),
        required=False
    )
    price = forms.DecimalField(
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg', 'step': '0.01'}),
        required=False,
        label='Price per Night'
    )
    address = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg'}),
        required=False
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg'}),
        required=False
    )


class EventForm(forms.Form):
    """Form for creating/editing cultural events"""
    event_id = forms.IntegerField(required=False, label='Event ID')
    event_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg', 'placeholder': 'Event name'})
    )
    region = forms.ChoiceField(
        choices=[('North', 'North'), ('South', 'South'), ('East', 'East')],
        widget=forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-lg'})
    )
    event_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg', 'type': 'date'}),
        label='Event Date'
    )
    event_type = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg', 'placeholder': 'e.g., Music, Heritage, Culture'}),
        required=False
    )
    description = forms.CharField(
        max_length=500,
        widget=forms.Textarea(attrs={'class': 'w-full px-3 py-2 border rounded-lg', 'rows': 3}),
        required=False
    )
    location = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg'}),
        required=False
    )


class TouristForm(forms.Form):
    """Form for creating/editing tourists (vertical fragmentation)"""
    tourist_id = forms.IntegerField(required=False, label='Tourist ID')
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg', 'placeholder': 'Full name'})
    )
    nationality = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg', 'placeholder': 'Nationality'}),
        required=False
    )
    contact = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg', 'placeholder': 'Email or phone'}),
        required=False,
        label='Contact Info'
    )


class BookingForm(forms.Form):
    """Form for creating/editing bookings (mixed fragmentation)"""
    booking_id = forms.IntegerField(required=False, label='Booking ID')
    tourist_id = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg'}),
        label='Tourist ID'
    )
    trip_id = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg'}),
        label='Trip ID'
    )
    amount = forms.DecimalField(
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg', 'step': '0.01'}),
        label='Booking Amount'
    )
