from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from fitnesstracker.config import DevelopmentConfig, ProductionConfig, TestingConfig
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

# load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()
# login_manager.login_view = 'users.login'

login_manager.blueprint_login_views = {
    'users': '/users/login',
}

login_manager.login_message_category = 'info'
mail = Mail()


<<<<<<< HEAD:fitnesstracker/__init__.py
def create_app(environment='development'):

    app = Flask(__name__)
    
    if environment == 'production':
=======
def create_app(environment='mariadb'):

    app = Flask(__name__)
    
    if environment == 'mariadb':
        print('Using MariaDB')
>>>>>>> testing:src/fitnesstracker/__init__.py
        app.config.from_object(ProductionConfig)
    elif environment == 'testing':
        app.config.from_object(TestingConfig)
    else:
        print('Using SQLite')
        app.config.from_object(DevelopmentConfig)
<<<<<<< HEAD:fitnesstracker/__init__.py
    
=======


>>>>>>> testing:src/fitnesstracker/__init__.py
    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

<<<<<<< HEAD:fitnesstracker/__init__.py
    @app.before_request
    def make_session_permanent():
        session.permanent = True
        
    @app.before_request
    def upgrade_databank():
        if environment != 'production':
            db.create_all()

=======
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
    
    @app.before_request
    def make_session_permanent():
        session.permanent = True
    
>>>>>>> testing:src/fitnesstracker/__init__.py
    from fitnesstracker.main.routes import main
    from fitnesstracker.users.routes import users
    from fitnesstracker.workout_templates.routes import workout_templates
    from fitnesstracker.workout_sessions.routes import workout_sessions
    from fitnesstracker.workout_statistics.routes import workout_statistics
    
    app.register_blueprint(main)
    app.register_blueprint(users)
    app.register_blueprint(workout_templates)
    app.register_blueprint(workout_sessions)
    app.register_blueprint(workout_statistics)

    return app