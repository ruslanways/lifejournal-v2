# LifeJournal v2

Instagram-like Django application for sharing posts with images, titles, descriptions, and likes.

**Tech Stack:** Django · Django REST Framework · Uvicorn (ASGI) · PostgreSQL · Redis · Celery · Whitenoise · S3

---

## Requirements

- **Docker** + **Docker Compose** plugin (`docker compose version`)
- **`uv`** (optional, for local tooling)

---

## Project Structure

```
config/          # Settings (base/dev/prod), URLs, ASGI configuration, Celery app
apps/
  ├── users/     # Custom user model with bio, avatar, website fields
  └── posts/     # Posts application
compose.dev.yml  # Development stack configuration
compose.prod.yml # Production stack configuration (no dev-only commands)
Dockerfile       # Multi-stage build, virtual environment in /opt/venv
```

---

## Authentication System

### Overview

The application uses **django-allauth** for authentication, providing:
- Email-based registration with mandatory verification
- Login with **both email and username**
- Password reset via email
- Email management (add, remove, verify multiple emails)
- Ready for social authentication (Google, GitHub, etc.)

### Custom User Model

**Model:** `apps.users.User` (extends `AbstractUser`)

**Additional Fields:**
- `bio` - Text field (max 500 characters)
- `avatar` - Image field (uploaded to `media/avatars/`)
- `website` - URL field (max 200 characters)

**Admin Panel:** Enhanced UserAdmin with custom fields visible at `/admin/`

### Authentication URLs

All authentication URLs are under `/accounts/`:

#### User Registration & Login
- `GET/POST /accounts/signup/` - User registration form
- `GET/POST /accounts/login/` - Login (accepts username OR email)
- `POST /accounts/logout/` - Logout

#### Email Verification
- `GET /accounts/confirm-email/<key>/` - Verify email with key from email
- `GET/POST /accounts/email/` - Change email address (one email per user)

#### Password Management
- `GET/POST /accounts/password/change/` - Change password (when logged in)
- `GET/POST /accounts/password/set/` - Set password (for social accounts)
- `GET/POST /accounts/password/reset/` - Request password reset via email
- `GET /accounts/password/reset/done/` - Password reset email sent confirmation
- `GET/POST /accounts/password/reset/key/<uidb36>-<key>/` - Password reset form
- `GET /accounts/password/reset/key/done/` - Password successfully reset

#### Other
- `GET /accounts/inactive/` - Account inactive notice

### Email Verification Flow

1. User submits registration form at `/accounts/signup/`
2. Account created but **inactive** until email verified
3. Verification email sent with unique link
4. User clicks link → account activated
5. User can now login at `/accounts/login/`

**Development:** Emails appear in Docker container logs (console backend):
```bash
docker compose -f compose.dev.yml logs -f web
```

**Production:** Configure SMTP settings in `config/settings/prod.py`

### Testing Authentication

#### Create Test User
```bash
# Via signup form
Open: http://localhost:8000/accounts/signup/

# Via command line
docker compose -f compose.dev.yml exec web python manage.py createsuperuser
```

#### Login Options
Both methods work:
- **Email:** `user@example.com` + password
- **Username:** `username` + password


### Settings Configuration

**Key Settings** (`config/settings/base.py`):
```python
AUTH_USER_MODEL = "users.User"                      # Custom user model
ACCOUNT_AUTHENTICATION_METHOD = "username_email"    # Allow both
ACCOUNT_EMAIL_REQUIRED = True                       # Email is required
ACCOUNT_USERNAME_REQUIRED = True                    # Username is required
ACCOUNT_EMAIL_VERIFICATION = "mandatory"            # Must verify email
ACCOUNT_UNIQUE_EMAIL = True                         # One email per user
ACCOUNT_MAX_EMAIL_ADDRESSES = 1                     # Limit to one email
```

### Future Enhancements

**Phase 2:** REST API with JWT tokens
- Add `dj-rest-auth` for API endpoints
- JWT authentication for SPAs and mobile apps
- Token refresh and rotation

**Phase 3:** Two-Factor Authentication
- TOTP (Google Authenticator, Authy)
- Email-based 2FA
- WebAuthn/Security keys

---

## Development

### 1. Environment Setup

Create a `.env` file in the project root (gitignored).

**Minimal example:**

```bash
DJANGO_SETTINGS_MODULE=config.settings.dev
DEBUG=True
SECRET_KEY=dev-insecure-change-me
ALLOWED_HOSTS=localhost,127.0.0.1

DATABASE_URL=postgresql://app:app@db:5432/app
REDIS_URL=redis://redis:6379/0
```

### 2. Start Development Stack

```bash
docker compose -f compose.dev.yml up --build
```

**What this starts:**
- **`web`** — Runs `migrate`, `collectstatic`, then starts Uvicorn with `--reload`
- **`db`** — PostgreSQL 16 with healthcheck
- **`redis`** — Redis with healthcheck
- **`celery_worker`** — Celery worker for background tasks
- **`celery_beat`** — Celery beat scheduler for periodic tasks

