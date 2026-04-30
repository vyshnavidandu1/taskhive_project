# TaskHive — Complete Setup Instructions

## Prerequisites

Make sure you have the following installed:

| Tool | Version | Check Command |
|---|---|---|
| Python | 3.10+ | `python --version` |
| pip | latest | `pip --version` |

---

## Step-by-Step Setup

### Step 1 — Download the project

Place the `taskhive/` folder wherever you want on your laptop.

```
taskhive/
├── manage.py
├── requirements.txt
├── README.md
├── taskhive/
├── users/
├── projects/
├── tasks/
├── comments/
├── static/
└── templates/
```

---

### Step 2 — Open a terminal in the project folder

```bash
cd path/to/taskhive
```

---

### Step 3 — Create a virtual environment

**macOS / Linux:**
```bash
python3 -m venv venv
```

**Windows:**
```cmd
python -m venv venv
```

---

### Step 4 — Activate the virtual environment

**macOS / Linux:**
```bash
source venv/bin/activate
```

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

You should see `(venv)` at the start of your terminal prompt.

---

### Step 5 — Install all dependencies

```bash
pip install -r requirements.txt
```

This installs:
- Django 4.2
- Django REST Framework
- django-crispy-forms + crispy-bootstrap5
- Pillow (for avatar image uploads)
- django-filter

---

### Step 6 — Run database migrations

```bash
python manage.py migrate
```

This creates the `db.sqlite3` database file with all tables.

---

### Step 7 — Create your admin superuser

```bash
python manage.py createsuperuser
```

You will be prompted for:
- Username
- Email (optional)
- Password (min 8 characters)

---

### Step 8 — (Recommended) Load demo data

```bash
python manage.py seed_data
```

This creates:
- 5 demo users (admin, manager, 3 team members)
- 4 sample projects
- 12 sample tasks with comments

**Demo login credentials:**

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `admin123` |
| Manager | `sarah` | `demo1234` |
| Member | `alex` | `demo1234` |
| Member | `priya` | `demo1234` |
| Member | `james` | `demo1234` |

---

### Step 9 — Start the development server

```bash
python manage.py runserver
```

---

### Step 10 — Open in your browser

Visit: **http://127.0.0.1:8000**

You will be redirected to the login page.

---

## Admin Panel

The Django admin panel is available at:

**http://127.0.0.1:8000/admin/**

Log in with your superuser credentials to manage all users, projects, tasks, and comments.

---

## Stopping the Server

Press `Ctrl + C` in the terminal to stop the server.

---

## Restarting Later

Every time you return to work on the project:

**macOS / Linux:**
```bash
cd path/to/taskhive
source venv/bin/activate
python manage.py runserver
```

**Windows:**
```cmd
cd path\to\taskhive
venv\Scripts\activate
python manage.py runserver
```

---

## Troubleshooting

### "Module not found" errors
Make sure your virtual environment is activated (`(venv)` in prompt) and you have run `pip install -r requirements.txt`.

### "No module named django"
```bash
pip install django
```

### Database errors / missing tables
```bash
python manage.py migrate
```

### Static files not loading
```bash
python manage.py collectstatic
```
Then reload the page with `Ctrl+Shift+R` to clear browser cache.

### Port already in use
```bash
python manage.py runserver 8080
```
Then visit: http://127.0.0.1:8080

### Windows PowerShell execution policy error
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Pillow installation fails on Windows
```cmd
pip install Pillow --pre
```

---

## Resetting the Database

To start fresh:

```bash
# Delete the database
del db.sqlite3          # Windows
rm db.sqlite3           # macOS/Linux

# Re-run migrations
python manage.py migrate

# Create admin
python manage.py createsuperuser

# Reload demo data
python manage.py seed_data
```

---

## Useful Management Commands

| Command | Description |
|---|---|
| `python manage.py migrate` | Apply database migrations |
| `python manage.py createsuperuser` | Create admin account |
| `python manage.py seed_data` | Load demo data |
| `python manage.py shell` | Open Django interactive shell |
| `python manage.py collectstatic` | Collect static files |
| `python manage.py runserver` | Start dev server on port 8000 |
| `python manage.py runserver 8080` | Start on custom port |
| `python manage.py dbshell` | Open SQLite shell |

---

## Environment

All data is stored in `db.sqlite3` in the project root.
No internet connection required after initial setup.
No cloud services. No Docker. Runs 100% locally.
