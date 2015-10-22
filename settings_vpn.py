# Django settings for catalog project.
import os
dirname = os.path.dirname(globals()["__file__"])


DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

#===============================================================================
#DATABASE_ENGINE = 'mysql'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
#DATABASE_NAME = 'catalog'             # Or path to database file if using sqlite3.
#DATABASE_USER = 'django'             # Not used with sqlite3.
#DATABASE_PASSWORD = 'djangodjango'         # Not used with sqlite3.
#DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
#DATABASE_PORT = '3306'             # Set to empty string for default. Not used with sqlite3.
#===============================================================================

DATABASE_ENGINE = 'mysql'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'rivelo'             # Or path to database file if using sqlite3.
DATABASE_USER = 'rivelo'             # Not used with sqlite3.
DATABASE_PASSWORD = 'Pnj5i5zjF6uC7nv'         # Not used with sqlite3.
#DATABASE_HOST = '195.154.74.135'             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_HOST = '192.168.88.1'             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = '3306'             # Set to empty string for default. Not used with sqlite3.


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
#TIME_ZONE = 'America/Chicago'
TIME_ZONE = 'Europe/Kiev'
DATE_FORMAT = 'd/m/Y'
DATETIME_FORMAT = 'D d M Y'
SHORT_DATE_FORMAT = 'd/m/Y'
SHORT_DATETIME_FORMAT = 'd/m/Y'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
DEFAULT_FROM_EMAIL = 'user@domain.com'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'velorivne@gmail.com'
EMAIL_HOST_PASSWORD = 'gvelovelo'
EMAIL_PORT = 587

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
#MEDIA_ROOT = 'd:/develop/catalog/media/'
MEDIA_ROOT = os.path.join(dirname, 'media/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = "/media/"

STATIC_ROOT = os.path.join(dirname, 'static_root/')
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static'),
)
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)


# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
#ADMIN_MEDIA_PREFIX = '/static/'


# Make this unique, and don't share it with anybody.
SECRET_KEY = 'zmjw9-ks9=p=9(mcoeq#uk89q6vgf2twyi4d(n0(_5wppi)i(u'

# List of callables that know how to import templates from various sources.
if DEBUG:
    TEMPLATE_LOADERS = [
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',      
    ]
else:
    TEMPLATE_LOADERS = [
    ('django.template.loaders.cached.Loader',(
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
        'forum.modules.template_loader.module_templates_loader',
        'forum.skins.load_template_source',
        )),
    ]

#TEMPLATE_LOADERS = (
#    'django.template.loaders.filesystem.load_template_source',
#    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
#)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
#    'django.middleware.csrf.CsrfViewMiddleware',
)

ROOT_URLCONF = 'catalog.urls'

#TEMPLATE_DIRS = (
#    'd:/develop/catalog/templates',
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
#)


TEMPLATE_DIRS = (
    os.path.join(dirname, 'templates'),
    #"D:/development/mysite/templates/",
    #"/templates/admin",
    #"/mysite/templates/",
    #"/templates/",
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.media",
    
    'django.contrib.messages.context_processors.messages',
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",
    'django.core.context_processors.request',
)

INSTALLED_APPS = (
    'django.contrib.admin',                  
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'django.contrib.staticfiles',
    'django.contrib.admindocs',
    'catalog.accounting',
    
)

