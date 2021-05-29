
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from datetime import timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '-$4r+c*pwl8-$#0-sl*dm8+u_j@%q5ad55gfb-f$v!8!5epk*z'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOST = ['127.0.0.1', 'localhost']
ALLOWED_HOSTS = ['k03q.azurewebsites.net']
CORS_ORIGIN_ALLOW_ALL = True
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin', 'django.contrib.auth',
    'django.contrib.contenttypes', 'django.contrib.sessions',
    'django.contrib.messages', 'django.contrib.staticfiles', 'account', 'post',
    'rest_framework', 'community', 'chat', 'corsheaders',
    'rest_framework.authtoken','track','chatv0','channels','notify'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'redditv1.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'), os.path.join(BASE_DIR, 'reddiv1', 'templates', 'reddiv1')],
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

WSGI_APPLICATION = 'redditv1.wsgi.application'
ASGI_APPLICATION = 'redditv1.asgi.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

# DATABASES = {
#     'default': {
#         # test3
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'test3',
#         'USER': 'postgres',
#         'PASSWORD': 'password',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }

DATABASES = {
    'default': {
        # test3
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'pollsdb',
        'USER': 'tuantran@social-network',
        'PASSWORD': 'Dongha2030@',
        'HOST': 'social-network.postgres.database.azure.com',
        'PORT': '5432',
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    # {
    #     'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    # },
]

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'

DEFAULT_RENDERER_CLASSES = [
    'rest_framework.renderers.JSONRenderer',
]

DEFAULT_AUTHENTICATION_CLASSES = [
    'rest_framework.authentication.SessionAuthentication',
    'rest_framework.authentication.TokenAuthentication',
    'rest_framework_simplejwt.authentication.JWTAuthentication',
]

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=10080),
    'REFRESH_TOKEN_LIFETIME ': timedelta(minutes=120),
}

if DEBUG:
    DEFAULT_RENDERER_CLASSES += [
        'rest_framework.renderers.BrowsableAPIRenderer',
    ]

    DEFAULT_AUTHENTICATION_CLASSES += [

        # 'redditv1.dev_auth.dev.DevAuthentication'
        # 'rest_framework.authentication.SessionAuthentication',
    ]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': DEFAULT_AUTHENTICATION_CLASSES,
    'DEFAULT_RENDERER_CLASSES': DEFAULT_RENDERER_CLASSES
}

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join(BASE_DIR, "static-root")
