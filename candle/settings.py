"""
Django settings for candle project.

Generated by 'django-admin startproject' using Django 3.0.8.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

import django.db.models
from dotenv import load_dotenv


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR,'.env'))



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['silentwrangler.pythonanywhere.com',
 'worldofcandle.club','portal.worldofcandle.club' , 'localhost' ]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'players',
    'world',
    'forum',
    'precise_bbcode',
    'rest_framework',
   # 'background_task',
    'rest_framework.authtoken',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'candle.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'world.context_processors.active_world',
                'players.context_processors.active_character',
                'players.context_processors.api_auth_token',
            ],
        },
    },
]

WSGI_APPLICATION = 'candle.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_BACK'),
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASS'),
        'HOST': os.getenv('DB_HOST'),
        'TEST':{
            'ENGINE': os.getenv('TEST_DB_BACK'),
            'NAME': os.getenv('TEST_DB_NAME'),
        },
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
#Email




#EMAIL_BACKEND = "anymail.backends.sendinblue.EmailBackend"
#ANYMAIL = {
#    "SENDINBLUE_API_KEY": os.getenv('SENDINBLUE_API_KEY'),
#}


DEFAULT_FROM_EMAIL = 'noreply@worldofcandle.club'
#REST API

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES':[
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        ]
    }

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


AUTH_USER_MODEL = 'players.Player'
LOGOUT_REDIRECT_URL = 'home'
# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = [
    f'{BASE_DIR}/locale',
    ]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR,'static/')
STATIC_URL = '/static/'

MEDIA_ROOT = '/usr/share/candle/media/'
MEDIA_URL = '/media/'

#CSRF

CSRF_TRUSTED_ORIGINS = ['https://silentwrangler.pythonanywhere.com',
 'https://*.worldofcandle.club' , 'https://localhost' ]
CSRF_COOKIE_DOMAIN = '.worldofcandle.club'
#Candle-specific

#list of modules contatining do_time_step() function
TIMESTEP_MODULES = [
    'world.logic',
    'players.logic',
    ]

PROJECT_PROCESSORS =[
    'players.projects',
    'world.projects'
]



