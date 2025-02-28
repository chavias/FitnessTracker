import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', '6f1d9450164dda48f7fac81a7f4a89c5bff52d841050b71897b6da8c3a46e5fd')
    SQLALCHEMY_TRACK_MODIFICATIONS = str(os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', 'False')).lower() in ('false', '0', 'f')
    WTF_CSRF_TIME_LIMIT = None
    PERMANENT_SESSION_LIFETIME = timedelta(hours=12)
    MAIL_USERNAME=os.getenv('EMAIL_USER')
    MAIL_PASSWORD=os.getenv('EMAIL_PASS')
    MAIL_SERVER=os.getenv('MAIL_SERVER')
    MAIL_PORT=os.getenv('MAIL_PORT')
    MAIL_USE_TLS=str(os.getenv('TLS')).lower() in ('true', '1', 't')
    MAIL_USE_SSL=str(os.getenv('SSL')).lower() in ('true', '1', 't')
    MAIL_DEFAULT_SENDER=os.getenv('MAIL_DEFAULT_SENDER')


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///fitness.db'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=12)


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')    
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')
    PERMANENT_SESSION_LIFETIME = timedelta(hours=12)
    WTF_CSRF_TIME_LIMIT = None


class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=12)
    WTF_CSRF_ENABLED = False
    TESTING = True
