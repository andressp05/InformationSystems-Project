#!/bin/bash

PROJECT="proyecto"
APP="aplicacion"
DB="examen"
URL="urlautogenerada$RANDOM$RANDOM"

export PGPASSWORD=alumnodb
dropdb -U alumnodb -h localhost $DB
if ! cd "$(dirname ${BASH_SOURCE[0]})" ; then
    echo "Error al iniciar el script"
    exit
fi

if ! django-admin startproject $PROJECT ; then
    echo "Error al inciar el proyecto"
    exit
fi

echo "Proyecto $PROJECT creado con exito"

if ! cd $PROJECT ; then
    echo "Error al intentar acceder al directorio del proyecto"
    exit
fi

if ! python3 manage.py  startapp $APP ; then
    echo "Error al intentar crear la aplicacion"
    exit
fi

echo "Aplicacion $APP creada con exito"

if ! createdb -U alumnodb -h localhost $DB ; then
    echo "Error al intentar crear la base de datos"
    exit
fi

echo "Base de datos $DB creada con exito"

mkdir templates
touch templates/a
mkdir static
touch static/a
git init
echo "INTRODUCE TUS CREDENCIALES DE HEROKU:"
heroku login
heroku create $URL

echo "Git inicializado, heroku logueado y aplicacion creada"

printf "release: python3 manage.py migrate\nweb: gunicorn $PROJECT.wsgi --log-file -" > Procfile
printf "python-3.6.8" > runtime.txt
printf "coverage==4.5.3\ndj-database-url==0.5.0\ndj-static==0.0.6\nDjango==2.1.7\nentrypoints==0.2.3\nflake8==3.7.7\ngunicorn==19.8.1\nimagesize==0.7.1\nmccabe==0.6.1\nPillow==5.1.0\npsycopg2==2.7.7\npsycopg2-binary==2.7.7\npycodestyle==2.3.1\npyflakes==1.6.0\npytz==2019.1\nstatic3==0.7.0" > requirements.txt

echo "Ficheros Procfile, runtime.txt y requirements.txt creado"

printf  "from django.core.wsgi import get_wsgi_application\nfrom dj_static import Cling\nimport os\nos.environ.setdefault(\"DJANGO_SETTINGS_MODULE\", \"$PROJECT.settings\")\napplication = get_wsgi_application()\napplication = Cling(get_wsgi_application())"> $PROJECT/wsgi.py 

echo "Fichero wsgi cambiado"

cat << EOF > ./$PROJECT/settings.py
"""
Django settings for project project.

Generated by 'django-admin startproject' using Django 1.11.16.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
import dj_database_url

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
DATABASE_URL='postgres://alumnodb:alumnodb@localhost:5432/$DB'
STATIC_DIR = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [STATIC_DIR, ]
STATIC_ROOT = 'staticfiles'
ALLOWED_HOSTS = [u'$URL.herokuapp.com', u'localhost', u'127.0.0.1']

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '2trhuh8*7@+ogrud^(uni9gb&!&i231yqurc%zb)v_fokv-0_s'
DATABASES={}
if os.getenv('SQLITE',False):
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
else:
    DATABASES['default']= dj_database_url.config(default=DATABASE_URL)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True



# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    '$APP',
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

ROOT_URLCONF = '$PROJECT.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR, ],
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

WSGI_APPLICATION = '$PROJECT.wsgi.application'


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

EOF


python3 manage.py migrate
echo "INTRODUCE LAS CREDENCIALES DEL SUPERUSUARIO"
python3 manage.py createsuperuser
echo "Super usuario creado"
git config --global user.email "tu email"
git config --global user.name "tu nombre"
git add -A && git commit -m 'autogenerado' && git push heroku master