**Access the application:**
- Main site: http://localhost:8000
- Django Admin: http://localhost:8000/admin/
- User Login: http://localhost:8000/accounts/login/
- User Signup: http://localhost:8000/accounts/signup/

### 3. Management Commands

Run Django management commands inside the `web` container:

```bash
# Create a superuser
docker compose -f compose.dev.yml exec web python manage.py createsuperuser

# Open Django shell
docker compose -f compose.dev.yml exec web python manage.py shell

# Run any other management command
docker compose -f compose.dev.yml exec web python manage.py <command>
```

### 4. View Logs

View logs for specific services:

```bash
# Web service logs
docker compose -f compose.dev.yml logs -f web

# Celery worker logs
docker compose -f compose.dev.yml logs -f celery_worker

# Celery beat logs
docker compose -f compose.dev.yml logs -f celery_beat

# All services
docker compose -f compose.dev.yml logs -f
```

### 5. Reset Development Database

⚠️ **Warning:** This deletes the PostgreSQL volume and all data.

```bash
docker compose -f compose.dev.yml down -v
docker compose -f compose.dev.yml up --build
```

---

## Production

### Overview

**Important:** The production compose configuration is intentionally "clean":
- No development bind mounts
- No `--reload` flag
- Does **not** run migrations or collectstatic on startup

**Recommended deployment approach:** Deploy on EC2 with RDS for PostgreSQL, use GitHub Actions for CI/CD, and store secrets in AWS Secrets Manager or use IAM roles.

### 1. Environment Variables

In production, you must provide environment variables via your EC2 environment, secrets manager (recommended), or via a `.env` file present on the server.

**Required variables:**

```bash
DJANGO_SETTINGS_MODULE=config.settings.prod
DEBUG=False
SECRET_KEY=<secure-random-key>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# External PostgreSQL (RDS)
# Note: Production compose does NOT run PostgreSQL in Docker
DATABASE_URL=postgresql://USER:PASSWORD@RDS_HOST:5432/DBNAME

REDIS_URL=redis://redis:6379/0

CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# S3 media storage (if enabled in prod settings)
AWS_STORAGE_BUCKET_NAME=your-bucket
AWS_S3_REGION_NAME=eu-central-1
```

**Production notes:**

- **Authentication:** Prefer **IAM roles** on EC2 instead of storing AWS access keys in environment variables
- **Static files:** Served by **Whitenoise** from `STATIC_ROOT` inside the Docker image
- **Media files:** Uploaded media is stored on **S3** in production (when `AWS_STORAGE_BUCKET_NAME` is set)
- **Database:** `compose.prod.yml` expects PostgreSQL to be external (e.g., AWS RDS), but runs Redis in Docker

### 2. Deploy Production Services

```bash
docker compose -f compose.prod.yml up -d --build
```

**Production services:**
- **`web`** — Uvicorn ASGI server with 2 workers, exposed internally on port 8000
- **`celery_worker`** — Celery worker for background task processing
- **`celery_beat`** — Celery beat for scheduled task execution
- **`redis`** — Redis cache and Celery message broker

### 3. Run Database Migrations

Migrations must be run explicitly in production (one-off command):

```bash
docker compose -f compose.prod.yml run --rm web python manage.py migrate
```

### 4. Create Admin User

Create a superuser account (one-off command):

```bash
docker compose -f compose.prod.yml run --rm web python manage.py createsuperuser
```

### 5. Static Files Handling

Static files are served from `STATIC_ROOT` via **Whitenoise**. 

You have two options:
1. Collect static files during image build (bake them into the image)
2. Collect static files during deployment as a one-off command

In development, `collectstatic` is run automatically by the web service startup command.

To collect static files manually in production:

```bash
docker compose -f compose.prod.yml run --rm web python manage.py collectstatic --noinput
```

---

## Technical Notes

### Why `/opt/venv`?

The Python virtual environment is installed into `/opt/venv` (not `/app/.venv`) so that development bind mounts (`.:/app`) never hide the installed dependencies. This prevents the common "No module named django" error when mounting the local directory into the container.

### Celery Beat Schedule Files

Celery Beat writes runtime state files under `var/celery/` (gitignored). This includes files like `celerybeat-schedule*` which track the schedule execution state. These files persist between container restarts when using volumes.

---

## Troubleshooting

### "Connection refused" to PostgreSQL during startup

**Problem:** PostgreSQL may take a moment to become ready after the container starts.

**Solution:** The `compose.dev.yml` file includes healthchecks and dependency conditions (`depends_on` with `condition: service_healthy`) to reduce race conditions. If you still experience issues, wait a few seconds and try again, or check the database logs:

```bash
docker compose -f compose.dev.yml logs db
```

### "No module named django" inside container

**Problem:** The virtual environment is being hidden by a bind mount.

**Solution:** This repository uses `/opt/venv` instead of `/app/.venv` to avoid this class of issue. If you're still experiencing this problem, ensure you haven't modified the Dockerfile or volume mounts in a way that hides the `/opt/venv` directory.
