@echo off
title TaskHive – Starting...
color 0A

echo.
echo  ============================================
echo   TaskHive - Collaborative Task Manager
echo  ============================================
echo.

cd /d "%~dp0"
echo  Working directory: %CD%
echo.

echo  [1/8] Checking Python...
python --version
if %errorlevel% neq 0 (
    color 0C
    echo.
    echo  ERROR: Python not found!
    echo  Install Python 3.10+ from https://python.org
    echo  Make sure to check "Add Python to PATH" during install.
    echo.
    pause
    exit /b 1
)
echo.

echo  [2/8] Installing dependencies...
pip install -r requirements.txt --quiet
echo  Done.
echo.

echo  [3/8] Wiping old database for fresh start...
if exist db.sqlite3 (
    del /f /q db.sqlite3
    echo  Old database deleted.
) else (
    echo  No old database found.
)
echo.

echo  [4/8] Clearing old migration files...
if exist "users\migrations\0001_initial.py"    del /f /q "users\migrations\0001_initial.py"
if exist "users\migrations\0002_initial.py"    del /f /q "users\migrations\0002_initial.py"
if exist "projects\migrations\0001_initial.py" del /f /q "projects\migrations\0001_initial.py"
if exist "projects\migrations\0002_initial.py" del /f /q "projects\migrations\0002_initial.py"
if exist "tasks\migrations\0001_initial.py"    del /f /q "tasks\migrations\0001_initial.py"
if exist "tasks\migrations\0002_initial.py"    del /f /q "tasks\migrations\0002_initial.py"
if exist "comments\migrations\0001_initial.py" del /f /q "comments\migrations\0001_initial.py"
if exist "comments\migrations\0002_initial.py" del /f /q "comments\migrations\0002_initial.py"
echo  Migration files cleared.
echo.

echo  [5/8] Creating migrations...

echo  - users
python manage.py makemigrations users
if %errorlevel% neq 0 (
    color 0C
    echo.
    echo  ERROR: makemigrations users failed!
    echo.
    pause
    exit /b 1
)

echo  - projects
python manage.py makemigrations projects
if %errorlevel% neq 0 (
    color 0C
    echo.
    echo  ERROR: makemigrations projects failed!
    echo.
    pause
    exit /b 1
)

echo  - tasks
python manage.py makemigrations tasks
if %errorlevel% neq 0 (
    color 0C
    echo.
    echo  ERROR: makemigrations tasks failed!
    echo.
    pause
    exit /b 1
)

echo  - comments
python manage.py makemigrations comments
if %errorlevel% neq 0 (
    color 0C
    echo.
    echo  ERROR: makemigrations comments failed!
    echo.
    pause
    exit /b 1
)

echo  All migrations created.
echo.

echo  [6/8] Applying migrations...
python manage.py migrate
if %errorlevel% neq 0 (
    color 0C
    echo.
    echo  ERROR: migrate failed!
    echo.
    pause
    exit /b 1
)
echo  Database ready.
echo.

echo  [7/8] Loading demo data...
python manage.py seed_data
echo  Demo data loaded.
echo.

echo  [8/8] Launching browser in 3 seconds...
timeout /t 3 /nobreak >nul
start "" "http://127.0.0.1:8000"
echo  Browser opened.
echo.

echo  ============================================
echo   TaskHive is RUNNING
echo   URL   : http://127.0.0.1:8000
echo   Admin : http://127.0.0.1:8000/admin/
echo  --------------------------------------------
echo   DEMO LOGINS:
echo     Username: admin   Password: admin123
echo     Username: sarah   Password: demo1234
echo     Username: alex    Password: demo1234
echo  --------------------------------------------
echo   Press CTRL+C to stop the server
echo  ============================================
echo.

python manage.py runserver 8000

echo.
echo  ============================================
echo   Server has stopped.
echo  ============================================
echo.
pause
