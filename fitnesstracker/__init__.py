from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from fitnesstracker.config import DevelopmentConfig, ProductionConfig, TestingConfig

load_dotenv()

db = SQLAlchemy()

def create_app(enviroment='development'):

    app = Flask(__name__)
    
    if enviroment == 'production':
        app.config.from_object(ProductionConfig)
    elif enviroment == 'testing':
        app.config.from_object(TestingConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    db.init_app(app)

    @app.before_request
    def make_session_permanent():
        session.permanent = True

    from fitnesstracker.workout_templates.routes import workout_templates
    from fitnesstracker.workout_sessions.routes import workout_sessions
    from fitnesstracker.main.routes import main
    app.register_blueprint(workout_sessions)
    app.register_blueprint(workout_templates)
    app.register_blueprint(main)

    return app