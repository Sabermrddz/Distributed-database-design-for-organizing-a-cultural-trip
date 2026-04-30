# Distributed Cultural Trip Database

A Django web application that demonstrates a **real distributed Oracle database** for managing cultural trips across three regions: **North**, **South**, and **East**.

The app connects to one **central Oracle database** on DigitalOcean, and that central database uses **DB links** to reach the regional databases. The website shows how data can be fragmented and combined across multiple nodes while still feeling like one system.

## Concept

This project is built to show a practical distributed database design for a travel agency:

- **Central database** stores shared data such as tourists and bookings.
- **Regional databases** store region-specific data such as trips, guides, accommodations, and events.
- **Oracle views** combine data from all nodes into one page for the frontend.
- **Django** acts as the website layer and reads live data from Oracle.

It is useful as a student project, a database architecture demo, or a prototype for a travel booking system.

## Features

- Public website for browsing trips, guides, accommodations, and events
- Admin panel with dashboard, itinerary view, and data overview
- Live Oracle-backed data loading
- Region-based filtering and distributed views
- Read-only admin presentation for explaining the schema and queries

## Architecture

```
Django Web App
    ↓
Central Oracle DB
    ↓
DB Links
 ├─ North DB
 ├─ South DB
 └─ East DB
```

The Django app connects only to the central Oracle service, and Oracle handles access to the regional nodes.

## Tech Stack

- Python 3.8+
- Django 4.2
- Oracle XE 21c
- `python-oracledb` in thin mode
- Tailwind CSS
- WhiteNoise for static files

## How to Use

### 1) Clone the project

```bash
git clone <repository-url>
cd "Distributed database design for organizing a cultural trip"
```

### 2) Create a virtual environment

```bash
python -m venv venv
```

Activate it:

- Windows:
  ```bash
  venv\Scripts\activate
  ```
- macOS/Linux:
  ```bash
  source venv/bin/activate
  ```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

### 4) Create your `.env` file

Copy the template:

```bash
copy env.example .env
```

Then fill in your real values:

```env
DB_HOST=PUBLIC-IP-AD
DB_PORT=1521
DB_SERVICE=XEPDB1
DB_USER=central_user
DB_PASSWORD=your_oracle_password

ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_admin_password

SECRET_KEY=replace_with_a_long_random_secret_key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com
```

### 5) Run the project

```bash
python manage.py runserver
```

Open the site in your browser at:

```bash
http://127.0.0.1:8000
```

## How to Use the Website

- Visit the **public site** to browse trips and region pages.
- Open the **admin login** page to access the admin panel.
- In the admin dashboard, you can inspect the live database status, itinerary data, and Oracle queries used by each section.
- Use the itinerary page to generate a live itinerary for a tourist ID.

## Project Structure

- `db.py` — Oracle connection helpers
- `settings.py` — Django configuration
- `trips/views.py` — public website views
- `trips/admin_views.py` — admin panel views
- `templates/` — HTML templates
- `db_schema.sql` — database schema and sample data

## Database Idea

- `Tourist_Basic` and `Tourist_Contact` represent vertically split tourist data
- `Booking_Info` and `Booking_Amount` represent mixed booking storage
- `Trips`, `Guides`, `Accommodations`, and `CulturalEvents` are region-based tables
- `All_Trips`, `All_Guides`, `All_Events`, and `Full_Itinerary` are Oracle views used by the website

## Important Notes

- The app depends on a live Oracle database connection.
- The website connects only to the **central Oracle database**.
- Do not commit your `.env` file.
- If Oracle is unreachable, some pages may show fallback or error states.

## Deployment

See [`DEPLOYMENT.md`](DEPLOYMENT.md) for Heroku deployment steps and environment setup.

## License

Provided as-is for educational and demonstration purposes.
