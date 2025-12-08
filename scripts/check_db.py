import os
import sys

# Make sure this script runs from project root
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE not in sys.path:
    sys.path.insert(0, BASE)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

try:
    import django
    django.setup()
except Exception as e:
    print('ERROR: Django setup failed:', e)
    sys.exit(2)

from django.conf import settings
from django.db import connections, OperationalError, DEFAULT_DB_ALIAS

print('Configured DB settings (default):')
conf = settings.DATABASES.get('default', {})
# Avoid printing password in interactive output for safety; show keys except password
conf_safe = {k: (v if k != 'PASSWORD' else '*****') for k, v in conf.items()}
print(conf_safe)

# Try a direct connection
try:
    conn = connections[DEFAULT_DB_ALIAS]
    # ensure connection initialization
    cursor = conn.cursor()
    cursor.execute('SELECT DATABASE()')
    dbname = cursor.fetchone()[0]
    print('Connected to database name returned by server:', dbname)
    # count users table rows as additional check
    try:
        cursor.execute("SELECT COUNT(*) FROM auth_user")
        user_count = cursor.fetchone()[0]
        print('auth_user row count:', user_count)
    except Exception as e:
        print('Could not query auth_user table (maybe migrations not applied?):', e)
    conn.close()
    sys.exit(0)
except OperationalError as oe:
    print('OperationalError: could not connect to the database server.')
    print('Details:', oe)
    print('Common causes: MySQL server not running, wrong credentials, missing DB, or missing mysqlclient in venv.')
    sys.exit(3)
except Exception as e:
    print('Unexpected error when connecting to DB:', type(e), e)
    sys.exit(4)
