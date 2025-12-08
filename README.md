# fsd_project_final

Local setup and run instructions for the Django project.

Prerequisites
- Git (optional)
- Python 3.10+ (this project was tested with the workspace venv)
- On Windows: Visual C++ Build Tools may be required to install `mysqlclient`.

Quickstart (recommended for local dev using bundled SQLite)

1. Activate the virtualenv (PowerShell):

```powershell
& D:/finalproject/fsd_project_final/.venv/Scripts/Activate.ps1
```

2. Install requirements (if not already installed):

```powershell
D:/finalproject/fsd_project_final/.venv/Scripts/python.exe -m pip install -r requirements.txt
```

3. Use SQLite for local development (recommended):

```powershell
# This tells Django to use the bundled db.sqlite3 instead of MySQL
$env:USE_SQLITE = '1'
D:/finalproject/fsd_project_final/.venv/Scripts/python.exe manage.py migrate
D:/finalproject/fsd_project_final/.venv/Scripts/python.exe manage.py runserver
```

4. Create a superuser (optional):

```powershell
D:/finalproject/fsd_project_final/.venv/Scripts/python.exe manage.py createsuperuser
```

Using MySQL instead of SQLite

1. If you prefer MySQL, ensure a MySQL server is available and the `DATABASES`
   settings in `mysite/settings.py` match your server credentials.

2. Install `mysqlclient` (may require build tools on Windows):

```powershell
# Activate venv first
D:/finalproject/fsd_project_final/.venv/Scripts/python.exe -m pip install mysqlclient
```

If you cannot install `mysqlclient`, you can use `mysql-connector-python` instead
by changing the engine in `mysite/settings.py` to `mysql.connector.django` and
ensuring `mysql-connector-python` is installed (this project already includes
`mysql-connector-python` in `requirements.txt`).

Environment-driven DB selection

- The project reads the environment variable `USE_SQLITE`. If set to `1`,
  `true`, or `yes` (case-insensitive), Django will use `db.sqlite3` locally.
- If `USE_SQLITE` is not set, the project defaults to SQLite when `DEBUG=True`.

Troubleshooting

- `ModuleNotFoundError: No module named 'MySQLdb'` — you need `mysqlclient`.
- On Windows, installing `mysqlclient` may require Visual C++ build tools or a
  compatible wheel for your Python version. If installation fails, switch to
  `USE_SQLITE=1` or use the `mysql-connector-python` backend as described above.

Contact
- Ask the project maintainer or your collaborator if you need the exact
  MySQL credentials or a dump of the production database.
