import dj_database_url

from .development import *

CSRF_TRUSTED_ORIGINS = ['https://awa.up.railway.app']
# Update database configuration from DATABASE_URL environment variable.
# Django will use the default database during development, unless DATABASE_URL is set
db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(db_from_env)

STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
