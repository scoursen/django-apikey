from django.conf import settings

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'my_db', 
        }
    }
INSTALLED_APPS = ['key', 'django.contrib.auth', 'django.contrib.contenttypes', 'django.contrib.sessions', 'django.contrib.admin']


ROOT_URLCONF = 'key.urls'

MAX_KEYS = getattr(settings, 'APIKEY_MAX_KEYS', -1)
KEY_SIZE = getattr(settings, 'APIKEY_KEY_SIZE', 32)
USE_API_GROUP = getattr(settings, 'APIKEY_USE_API_GROUP', False)
AUTH_HEADER =  getattr(settings, 'APIKEY_AUTHORIZATION_HEADER', 'X-Api-Authorization')

