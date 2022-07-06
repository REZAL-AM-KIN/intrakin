from os import environ, getenv

from intra.settings import BASE_DIR
from intra.settings import RADIUS

LOCALDB = getenv("LOCALDB","True") == "True"
RADIUS = getenv("RADIUS", "False") == "True"

if LOCALDB:
    DB_SETTINGS = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(BASE_DIR / "db.sqlite3"),
    }
else:
    DB_SETTINGS = {
        "NAME": environ["DB_NAME"],
        "ENGINE": "django.db.backends.mysql",
        "USER": environ["DB_USERNAME"],
        "PASSWORD": environ["DB_PASSWORD"],
        "HOST": environ["DB_ADDR"],
    }    

if RADIUS:
    RADIUS_SETTINGS = {
        'NAME': 'radius',
        'ENGINE': 'django.db.backends.mysql',
        'USER': environ["RADIUS_USERNAME"],
        'PASSWORD': environ["RADIUS_PASSWORD"],
        'HOST': environ["RADIUS_ADDR"],
    }