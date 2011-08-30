DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'my_db', 
        }
    }
INSTALLED_APPS = ['key', 'django.contrib.auth', 'django.contrib.contenttypes', 'django.contrib.sessions', 'django.contrib.admin']


ROOT_URLCONF = 'key.urls'
