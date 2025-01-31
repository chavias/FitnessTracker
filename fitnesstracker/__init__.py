from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from datetime import timedelta

load_dotenv()

app = Flask(__name__)

# app.config['SECRET_KEY'] ='34110d22dfd1e0ac02ddca391a1db27f'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fitness.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=4)

@app.before_request
def make_session_permanent():
    session.permanent = True


db = SQLAlchemy(app)
from fitnesstracker import routes