"""
Forms for Cultural Trip application.
"""

from django import forms
from django.core.validators import MinValueValidator
import datetime


class BookingForm(forms.Form):
    """Form for booking a cultural trip"""
    
    name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Full Name'
        })
    )
    
    nationality = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nationality'
        })
    )
    
    contact = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone or Email'
        })
    )
    
    trip_id = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control'
        })
    )
    
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=True,
        validators=[MinValueValidator(0)],
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01'
        })
    )


class TouristForm(forms.Form):
    """Form for registering a new tourist"""
    
    name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Full Name'
        })
    )
    
    nationality = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nationality'
        })
    )
    
    contact = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone Number or Email'
        })
    )


class TripFilterForm(forms.Form):
    """Form for filtering trips by region"""
    
    REGION_CHOICES = [
        ('', 'All Regions'),
        ('North', 'North'),
        ('South', 'South'),
        ('East', 'East'),
    ]
    
    region = forms.ChoiceField(
        choices=REGION_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
