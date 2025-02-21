import os
from datetime import timedelta



class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', '6f1d9450164dda48f7fac81a7f4a89c5bff52d841050b71897b6da8c3a46e5fd')
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', False)
    WTF_CSRF_TIME_LIMIT = None
    PERMANENT_SESSION_LIFETIME = timedelta(hours=12)


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///fitness.db'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=12)


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')    
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')
    PERMANENT_SESSION_LIFETIME = timedelta(hours=12)
    WTF_CSRF_TIME_LIMIT = None


class TestingConfig(Config):
    # SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///fitness.db')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///fitness.db'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=12)
    TESTING = True
