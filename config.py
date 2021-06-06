# DATABASE SETTINGS
import configparser
import socket
import os
from oauth2client.service_account import ServiceAccountCredentials
import json

hostname = socket.gethostname()
host = None
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
# Chuns-MacBook-Air.local

if  os.environ.get('DEPLOY_TYPE', None) == "HEROKU":
    host = "HEROKU"
elif hostname[:5] == "vultr":
    host = "VULTR"
else:
    host = "LOCAL"

DEPLOY_HOST = host



if host == "LOCAL" or host == "VULTR":
    print(host)
    config = configparser.ConfigParser()
    config.read('config.ini')

    pg_db_username = config[host]['LOCAL_DB_USERNAME']
    pg_db_password = config[host]['LOCAL_DB_PASSWORD']
    pg_db_name = config[host]['LOCAL_DB_NAME']
    pg_db_hostname = config[host]['LOCAL_DB_HOSTNAME']

    SQLALCHEMY_DATABASE_URI = "postgresql://{DB_USER}:{DB_PASS}@{DB_ADDR}/{DB_NAME}".format(DB_USER=pg_db_username,
                                                                                            DB_PASS=pg_db_password,
                                                                                            DB_ADDR=pg_db_hostname,
                                                                                            DB_NAME=pg_db_name)

    DEBUG = False
    PORT = 5000
    HOST = "0.0.0.0"
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = config[host]['SECRET_KEY']
    DISCORD_WEBHOOK_URL = config[host]['DISCORD_WEBHOOK_URL']

    REDIS_URL = config[host]['REDIS_URL']

    GOOGLE_CREDENTIALS = ServiceAccountCredentials.from_json_keyfile_name(config[host]['GOOGLE_CREDENTIALS_PATH'],
                                                                          scope)

    FIREBASE_CREDENTIALS_PATH = config[host]['FIREBASE_CREDENTIALS_PATH']

    MAIL_ID = config[host]["MAIL_ID"]
    MAIL_PASSWORD = config[host]["MAIL_PASSWORD"]

    NEIS_KEY = config[host]["NEIS_KEY"]

    if host == "LOCAL":
        TEMPLATES_AUTO_RELOAD = True
    else:
        pass

else:
    pg_db_username = 'yeah'
    pg_db_password = 'yeah'
    pg_db_name = 'yeah'
    pg_db_hostname = 'yeah'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', None)

    DEBUG = False
    PORT = 5000
    HOST = "127.0.0.1"
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = os.environ.get('SECRET_KEY', None)

    GOOGLE_CREDENTIALS = ServiceAccountCredentials.from_json_keyfile_dict(
        json.loads(os.environ.get('GOOGLE_CREDENTIALS', None)), scope)

    DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL', None)

    REDIS_URL = os.environ.get('REDIS_URL', None)

    NEIS_KEY = os.environ.get("NEIS_KEY", None)

    FIREBASE_CREDENTIALS_PATH = None

    MAIL_ID = os.environ.get("MAIL_ID", None)
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", None)

MAX_CONTENT_LENGTH = 5 * 1024 * 1024
ADMIN_ID = os.environ.get('ADMIN_ID', None)
ADMIN_PW = os.environ.get('ADMIN_PW', None)


ACCESS_TOKEN_LIFE = 24 * 60 * 60 * 30
REFRESH_TOKEN_LIFE = 60 * 60 * 24 * 21

# ACCESS_TOKEN_LIFE = 30
# REFRESH_TOKEN_LIFE = 5
