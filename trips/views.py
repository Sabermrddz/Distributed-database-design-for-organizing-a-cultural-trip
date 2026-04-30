"""
Views for Cultural Trip application.
Uses raw Oracle queries via db.py module.
Includes graceful fallback to sample data when database is unavailable.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import db
from .forms import BookingForm, TouristForm
import datetime

# Sample data for development/demo when database is unavailable
SAMPLE_TRIPS = [
    {'tripid': 101, 'region': 'North', 'startdate': datetime.date(2025, 6, 1), 'enddate': datetime.date(2025, 6, 10)},
    {'tripid': 102, 'region': 'South', 'startdate': datetime.date(2025, 7, 5), 'enddate': datetime.date(2025, 7, 15)},
    {'tripid': 103, 'region': 'East', 'startdate': datetime.date(2025, 8, 1), 'enddate': datetime.date(2025, 8, 10)},
]

SAMPLE_GUIDES = [
    {'guideid': 301, 'name': 'Nasser Samir', 'region': 'North', 'languages': 'Arabic, French'},
    {'guideid': 302, 'name': 'Hadj Moussa', 'region': 'South', 'languages': 'Arabic, Tamazight'},
    {'guideid': 303, 'name': 'Omar Ben Ali', 'region': 'East', 'languages': 'Arabic, French'},
]

SAMPLE_ACCOMMODATIONS = [
    {'hotelid': 501, 'name': 'El Aurassi Hotel', 'region': 'North', 'rating': 5},
    {'hotelid': 502, 'name': 'Hotel Tahat', 'region': 'South', 'rating': 4},
    {'hotelid': 503, 'name': 'Hotel Chiak', 'region': 'East', 'rating': 4},
]

SAMPLE_EVENTS = [
    {'eventid': 401, 'region': 'North', 'name': 'Timgad Festival', 'eventdate': datetime.date(2025, 6, 5), 'type': 'Music'},
    {'eventid': 402, 'region': 'South', 'name': 'Tamanrasset Festival', 'eventdate': datetime.date(2025, 7, 10), 'type': 'Heritage'},
    {'eventid': 403, 'region': 'East', 'name': 'Batna Festival', 'eventdate': datetime.date(2025, 8, 5), 'type': 'Culture'},
]


def build_query_info(title, queries, fallback=False, note=None):
    return {
        'title': title,
        'queries': queries,
        'fallback': fallback,
        'note': note,
    }


def index(request):
    """
    Homepage - Display overview of all regions and available trips.
    """
    try:
        # Query trips from central database via DB Links
        trips_query = "SELECT * FROM All_Trips ORDER BY StartDate"
        trips = db.execute_query(trips_query)
        
        # Query all guides
        guides_query = "SELECT * FROM All_Guides ORDER BY Region"
        guides = db.execute_query(guides_query)
    except Exception as e:
        # Use sample data when database is unavailable
        trips = SAMPLE_TRIPS
        guides = SAMPLE_GUIDES
        query_info = build_query_info(
            'Home Data Source',
            [
                trips_query,
                guides_query,
            ],
            fallback=True,
            note='Sample data fallback used because the Oracle connection was unavailable.'
        )
    else:
        query_info = build_query_info(
            'Home Data Source',
            [
                trips_query,
                guides_query,
            ],
            fallback=False,
            note='This page reads from the live Oracle views All_Trips and All_Guides.'
        )
    
    context = {
        'trips': trips,
        'guides': guides,
        'regions': ['North', 'South', 'East']
        ,
        'query_info': query_info,
    }
    return render(request, 'index.html', context)


def trips_list(request):
    """
    List all trips by region.
    """
    region = request.GET.get('region', None)
    
    try:
        if region:
            query = "SELECT * FROM All_Trips WHERE Region = :region ORDER BY STARTDATE"
            trips = db.execute_query(query, (region,))
        else:
            query = "SELECT * FROM All_Trips ORDER BY Region, STARTDATE"
            trips = db.execute_query(query)
    except Exception:
        # Use sample data when database is unavailable
        trips = [t for t in SAMPLE_TRIPS if not region or t['region'] == region]
        query_info = build_query_info(
            'Trips Data Source',
            [query],
            fallback=True,
            note='Sample data fallback used because the Oracle connection was unavailable.'
        )
    else:
        query_info = build_query_info(
            'Trips Data Source',
            [query],
            fallback=False,
            note='This page reads from the live Oracle view All_Trips.'
        )
    
    context = {
        'trips': trips,
        'selected_region': region,
        'regions': ['North', 'South', 'East']
        ,
        'query_info': query_info,
    }
    return render(request, 'trips/trips_list.html', context)


def trip_detail(request, trip_id):
    """
    Display details of a specific trip including accommodations and events.
    """
    try:
        # Get trip info
        trip_query = "SELECT * FROM All_Trips WHERE TripID = :trip_id"
        trip_result = db.execute_query(trip_query, (trip_id,))
        
        if not trip_result:
            # Try sample data
            trip = next((t for t in SAMPLE_TRIPS if t['tripid'] == trip_id), None)
            if not trip:
                messages.error(request, "Trip not found")
                return redirect('trips_list')
        else:
            trip = trip_result[0]
    except Exception:
        # Use sample data when database is unavailable
        trip = next((t for t in SAMPLE_TRIPS if t['tripid'] == trip_id), None)
        if not trip:
            messages.error(request, "Trip not found")
            return redirect('trips_list')
        query_info = build_query_info(
            'Trip Detail Data Source',
            [
                trip_query,
                "SELECT * FROM All_Accommodations WHERE Region = :region",
                "SELECT * FROM All_Events WHERE Region = :region",
                "SELECT * FROM All_Guides WHERE Region = :region",
            ],
            fallback=True,
            note='Sample data fallback used because the Oracle connection was unavailable.'
        )
    else:
        query_info = build_query_info(
            'Trip Detail Data Source',
            [
                trip_query,
                "SELECT * FROM All_Accommodations WHERE Region = :region",
                "SELECT * FROM All_Events WHERE Region = :region",
                "SELECT * FROM All_Guides WHERE Region = :region",
            ],
            fallback=False,
            note='This page reads from the live Oracle views All_Trips, All_Accommodations, All_Events, and All_Guides.'
        )
    
    region = trip['region']  # Region from dict key
    
    try:
        # Get accommodations for this region
        acc_query = "SELECT * FROM All_Accommodations WHERE Region = :region"
        accommodations = db.execute_query(acc_query, (region,))
        
        # Get events for this region
        events_query = "SELECT * FROM All_Events WHERE Region = :region"
        events = db.execute_query(events_query, (region,))
        
        # Get guides for this region
        guides_query = "SELECT * FROM All_Guides WHERE Region = :region"
        guides = db.execute_query(guides_query, (region,))
    except Exception:
        # Use sample data
        accommodations = [a for a in SAMPLE_ACCOMMODATIONS if a['region'] == region]
        events = [e for e in SAMPLE_EVENTS if e['region'] == region]
        guides = [g for g in SAMPLE_GUIDES if g['region'] == region]
        query_info['queries'] = [
            trip_query,
            acc_query,
            events_query,
            guides_query,
        ]
    
    # Calculate trip duration in days
    start_date = trip['startdate']
    end_date = trip['enddate']
    duration_days = (end_date - start_date).days + 1  # +1 to include both start and end dates
    duration_text = f"{duration_days} day{'s' if duration_days != 1 else ''}"
    
    context = {
        'trip': trip,
        'accommodations': accommodations,
        'events': events,
        'guides': guides,
        'query_info': query_info,
        'duration_days': duration_days,
        'duration_text': duration_text,
    }
    return render(request, 'trips/trip_detail.html', context)


def accommodations_list(request):
    """
    List all accommodations by region.
    """
    region = request.GET.get('region', None)
    
    try:
        if region:
            query = "SELECT * FROM All_Accommodations WHERE Region = :region ORDER BY RATING DESC"
            accommodations = db.execute_query(query, (region,))
        else:
            query = "SELECT * FROM All_Accommodations ORDER BY Region, RATING DESC"
            accommodations = db.execute_query(query)
    except Exception:
        # Use sample data when database is unavailable
        accommodations = [a for a in SAMPLE_ACCOMMODATIONS if not region or a['region'] == region]
        query_info = build_query_info(
            'Accommodations Data Source',
            [query],
            fallback=True,
            note='Sample data fallback used because the Oracle connection was unavailable.'
        )
    else:
        query_info = build_query_info(
            'Accommodations Data Source',
            [query],
            fallback=False,
            note='This page reads from the live Oracle view All_Accommodations.'
        )
    
    context = {
        'accommodations': accommodations,
        'selected_region': region,
        'regions': ['North', 'South', 'East']
        ,
        'query_info': query_info,
    }
    return render(request, 'trips/accommodations_list.html', context)


def guides_list(request):
    """
    List all guides by region.
    """
    region = request.GET.get('region', None)
    
    try:
        if region:
            query = "SELECT * FROM All_Guides WHERE Region = :region ORDER BY NAME"
            guides = db.execute_query(query, (region,))
        else:
            query = "SELECT * FROM All_Guides ORDER BY Region, NAME"
            guides = db.execute_query(query)
    except Exception:
        # Use sample data when database is unavailable
        guides = [g for g in SAMPLE_GUIDES if not region or g['region'] == region]
        query_info = build_query_info(
            'Guides Data Source',
            [query],
            fallback=True,
            note='Sample data fallback used because the Oracle connection was unavailable.'
        )
    else:
        query_info = build_query_info(
            'Guides Data Source',
            [query],
            fallback=False,
            note='This page reads from the live Oracle view All_Guides.'
        )
    
    context = {
        'guides': guides,
        'selected_region': region,
        'regions': ['North', 'South', 'East']
        ,
        'query_info': query_info,
    }
    return render(request, 'trips/guides_list.html', context)


def events_list(request):
    """
    List all cultural events by region.
    """
    region = request.GET.get('region', None)
    
    try:
        if region:
            query = "SELECT * FROM All_Events WHERE Region = :region ORDER BY EVENTDATE"
            events = db.execute_query(query, (region,))
        else:
            query = "SELECT * FROM All_Events ORDER BY Region, EVENTDATE"
            events = db.execute_query(query)
    except Exception:
        # Use sample data when database is unavailable
        events = [e for e in SAMPLE_EVENTS if not region or e['region'] == region]
        query_info = build_query_info(
            'Events Data Source',
            [query],
            fallback=True,
            note='Sample data fallback used because the Oracle connection was unavailable.'
        )
    else:
        query_info = build_query_info(
            'Events Data Source',
            [query],
            fallback=False,
            note='This page reads from the live Oracle view All_Events.'
        )
    
    context = {
        'events': events,
        'selected_region': region,
        'regions': ['North', 'South', 'East']
        ,
        'query_info': query_info,
    }
    return render(request, 'trips/events_list.html', context)


@require_http_methods(["GET", "POST"])
def book_trip(request):
    """
    Booking feature disabled - display only mode.
    This feature will be implemented later.
    """
    messages.info(request, "Booking feature coming soon! For now, this is a display-only database.")
    return redirect('index')


def booking_success(request):
    """
    Booking confirmation page.
    """
    return render(request, 'trips/booking_success.html')


def dashboard(request):
    """
    Admin dashboard - Show statistics and key metrics.
    """
    try:
        # Count trips by region
        trips_query = "SELECT Region, COUNT(*) as count FROM Trips_All GROUP BY Region"
        trips_by_region = db.execute_query(trips_query)
        
        # Count guides by region
        guides_query = "SELECT Region, COUNT(*) as count FROM Guides_All GROUP BY Region"
        guides_by_region = db.execute_query(guides_query)
        
        # Count bookings
        bookings_query = "SELECT COUNT(*) FROM Booking_Info"
        bookings_count = db.execute_query(bookings_query)[0][0]
        
        # Count tourists
        tourists_query = "SELECT COUNT(*) FROM Tourist_Basic"
        tourists_count = db.execute_query(tourists_query)[0][0]
    except Exception:
        # Use sample data when database is unavailable
        from itertools import groupby
        from operator import itemgetter
        
        trips_by_region = [(k, len(list(g))) for k, g in groupby(sorted(SAMPLE_TRIPS, key=itemgetter(1)), key=itemgetter(1))]
        guides_by_region = [(k, len(list(g))) for k, g in groupby(sorted(SAMPLE_GUIDES, key=itemgetter(2)), key=itemgetter(2))]
        bookings_count = 3
        tourists_count = 3
        query_info = build_query_info(
            'Dashboard Data Source',
            [
                trips_query,
                guides_query,
                bookings_query,
                tourists_query,
            ],
            fallback=True,
            note='Sample data fallback used because the Oracle connection was unavailable.'
        )
    else:
        query_info = build_query_info(
            'Dashboard Data Source',
            [
                trips_query,
                guides_query,
                bookings_query,
                tourists_query,
            ],
            fallback=False,
            note='This dashboard reads live counts from the Oracle-backed database.'
        )
    
    context = {
        'trips_by_region': trips_by_region,
        'guides_by_region': guides_by_region,
        'bookings_count': bookings_count,
        'tourists_count': tourists_count,
        'query_info': query_info,
    }
    return render(request, 'trips/dashboard.html', context)

# ========== DEBUG ==========
def debug_env(request):
    """Debug view to check environment variables and database connection"""
    import os
    
    debug_info = f"""✓ Environment Variables:
  DB_HOST: {os.getenv('DB_HOST', 'MISSING')}
  DB_PORT: {os.getenv('DB_PORT', 'MISSING')}
  DB_SERVICE: {os.getenv('DB_SERVICE', 'MISSING')}
  DB_USER: {os.getenv('DB_USER', 'MISSING')}
  DB_PASSWORD: {'*' * len(os.getenv('DB_PASSWORD', ''))}
  
✓ DSN Connection String:
  {os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_SERVICE')}
"""
    
    connection_test = "Testing database connection...\n"
    try:
        conn = db.get_central_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM ALL_TRIPS")
        result = cursor.fetchone()
        connection_test += f"✅ Connected successfully!\n"
        connection_test += f"✅ All_Trips view accessible - Count: {result[0]}"
        conn.close()
    except Exception as e:
        connection_test += f"❌ Connection failed:\n{str(e)}"
    
    context = {
        'debug_info': debug_info,
        'connection_test': connection_test,
    }
    return render(request, 'debug.html', context)
