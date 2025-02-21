from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from fitnesstracker.config import DevelopmentConfig, ProductionConfig, TestingConfig
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail


load_dotenv()

db = SQLAlchemy()
migrate = Migrate()

bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
mail = Mail()


def create_app(enviroment='development'):

    app = Flask(__name__)
    
    if enviroment == 'production':
        app.config.from_object(ProductionConfig)
    elif enviroment == 'testing':
        app.config.from_object(TestingConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)


    @app.before_request
    def make_session_permanent():
        session.permanent = True

    from fitnesstracker.workout_templates.routes import workout_templates
    from fitnesstracker.workout_sessions.routes import workout_sessions
    from fitnesstracker.main.routes import main
    from fitnesstracker.workout_statistics.routes import workout_statistics
    app.register_blueprint(workout_sessions)
    app.register_blueprint(workout_templates)
    app.register_blueprint(workout_statistics)
    app.register_blueprint(main)

    return app