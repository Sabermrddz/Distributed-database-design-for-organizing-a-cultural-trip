"""
Admin panel views for CRUD operations.
All admin views require @admin_required decorator for authentication.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import db
from .auth import admin_required, verify_admin_credentials
from .admin_forms import (
    TripForm, GuideForm, AccommodationForm, EventForm, 
    TouristForm, BookingForm
)
import os


def build_query_info(title, queries, note):
    return {
        'title': title,
        'queries': queries,
        'fallback': False,
        'note': note,
    }


# ========== AUTHENTICATION VIEWS ==========

def admin_login(request):
    """Admin login page"""
    if request.session.get('is_admin'):
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if verify_admin_credentials(username, password):
            request.session['is_admin'] = True
            messages.success(request, f'Welcome {username}!')
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'admin/login.html')


def admin_logout(request):
    """Admin logout"""
    request.session.flush()
    messages.success(request, 'Logged out successfully')
    return redirect('/')


# ========== DASHBOARD ==========

@admin_required
def admin_dashboard(request):
    """Admin dashboard - show statistics and DB status"""
    def fetch_rows(query):
        conn = db.get_central_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            if not cursor.description:
                return []
            columns = [column[0].lower() for column in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        finally:
            cursor.close()
            conn.close()

    def fetch_count(query):
        conn = db.get_central_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            row = cursor.fetchone()
            return int(row[0]) if row and row[0] is not None else 0
        finally:
            cursor.close()
            conn.close()

    def node_status(name, query, source):
        try:
            count = fetch_count(query)
            return {
                'name': name,
                'connected': True,
                'count': count,
                'message': f'{source} connected successfully'
            }
        except Exception as e:
            return {
                'name': name,
                'connected': False,
                'count': None,
                'message': f'Error connecting: {str(e)}'
            }

    try:
        trips_by_region = fetch_rows(
            "SELECT Region, COUNT(*) AS cnt FROM All_Trips GROUP BY Region ORDER BY Region"
        )
        guides_by_region = fetch_rows(
            "SELECT Region, COUNT(*) AS cnt FROM All_Guides GROUP BY Region ORDER BY Region"
        )

        bookings_count = fetch_count("SELECT COUNT(*) FROM Booking_Info")
        tourists_count = fetch_count("SELECT COUNT(*) FROM Tourist_Basic")
        total_trips = sum(int(row.get('cnt', 0) or 0) for row in trips_by_region)
        dashboard_cards = [
            {
                'icon': 'fas fa-suitcase',
                'label': 'Total Bookings',
                'value': bookings_count,
                'style': '',
                'title': 'Bookings Count',
                'query': "SELECT COUNT(*) FROM Booking_Info",
                'note': 'Counts all booking records stored in Booking_Info.',
            },
            {
                'icon': 'fas fa-users',
                'label': 'Total Tourists',
                'value': tourists_count,
                'style': 'background: linear-gradient(135deg, #F093FB 0%, #F5576C 100%);',
                'title': 'Tourists Count',
                'query': "SELECT COUNT(*) FROM Tourist_Basic",
                'note': 'Counts all registered tourists from the central tourist table.',
            },
            {
                'icon': 'fas fa-route',
                'label': 'Total Trips',
                'value': total_trips,
                'style': 'background: linear-gradient(135deg, #4FACFE 0%, #00F2FE 100%);',
                'title': 'Trips Count by Region',
                'query': "SELECT Region, COUNT(*) AS cnt FROM All_Trips GROUP BY Region ORDER BY Region",
                'note': 'Counts trips from the distributed All_Trips view and groups them by region.',
            },
        ]

        nodes = [
            node_status('Central HQ', "SELECT COUNT(*) AS cnt FROM Tourist_Basic", 'Central database'),
            node_status('North DB', "SELECT COUNT(*) AS cnt FROM Trips@north_link", 'North DB via north_link'),
            node_status('South DB', "SELECT COUNT(*) AS cnt FROM Trips@south_link", 'South DB via south_link'),
            node_status('East DB', "SELECT COUNT(*) AS cnt FROM Trips@east_link", 'East DB via east_link'),
        ]

        dashboard_sections = [
            {
                'title': 'Database Nodes Status',
                'note': 'Central database is connected directly, and the regional databases are connected through DB links.',
                'queries': [
                    "SELECT COUNT(*) AS cnt FROM Tourist_Basic",
                    "SELECT COUNT(*) AS cnt FROM Trips@north_link",
                    "SELECT COUNT(*) AS cnt FROM Trips@south_link",
                    "SELECT COUNT(*) AS cnt FROM Trips@east_link",
                ],
            },
            {
                'title': 'Trips by Region',
                'note': 'This section groups live trips by region from the distributed view.',
                'queries': [
                    "SELECT Region, COUNT(*) AS cnt FROM All_Trips GROUP BY Region ORDER BY Region",
                ],
            },
            {
                'title': 'Guides by Region',
                'note': 'This section groups live guides by region from the distributed view.',
                'queries': [
                    "SELECT Region, COUNT(*) AS cnt FROM All_Guides GROUP BY Region ORDER BY Region",
                ],
            },
        ]

        context = {
            'trips_by_region': trips_by_region,
            'guides_by_region': guides_by_region,
            'bookings_count': bookings_count,
            'tourists_count': tourists_count,
            'total_trips': total_trips,
            'nodes': nodes,
            'dashboard_cards': dashboard_cards,
            'dashboard_sections': dashboard_sections,
        }
        return render(request, 'admin/dashboard.html', context)

    except Exception as e:
        print(f"\n[DASHBOARD ERROR] {type(e).__name__}: {str(e)}\n")
        messages.error(request, f'Error loading dashboard: {str(e)}')
        dashboard_cards = [
            {
                'icon': 'fas fa-suitcase',
                'label': 'Total Bookings',
                'value': 0,
                'style': '',
                'title': 'Bookings Count',
                'query': "SELECT COUNT(*) FROM Booking_Info",
                'note': 'Counts all booking records stored in Booking_Info.',
            },
            {
                'icon': 'fas fa-users',
                'label': 'Total Tourists',
                'value': 0,
                'style': 'background: linear-gradient(135deg, #F093FB 0%, #F5576C 100%);',
                'title': 'Tourists Count',
                'query': "SELECT COUNT(*) FROM Tourist_Basic",
                'note': 'Counts all registered tourists from the central tourist table.',
            },
            {
                'icon': 'fas fa-route',
                'label': 'Total Trips',
                'value': 0,
                'style': 'background: linear-gradient(135deg, #4FACFE 0%, #00F2FE 100%);',
                'title': 'Trips Count by Region',
                'query': "SELECT Region, COUNT(*) AS cnt FROM All_Trips GROUP BY Region ORDER BY Region",
                'note': 'Counts trips from the distributed All_Trips view and groups them by region.',
            },
        ]
        dashboard_sections = [
            {
                'title': 'Database Nodes Status',
                'note': 'Central database is connected directly, and the regional databases are connected through DB links.',
                'queries': [
                    "SELECT COUNT(*) AS cnt FROM Tourist_Basic",
                    "SELECT COUNT(*) AS cnt FROM Trips@north_link",
                    "SELECT COUNT(*) AS cnt FROM Trips@south_link",
                    "SELECT COUNT(*) AS cnt FROM Trips@east_link",
                ],
            },
            {
                'title': 'Trips by Region',
                'note': 'This section groups live trips by region from the distributed view.',
                'queries': [
                    "SELECT Region, COUNT(*) AS cnt FROM All_Trips GROUP BY Region ORDER BY Region",
                ],
            },
            {
                'title': 'Guides by Region',
                'note': 'This section groups live guides by region from the distributed view.',
                'queries': [
                    "SELECT Region, COUNT(*) AS cnt FROM All_Guides GROUP BY Region ORDER BY Region",
                ],
            },
        ]
        context = {
            'trips_by_region': [],
            'guides_by_region': [],
            'bookings_count': 0,
            'tourists_count': 0,
            'total_trips': 0,
            'nodes': [],
            'dashboard_cards': dashboard_cards,
            'dashboard_sections': dashboard_sections,
        }
        return render(request, 'admin/dashboard.html', context)


@admin_required
def itinerary_view(request):
    """Generate and display an itinerary for a tourist."""
    error = None
    result = None

    def fetch_rows(query, params=None):
        conn = db.get_central_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params or [])
            if not cursor.description:
                return []
            columns = [column[0].lower() for column in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        finally:
            cursor.close()
            conn.close()

    def fetch_one(query, params=None):
        rows = fetch_rows(query, params)
        return rows[0] if rows else None

    try:
        all_itineraries = fetch_rows(
            "SELECT * FROM Full_Itinerary ORDER BY StartDate, TouristName"
        )
    except Exception as e:
        messages.error(request, f'Error loading itineraries: {str(e)}')
        all_itineraries = []

    if request.method == 'POST':
        tourist_id = request.POST.get('tourist_id', '').strip()

        if not tourist_id:
            error = 'Please enter a Tourist ID.'
        else:
            try:
                tourist = fetch_one(
                    "SELECT TouristID, Name, Nationality FROM All_Tourists WHERE TouristID = :1",
                    (tourist_id,)
                )

                if not tourist:
                    error = f"No tourist found for Tourist ID: {tourist_id}"
                else:
                    rows = fetch_rows(
                        """
                        SELECT fi.*
                        FROM Full_Itinerary fi
                        JOIN Booking_Info bi ON fi.BookingID = bi.BookingID
                        WHERE bi.TouristID = :1
                        ORDER BY fi.StartDate, fi.EventDate
                        """,
                        (tourist_id,)
                    )

                    if not rows:
                        error = f"No itinerary found for Tourist ID: {tourist_id}"
                    else:
                        result = rows[0]
                        result['touristid'] = tourist.get('touristid')
                        result['touristname'] = tourist.get('name')
                        result['nationality'] = tourist.get('nationality')
            except Exception as e:
                error = str(e)

    context = {
        'result': result,
        'error': error,
        'all_itineraries': all_itineraries,
        'itinerary_sections': [
            {
                'title': 'Tourist Lookup',
                'note': 'This lookup verifies the Tourist ID before generating the itinerary result.',
                'queries': [
                    "SELECT TouristID, Name, Nationality FROM All_Tourists WHERE TouristID = :1",
                ],
            },
            {
                'title': 'Generated Itinerary',
                'note': 'This query builds the live itinerary result for the selected tourist.',
                'queries': [
                    """
                    SELECT fi.*
                    FROM Full_Itinerary fi
                    JOIN Booking_Info bi ON fi.BookingID = bi.BookingID
                    WHERE bi.TouristID = :1
                    ORDER BY fi.StartDate, fi.EventDate
                    """.strip(),
                ],
            },
            {
                'title': 'Full Itinerary Table',
                'note': 'This table is loaded from the live `Full_Itinerary` view.',
                'queries': [
                    "SELECT * FROM Full_Itinerary ORDER BY StartDate, TouristName",
                ],
            },
        ],
    }
    return render(request, 'admin/itinerary.html', context)


# ========== TRIPS CRUD ==========

@admin_required
def trips_list(request):
    """List all trips"""
    region = request.GET.get('region')
    
    try:
        if region:
            query = "SELECT * FROM All_Trips WHERE Region = :1 ORDER BY StartDate"
            trips = db.execute_query(query, (region,))
        else:
            query = "SELECT * FROM All_Trips ORDER BY Region, StartDate"
            trips = db.execute_query(query)
    except Exception as e:
        messages.error(request, f'Error loading trips: {str(e)}')
        trips = []
    
    context = {
        'trips': trips,
        'regions': ['North', 'South', 'East'],
        'selected_region': region,
        'query_info': build_query_info(
            'Trips Data Source',
            [query],
            'Trips are read from the live Oracle view All_Trips.'
        ),
    }
    return render(request, 'admin/trips_list.html', context)


@admin_required
def trip_add(request):
    """Add new trip"""
    if request.method == 'POST':
        form = TripForm(request.POST)
        if form.is_valid():
            try:
                data = form.cleaned_data
                region = data['region']
                link = db.get_db_link(region)
                
                query = f"""
                    INSERT INTO Trips{link} 
                    (TripID, TripName, Description, Region, StartDate, EndDate, Duration)
                    VALUES (TRIPS_SEQ.NEXTVAL, :1, :2, :3, :4, :5, :6)
                """
                db.execute_dml(query, (
                    data['trip_name'],
                    data.get('description', ''),
                    region,
                    data['start_date'],
                    data['end_date'],
                    data.get('duration', 0)
                ))
                messages.success(request, 'Trip added successfully')
                return redirect('trips_list')
            except Exception as e:
                messages.error(request, f'Error adding trip: {str(e)}')
    else:
        form = TripForm()
    
    return render(request, 'admin/form.html', {'form': form, 'title': 'Add Trip'})


@admin_required
def trip_edit(request, trip_id):
    """Edit existing trip"""
    try:
        # Get trip to find its region
        query = "SELECT * FROM All_Trips WHERE TripID = :1"
        trip = db.execute_query_one(query, (trip_id,))
        
        if not trip:
            messages.error(request, 'Trip not found')
            return redirect('trips_list')
        
        if request.method == 'POST':
            form = TripForm(request.POST)
            if form.is_valid():
                try:
                    data = form.cleaned_data
                    region = trip['region']
                    link = db.get_db_link(region)
                    
                    query = f"""
                        UPDATE Trips{link}
                        SET TripName = :1, Description = :2, StartDate = :3, EndDate = :4, Duration = :5
                        WHERE TripID = :6
                    """
                    db.execute_dml(query, (
                        data['trip_name'],
                        data.get('description', ''),
                        data['start_date'],
                        data['end_date'],
                        data.get('duration', 0),
                        trip_id
                    ))
                    messages.success(request, 'Trip updated successfully')
                    return redirect('trips_list')
                except Exception as e:
                    messages.error(request, f'Error updating trip: {str(e)}')
        else:
            form = TripForm(initial={
                'trip_id': trip['tripid'],
                'trip_name': trip.get('tripname', ''),
                'description': trip.get('description', ''),
                'region': trip['region'],
                'start_date': trip['startdate'],
                'end_date': trip['enddate'],
                'duration': trip.get('duration', 0)
            })
        
        return render(request, 'admin/form.html', {'form': form, 'trip': trip, 'title': 'Edit Trip'})
    
    except Exception as e:
        messages.error(request, f'Error loading trip: {str(e)}')
        return redirect('trips_list')


@admin_required
def trip_delete(request, trip_id):
    """Delete trip"""
    try:
        # Get trip to find its region
        query = "SELECT Region FROM All_Trips WHERE TripID = :1"
        trip = db.execute_query_one(query, (trip_id,))
        
        if trip:
            region = trip['region']
            link = db.get_db_link(region)
            delete_query = f"DELETE FROM Trips{link} WHERE TripID = :1"
            db.execute_dml(delete_query, (trip_id,))
            messages.success(request, 'Trip deleted successfully')
        else:
            messages.error(request, 'Trip not found')
    except Exception as e:
        messages.error(request, f'Error deleting trip: {str(e)}')
    
    return redirect('trips_list')


# ========== TOURISTS CRUD (VERTICAL FRAGMENTATION) ==========

@admin_required
def tourists_list(request):
    """List all tourists"""
    try:
        query = "SELECT * FROM All_Tourists ORDER BY TouristID"
        tourists = db.execute_query(query)
    except Exception as e:
        messages.error(request, f'Error loading tourists: {str(e)}')
        tourists = []
    
    return render(request, 'admin/tourists_list.html', {
        'tourists': tourists,
        'query_info': build_query_info(
            'Tourists Data Source',
            [query],
            'Tourists are read from the live Oracle view All_Tourists.'
        ),
    })


@admin_required
def tourist_add(request):
    """Add new tourist (inserts into BOTH Tourist_Basic and Tourist_Contact)"""
    if request.method == 'POST':
        form = TouristForm(request.POST)
        if form.is_valid():
            try:
                data = form.cleaned_data
                
                # Insert into Tourist_Basic (stores name - horizontal on central)
                query1 = "INSERT INTO Tourist_Basic (TouristID, Name) VALUES (TOURIST_SEQ.NEXTVAL, :1)"
                db.execute_dml(query1, (data['name'],))
                
                # Get the last inserted ID
                query_id = "SELECT MAX(TouristID) as id FROM Tourist_Basic"
                result = db.execute_query_one(query_id)
                tourist_id = result['id'] if result else 1
                
                # Insert into Tourist_Contact (stores contact info - vertical fragment on central)
                query2 = """
                    INSERT INTO Tourist_Contact (TouristID, Nationality, Contact)
                    VALUES (:1, :2, :3)
                """
                db.execute_dml(query2, (tourist_id, data.get('nationality', ''), data.get('contact', '')))
                
                messages.success(request, 'Tourist added successfully')
                return redirect('tourists_list')
            except Exception as e:
                messages.error(request, f'Error adding tourist: {str(e)}')
    else:
        form = TouristForm()
    
    return render(request, 'admin/form.html', {'form': form, 'title': 'Add Tourist'})


@admin_required
def tourist_edit(request, tourist_id):
    """Edit existing tourist"""
    try:
        query = "SELECT * FROM All_Tourists WHERE TouristID = :1"
        tourist = db.execute_query_one(query, (tourist_id,))
        
        if not tourist:
            messages.error(request, 'Tourist not found')
            return redirect('tourists_list')
        
        if request.method == 'POST':
            form = TouristForm(request.POST)
            if form.is_valid():
                try:
                    data = form.cleaned_data
                    
                    # Update Tourist_Basic
                    query1 = "UPDATE Tourist_Basic SET Name = :1 WHERE TouristID = :2"
                    db.execute_dml(query1, (data['name'], tourist_id))
                    
                    # Update Tourist_Contact
                    query2 = """
                        UPDATE Tourist_Contact 
                        SET Nationality = :1, Contact = :2 
                        WHERE TouristID = :3
                    """
                    db.execute_dml(query2, (data.get('nationality', ''), data.get('contact', ''), tourist_id))
                    
                    messages.success(request, 'Tourist updated successfully')
                    return redirect('tourists_list')
                except Exception as e:
                    messages.error(request, f'Error updating tourist: {str(e)}')
        else:
            form = TouristForm(initial={
                'tourist_id': tourist['touristid'],
                'name': tourist.get('name', ''),
                'nationality': tourist.get('nationality', ''),
                'contact': tourist.get('contact', '')
            })
        
        return render(request, 'admin/form.html', {'form': form, 'tourist': tourist, 'title': 'Edit Tourist'})
    
    except Exception as e:
        messages.error(request, f'Error loading tourist: {str(e)}')
        return redirect('tourists_list')


@admin_required
def tourist_delete(request, tourist_id):
    """Delete tourist (removes from BOTH tables)"""
    try:
        # Delete from Tourist_Contact first (FK constraint)
        query1 = "DELETE FROM Tourist_Contact WHERE TouristID = :1"
        db.execute_dml(query1, (tourist_id,))
        
        # Then delete from Tourist_Basic
        query2 = "DELETE FROM Tourist_Basic WHERE TouristID = :1"
        db.execute_dml(query2, (tourist_id,))
        
        messages.success(request, 'Tourist deleted successfully')
    except Exception as e:
        messages.error(request, f'Error deleting tourist: {str(e)}')
    
    return redirect('tourists_list')


# ========== BOOKINGS CRUD (MIXED FRAGMENTATION) ==========

@admin_required
def bookings_list(request):
    """List all bookings"""
    try:
        query = "SELECT * FROM Booking_Details ORDER BY BookingID DESC"
        bookings = db.execute_query(query)
    except Exception as e:
        messages.error(request, f'Error loading bookings: {str(e)}')
        bookings = []
    
    return render(request, 'admin/bookings_list.html', {
        'bookings': bookings,
        'query_info': build_query_info(
            'Bookings Data Source',
            [query],
            'Bookings are read from the live Oracle view Booking_Details.'
        ),
    })


@admin_required
def booking_add(request):
    """Add new booking (inserts into BOTH Booking_Info and Booking_Amount)"""
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            try:
                data = form.cleaned_data
                
                # Insert into Booking_Info (stores booking info - horizontal on central)
                query1 = """
                    INSERT INTO Booking_Info (BookingID, TouristID, TripID)
                    VALUES (BOOKING_SEQ.NEXTVAL, :1, :2)
                """
                db.execute_dml(query1, (data['tourist_id'], data['trip_id']))
                
                # Get the last inserted ID
                query_id = "SELECT MAX(BookingID) as id FROM Booking_Info"
                result = db.execute_query_one(query_id)
                booking_id = result['id'] if result else 1
                
                # Insert into Booking_Amount (stores amount - vertical fragment on central)
                query2 = """
                    INSERT INTO Booking_Amount (BookingID, Amount, BookingDate)
                    VALUES (:1, :2, SYSDATE)
                """
                db.execute_dml(query2, (booking_id, data['amount']))
                
                messages.success(request, 'Booking added successfully')
                return redirect('bookings_list')
            except Exception as e:
                messages.error(request, f'Error adding booking: {str(e)}')
    else:
        form = BookingForm()
    
    return render(request, 'admin/form.html', {'form': form, 'title': 'Add Booking'})


@admin_required
def booking_edit(request, booking_id):
    """Edit existing booking"""
    try:
        query = "SELECT * FROM Booking_Details WHERE BookingID = :1"
        booking = db.execute_query_one(query, (booking_id,))
        
        if not booking:
            messages.error(request, 'Booking not found')
            return redirect('bookings_list')
        
        if request.method == 'POST':
            form = BookingForm(request.POST)
            if form.is_valid():
                try:
                    data = form.cleaned_data
                    
                    # Update Booking_Info
                    query1 = """
                        UPDATE Booking_Info 
                        SET TouristID = :1, TripID = :2 
                        WHERE BookingID = :3
                    """
                    db.execute_dml(query1, (data['tourist_id'], data['trip_id'], booking_id))
                    
                    # Update Booking_Amount
                    query2 = """
                        UPDATE Booking_Amount 
                        SET Amount = :1 
                        WHERE BookingID = :2
                    """
                    db.execute_dml(query2, (data['amount'], booking_id))
                    
                    messages.success(request, 'Booking updated successfully')
                    return redirect('bookings_list')
                except Exception as e:
                    messages.error(request, f'Error updating booking: {str(e)}')
        else:
            form = BookingForm(initial={
                'booking_id': booking['bookingid'],
                'tourist_id': booking.get('touristid', 0),
                'trip_id': booking.get('tripid', 0),
                'amount': booking.get('amount', 0)
            })
        
        return render(request, 'admin/form.html', {'form': form, 'booking': booking, 'title': 'Edit Booking'})
    
    except Exception as e:
        messages.error(request, f'Error loading booking: {str(e)}')
        return redirect('bookings_list')


@admin_required
def booking_delete(request, booking_id):
    """Delete booking (removes from BOTH tables)"""
    try:
        # Delete from Booking_Amount first (FK constraint)
        query1 = "DELETE FROM Booking_Amount WHERE BookingID = :1"
        db.execute_dml(query1, (booking_id,))
        
        # Then delete from Booking_Info
        query2 = "DELETE FROM Booking_Info WHERE BookingID = :1"
        db.execute_dml(query2, (booking_id,))
        
        messages.success(request, 'Booking deleted successfully')
    except Exception as e:
        messages.error(request, f'Error deleting booking: {str(e)}')
    
    return redirect('bookings_list')


# ========== GUIDES CRUD ==========

@admin_required
def guides_list(request):
    """List all guides"""
    region = request.GET.get('region')
    
    try:
        if region:
            query = "SELECT * FROM All_Guides WHERE Region = :1 ORDER BY Name"
            guides = db.execute_query(query, (region,))
        else:
            query = "SELECT * FROM All_Guides ORDER BY Region, Name"
            guides = db.execute_query(query)
    except Exception as e:
        messages.error(request, f'Error loading guides: {str(e)}')
        guides = []
    
    context = {
        'guides': guides,
        'regions': ['North', 'South', 'East'],
        'selected_region': region,
        'query_info': build_query_info(
            'Guides Data Source',
            [query],
            'Guides are read from the live Oracle view All_Guides.'
        ),
    }
    return render(request, 'admin/guides_list.html', context)


@admin_required
def guide_add(request):
    """Add new guide"""
    if request.method == 'POST':
        form = GuideForm(request.POST)
        if form.is_valid():
            try:
                data = form.cleaned_data
                region = data['region']
                link = db.get_db_link(region)
                
                query = f"""
                    INSERT INTO Guides{link} 
                    (GuideID, Name, Region, Languages, Phone, ExperienceYears)
                    VALUES (GUIDES_SEQ.NEXTVAL, :1, :2, :3, :4, :5)
                """
                db.execute_dml(query, (
                    data['name'],
                    region,
                    data.get('languages', ''),
                    data.get('phone', ''),
                    data.get('experience_years', 0)
                ))
                messages.success(request, 'Guide added successfully')
                return redirect('admin_guides_list')
            except Exception as e:
                messages.error(request, f'Error adding guide: {str(e)}')
    else:
        form = GuideForm()
    
    return render(request, 'admin/form.html', {'form': form, 'title': 'Add Guide'})


@admin_required
def guide_edit(request, guide_id):
    """Edit existing guide"""
    try:
        query = "SELECT * FROM All_Guides WHERE GuideID = :1"
        guide = db.execute_query_one(query, (guide_id,))
        
        if not guide:
            messages.error(request, 'Guide not found')
            return redirect('admin_guides_list')
        
        if request.method == 'POST':
            form = GuideForm(request.POST)
            if form.is_valid():
                try:
                    data = form.cleaned_data
                    region = guide['region']
                    link = db.get_db_link(region)
                    
                    query = f"""
                        UPDATE Guides{link}
                        SET Name = :1, Languages = :2, Phone = :3, ExperienceYears = :4
                        WHERE GuideID = :5
                    """
                    db.execute_dml(query, (
                        data['name'],
                        data.get('languages', ''),
                        data.get('phone', ''),
                        data.get('experience_years', 0),
                        guide_id
                    ))
                    messages.success(request, 'Guide updated successfully')
                    return redirect('admin_guides_list')
                except Exception as e:
                    messages.error(request, f'Error updating guide: {str(e)}')
        else:
            form = GuideForm(initial={
                'name': guide.get('name', ''),
                'region': guide['region'],
                'languages': guide.get('languages', ''),
                'phone': guide.get('phone', ''),
                'experience_years': guide.get('experienceyears', 0)
            })
        
        return render(request, 'admin/form.html', {'form': form, 'guide': guide, 'title': 'Edit Guide'})
    
    except Exception as e:
        messages.error(request, f'Error loading guide: {str(e)}')
        return redirect('admin_guides_list')


@admin_required
def guide_delete(request, guide_id):
    """Delete guide"""
    try:
        query = "SELECT Region FROM All_Guides WHERE GuideID = :1"
        guide = db.execute_query_one(query, (guide_id,))
        
        if guide:
            region = guide['region']
            link = db.get_db_link(region)
            delete_query = f"DELETE FROM Guides{link} WHERE GuideID = :1"
            db.execute_dml(delete_query, (guide_id,))
            messages.success(request, 'Guide deleted successfully')
        else:
            messages.error(request, 'Guide not found')
    except Exception as e:
        messages.error(request, f'Error deleting guide: {str(e)}')
    
    return redirect('admin_guides_list')


# ========== ACCOMMODATIONS CRUD ==========

@admin_required
def accommodations_list(request):
    """List all accommodations"""
    region = request.GET.get('region')
    
    try:
        if region:
            query = "SELECT * FROM All_Accommodations WHERE Region = :1 ORDER BY Name"
            accommodations = db.execute_query(query, (region,))
        else:
            query = "SELECT * FROM All_Accommodations ORDER BY Region, Name"
            accommodations = db.execute_query(query)
    except Exception as e:
        messages.error(request, f'Error loading accommodations: {str(e)}')
        accommodations = []
    
    context = {
        'accommodations': accommodations,
        'regions': ['North', 'South', 'East'],
        'selected_region': region,
        'query_info': build_query_info(
            'Accommodations Data Source',
            [query],
            'Accommodations are read from the live Oracle view All_Accommodations.'
        ),
    }
    return render(request, 'admin/accommodations_list.html', context)


@admin_required
def accommodation_add(request):
    """Add new accommodation"""
    if request.method == 'POST':
        form = AccommodationForm(request.POST)
        if form.is_valid():
            try:
                data = form.cleaned_data
                region = data['region']
                link = db.get_db_link(region)
                
                query = f"""
                    INSERT INTO Accommodations{link} 
                    (AccommodationID, Name, Region, Rating, Price, Address, Phone)
                    VALUES (ACCOMMODATIONS_SEQ.NEXTVAL, :1, :2, :3, :4, :5, :6)
                """
                db.execute_dml(query, (
                    data['name'],
                    region,
                    data.get('rating', 0),
                    data.get('price', 0),
                    data.get('address', ''),
                    data.get('phone', '')
                ))
                messages.success(request, 'Accommodation added successfully')
                return redirect('admin_accommodations_list')
            except Exception as e:
                messages.error(request, f'Error adding accommodation: {str(e)}')
    else:
        form = AccommodationForm()
    
    return render(request, 'admin/form.html', {'form': form, 'title': 'Add Accommodation'})


@admin_required
def accommodation_edit(request, accommodation_id):
    """Edit existing accommodation"""
    try:
        query = "SELECT * FROM All_Accommodations WHERE AccommodationID = :1"
        accommodation = db.execute_query_one(query, (accommodation_id,))
        
        if not accommodation:
            messages.error(request, 'Accommodation not found')
            return redirect('admin_accommodations_list')
        
        if request.method == 'POST':
            form = AccommodationForm(request.POST)
            if form.is_valid():
                try:
                    data = form.cleaned_data
                    region = accommodation['region']
                    link = db.get_db_link(region)
                    
                    query = f"""
                        UPDATE Accommodations{link}
                        SET Name = :1, Rating = :2, Price = :3, Address = :4, Phone = :5
                        WHERE AccommodationID = :6
                    """
                    db.execute_dml(query, (
                        data['name'],
                        data.get('rating', 0),
                        data.get('price', 0),
                        data.get('address', ''),
                        data.get('phone', ''),
                        accommodation_id
                    ))
                    messages.success(request, 'Accommodation updated successfully')
                    return redirect('admin_accommodations_list')
                except Exception as e:
                    messages.error(request, f'Error updating accommodation: {str(e)}')
        else:
            form = AccommodationForm(initial={
                'name': accommodation.get('name', ''),
                'region': accommodation['region'],
                'rating': accommodation.get('rating', 0),
                'price': accommodation.get('price', 0),
                'address': accommodation.get('address', ''),
                'phone': accommodation.get('phone', '')
            })
        
        return render(request, 'admin/form.html', {'form': form, 'accommodation': accommodation, 'title': 'Edit Accommodation'})
    
    except Exception as e:
        messages.error(request, f'Error loading accommodation: {str(e)}')
        return redirect('admin_accommodations_list')


@admin_required
def accommodation_delete(request, accommodation_id):
    """Delete accommodation"""
    try:
        query = "SELECT Region FROM All_Accommodations WHERE AccommodationID = :1"
        accommodation = db.execute_query_one(query, (accommodation_id,))
        
        if accommodation:
            region = accommodation['region']
            link = db.get_db_link(region)
            delete_query = f"DELETE FROM Accommodations{link} WHERE AccommodationID = :1"
            db.execute_dml(delete_query, (accommodation_id,))
            messages.success(request, 'Accommodation deleted successfully')
        else:
            messages.error(request, 'Accommodation not found')
    except Exception as e:
        messages.error(request, f'Error deleting accommodation: {str(e)}')
    
    return redirect('admin_accommodations_list')


# ========== EVENTS CRUD ==========

@admin_required
def events_list(request):
    """List all events"""
    region = request.GET.get('region')
    
    try:
        if region:
            query = "SELECT * FROM All_Events WHERE Region = :1 ORDER BY EventDate DESC"
            events = db.execute_query(query, (region,))
        else:
            query = "SELECT * FROM All_Events ORDER BY Region, EventDate DESC"
            events = db.execute_query(query)
    except Exception as e:
        messages.error(request, f'Error loading events: {str(e)}')
        events = []
    
    context = {
        'events': events,
        'regions': ['North', 'South', 'East'],
        'selected_region': region,
        'query_info': build_query_info(
            'Events Data Source',
            [query],
            'Events are read from the live Oracle view All_Events.'
        ),
    }
    return render(request, 'admin/events_list.html', context)


@admin_required
def event_add(request):
    """Add new event"""
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            try:
                data = form.cleaned_data
                region = data['region']
                link = db.get_db_link(region)
                id_query = f"SELECT COALESCE(MAX(EventID), 0) + 1 AS id FROM CulturalEvents{link}"
                result = db.execute_query_one(id_query)
                next_id = result['id'] if result else 1
                
                query = f"""
                    INSERT INTO CulturalEvents{link} 
                    (EventID, Region, Name, EventDate, Type)
                    VALUES (:1, :2, :3, :4, :5)
                """
                db.execute_dml(query, (
                    next_id,
                    region,
                    data['event_name'],
                    data['event_date'],
                    data.get('event_type', '')
                ))
                messages.success(request, 'Event added successfully')
                return redirect('admin_events_list')
            except Exception as e:
                messages.error(request, f'Error adding event: {str(e)}')
    else:
        form = EventForm()
    
    return render(request, 'admin/form.html', {'form': form, 'title': 'Add Event'})


@admin_required
def event_edit(request, event_id):
    """Edit existing event"""
    try:
        query = "SELECT * FROM All_Events WHERE EventID = :1"
        event = db.execute_query_one(query, (event_id,))
        
        if not event:
            messages.error(request, 'Event not found')
            return redirect('admin_events_list')
        
        if request.method == 'POST':
            form = EventForm(request.POST)
            if form.is_valid():
                try:
                    data = form.cleaned_data
                    region = event['region']
                    link = db.get_db_link(region)
                    
                    query = f"""
                        UPDATE CulturalEvents{link}
                        SET Name = :1, EventDate = :2, Type = :3
                        WHERE EventID = :4
                    """
                    db.execute_dml(query, (
                        data['event_name'],
                        data['event_date'],
                        data.get('event_type', ''),
                        event_id
                    ))
                    messages.success(request, 'Event updated successfully')
                    return redirect('admin_events_list')
                except Exception as e:
                    messages.error(request, f'Error updating event: {str(e)}')
        else:
            form = EventForm(initial={
                'event_name': event.get('name', ''),
                'region': event['region'],
                'event_date': event['eventdate'],
                'event_type': event.get('type', '')
            })
        
        return render(request, 'admin/form.html', {'form': form, 'event': event, 'title': 'Edit Event'})
    
    except Exception as e:
        messages.error(request, f'Error loading event: {str(e)}')
        return redirect('admin_events_list')


@admin_required
def event_delete(request, event_id):
    """Delete event"""
    try:
        query = "SELECT Region FROM All_Events WHERE EventID = :1"
        event = db.execute_query_one(query, (event_id,))
        
        if event:
            region = event['region']
            link = db.get_db_link(region)
            delete_query = f"DELETE FROM CulturalEvents{link} WHERE EventID = :1"
            db.execute_dml(delete_query, (event_id,))
            messages.success(request, 'Event deleted successfully')
        else:
            messages.error(request, 'Event not found')
    except Exception as e:
        messages.error(request, f'Error deleting event: {str(e)}')
    
    return redirect('admin_events_list')


