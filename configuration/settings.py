# Fichiers de configuration principaux de Django - django_project ajustés pour une plateforme d'apprentissage en ligne

import os
from pathlib import Path

# Construire les chemins de base
BASE_DIR = Path(__file__).resolve().parent.parent

# Paramètres de sécurité - utiliser les variables d'environnement en production
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-dev-key-changer-en-production')

# Contrôles d'accès
DEBUG = os.environ.get('DJANGO_DEBUG', 'true').lower() == 'true'
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver', '.pythonanywhere.com']

# Application définissant l'API visuelle
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Nos applications métier
    'app_web',
    'app_algs',
    'app_python',
]

# Modèle d'utilisateur personnalisé (authentification par e-mail)
AUTH_USER_MODEL = 'app_web.Utilisateur'

# Connexion par e-mail ou téléphone (app_web.authentication)
AUTHENTICATION_BACKENDS = [
    'app_web.authentication.BackendEmailTelephone',
    'django.contrib.auth.backends.ModelBackend',
]

# Middleware gérant les requêtes
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'app_web.middleware.RestreindreAdminMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Configuration de l'URL principal
ROOT_URLCONF = 'configuration.urls'

# Configuration du template
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Configuration WSGI
WSGI_APPLICATION = 'configuration.wsgi.application'

# Configuration de la base de données
# - SQLite par défaut (zéro configuration, parfait pour PythonAnywhere)
# - PostgreSQL si les variables DATABASE_* ou DATABASE_URL sont définies
if os.environ.get('DATABASE_NAME') or os.environ.get('DATABASE_URL'):
    if os.environ.get('DATABASE_URL'):
        import dj_database_url

        DATABASES = {'default': dj_database_url.parse(os.environ['DATABASE_URL'], conn_max_age=60)}
    else:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': os.environ['DATABASE_NAME'],
                'USER': os.environ.get('DATABASE_USER', 'plateforme_user'),
                'PASSWORD': os.environ.get('DATABASE_PASSWORD', ''),
                'HOST': os.environ.get('DATABASE_HOST', 'localhost'),
                'PORT': os.environ.get('DATABASE_PORT', '5432'),
                'CONN_MAX_AGE': 60,
            }
        }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Configuration de la validation des mots de passe
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Configuration internationale
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_TZ = True

# Fichiers statiques (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Fichiers média (photos de profil, images de couverture, vidéos...)
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Gestionnaire de fichiers par défaut
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Type de session
session_engine = 'django.contrib.sessions.backends.db'

# Suivi des utilisateurs
LOGIN_REDIRECT_URL = 'app_web:accueil'
LOGIN_URL = 'app_web:connexion'

# Messages
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'error',
}

# Frames : autoriser les iframes de même origine (débloque le lecteur PDF intégré)
X_FRAME_OPTIONS = 'SAMEORIGIN'