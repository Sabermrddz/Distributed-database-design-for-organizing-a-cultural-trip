# Deployment Instructions for Heroku

## Prerequisites

1. **Heroku Account** - Create account at https://www.heroku.com
2. **Heroku CLI** - Download from https://devcenter.heroku.com/articles/heroku-cli
3. **Git** - For version control
4. **Python 3.11** - Local development

## Step 1: Prepare Your Local Repository

```bash
# Initialize git if not already done
git init
git add .
git commit -m "Initial commit: Django cultural trip app"
```

## Step 2: Create Heroku Application

```bash
# Login to Heroku
heroku login

# Create new Heroku app
heroku create your-app-name

# or use heroku Student Pack benefits
# Create app through web dashboard if using Student Pack
```

## Step 3: Configure Environment Variables

```bash
# Set environment variables on Heroku
heroku config:set SECRET_KEY="your-django-secret-key"
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS="your-app-name.herokuapp.com"

# Database credentials (from your Oracle deployment)
heroku config:set DB_HOST="146.190.236.185"
heroku config:set DB_PORT="1521"
heroku config:set DB_SERVICE="XEPDB1"
heroku config:set DB_USER="central_user"
heroku config:set DB_PASSWORD="your-password"

# Regional nodes
heroku config:set NORTH_HOST="10.110.0.3"
heroku config:set NORTH_USER="north_user"
heroku config:set NORTH_PASSWORD="your-password"

heroku config:set SOUTH_HOST="10.110.0.4"
heroku config:set SOUTH_USER="south_user"
heroku config:set SOUTH_PASSWORD="your-password"

heroku config:set EAST_HOST="10.110.0.5"
heroku config:set EAST_USER="east_user"
heroku config:set EAST_PASSWORD="your-password"
```

## Step 4: Deploy to Heroku

```bash
# Deploy
git push heroku main
# (or master if using master branch)

# View logs
heroku logs --tail

# Check app status
heroku ps
```

## Step 5: Open Your Application

```bash
# Open in browser
heroku open

# Or visit: https://your-app-name.herokuapp.com
```

## Step 6: Troubleshooting

### Check logs for errors
```bash
heroku logs --tail
```

### Restart app
```bash
heroku restart
```

### Access database
```bash
# These will be accessed through your Oracle connections
# The app doesn't use a local database, only Oracle via db.py
```

### View config variables
```bash
heroku config
```

### Update environment variables
```bash
heroku config:set VARIABLE_NAME="new_value"
```

## Step 7: Continuous Deployment

For automatic deployment when pushing to your repository:

```bash
# Connect to GitHub (if using GitHub)
heroku apps:create --remote heroku

# Set up automatic deploys through Heroku dashboard
# Settings → Deployment method → Connect to GitHub
# Enable "Automatic deploys from main branch"
```

## Local Development

### Run locally
```bash
# Create .env file with all credentials
cp env.example .env

# Install dependencies
pip install -r requirements.txt

# Run development server
python manage.py runserver
```

### Test before deploying
```bash
# Create superuser for admin
python manage.py createsuperuser

# Run tests
python manage.py test

# Visit: http://localhost:8000
```

## Important Notes

1. **Never commit `.env` file** - Use `.env.example` as template
2. **Test locally first** - Always test locally before pushing to Heroku
3. **Database connections** - Connections must be able to reach your Oracle servers from Heroku
4. **Firewall rules** - Ensure DigitalOcean firewall allows Heroku IPs
5. **SSL/TLS** - Heroku provides free SSL certificates
6. **Static files** - WhiteNoise middleware handles compression and serving
7. **Monitoring** - Use Heroku dashboard to monitor app performance

## Rollback

If deployment fails, rollback to previous version:

```bash
heroku releases
heroku rollback v3  # Replace v3 with version number
```

## Scaling

```bash
# View current dynos
heroku ps

# Scale dynos
heroku ps:scale web=2

# Check costs
heroku billing:what-it-will-cost
```

## More Information

- [Heroku Python Deployment](https://devcenter.heroku.com/articles/getting-started-with-python)
- [Environment Variables](https://devcenter.heroku.com/articles/config-vars)
- [Django on Heroku](https://devcenter.heroku.com/articles/django-app-configuration)
- [Procfile Reference](https://devcenter.heroku.com/articles/procfile)
