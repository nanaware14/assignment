# Lead Management System

A production-ready CRM-style Lead Management System built with Django 5, Django REST Framework, Bootstrap 5 templates, and role-based authentication.

Every page includes the required footer link: [Built for Digital Heroes Training Task](https://digitalheroesco.com).

## Features

- Public lead capture form
- Django authentication with Admin and Member roles
- Admin dashboard with lead totals and activity log
- Member dashboard with assigned lead metrics
- Lead pipeline: New, Contacted, Qualified, Proposal Sent, Won, Lost
- Lead assignment, priority, notes, timestamps, and activity trail
- Admin user management
- DRF API with pagination, filtering, search, ordering, and role-aware access
- Bootstrap 5 responsive UI with sidebar, navbar, cards, tables, forms, filters, pagination, and modals
- Automated Django tests for authentication, permissions, lead creation, assignment, and status updates

## Tech Stack

- Python 3.12
- Django 5
- Django REST Framework
- django-filter
- Bootstrap 5
- PostgreSQL for production
- SQLite for local development
- WhiteNoise for static files
- Gunicorn for Render

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file from `.env.example`.

```env
SECRET_KEY=change-me-in-production
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=
DATABASE_URL=
```

For Render/PostgreSQL, set `DATABASE_URL` to the Render database internal connection string.

## Local Setup

```bash
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Open:

- Public lead form: `http://127.0.0.1:8000/`
- Login: `http://127.0.0.1:8000/accounts/login/`
- Dashboard: `http://127.0.0.1:8000/dashboard/`

## Sample Credentials

Created by:

```bash
python manage.py seed_demo
```

Admin:

- Username: `admin`
- Password: `Admin@12345`

Member:

- Username: `member`
- Password: `Member@12345`

## Database Migration

```bash
python manage.py makemigrations
python manage.py migrate
```

The initial migration is already included, so `migrate` is enough for a fresh setup.

## Running Tests

```bash
python manage.py test
```

## API Documentation

Authentication uses Django session auth or basic auth. Public lead creation is allowed without authentication.

### Endpoints

`GET /api/leads/`

- Auth required
- Admin: all leads
- Member: assigned leads only
- Supports pagination, filtering, search, and ordering

Query examples:

```text
/api/leads/?status=NEW
/api/leads/?priority=HIGH
/api/leads/?search=acme
/api/leads/?ordering=-updated_at
```

`POST /api/leads/`

- Public endpoint for lead capture
- Returns `201 Created`

Payload:

```json
{
  "full_name": "Jane Doe",
  "email": "jane@example.com",
  "phone": "+1 555 0111",
  "company": "Example Inc",
  "source": "Website",
  "message": "Interested in your services."
}
```

`GET /api/leads/{id}/`

- Auth required
- Admin can view all
- Member can view assigned leads only

`PUT /api/leads/{id}/`

- Auth required
- Admin can update lead fields and assignment
- Member can update only `status` for assigned leads

`DELETE /api/leads/{id}/`

- Admin only
- Returns `204 No Content`

## Role Permissions

Admin:

- View all leads
- Create, edit, assign, and delete leads
- Manage users
- View activity log

Member:

- View assigned leads only
- Update lead status
- Add notes
- Cannot delete leads
- Cannot assign leads

Permissions are enforced in Django views, templates, and DRF permissions/serializers.

## Deployment On Render Free Tier

1. Push this project to GitHub.
2. Create a new PostgreSQL database on Render Free Tier.
3. Create a new Render Web Service from the GitHub repository.
4. Use these settings:
   - Build command: `bash build.sh`
   - Start command: `gunicorn lead_management.wsgi:application`
5. Add environment variables:
   - `SECRET_KEY`
   - `DEBUG=False`
   - `ALLOWED_HOSTS=.onrender.com`
   - `CSRF_TRUSTED_ORIGINS=https://your-service-name.onrender.com`
   - `DATABASE_URL`
6. Deploy.
7. Open the Render shell and create an admin:

```bash
python manage.py createsuperuser
```

Optional demo data:

```bash
python manage.py seed_demo
```

## GitHub Version Control

```bash
git init
git add .
git commit -m "Build Django lead management system"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

## Project Structure

```text
lead_management/
  settings.py
  urls.py
crm/
  models.py
  forms.py
  views.py
  api_views.py
  serializers.py
  permissions.py
  tests.py
templates/
  base.html
  crm/
  registration/
static/
  css/styles.css
  js/app.js
```
