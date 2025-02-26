import pytest
from datetime import datetime, timedelta
from src.fitnesstracker import create_app, db
from src.fitnesstracker.models import User, Template, TemplateExercise, TrainingSession, Exercise, ExerciseDetails

@pytest.fixture
def app():
    app = create_app(environment='testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def authenticated_user(app, client):
    with app.app_context():
        # Create a test user
        user = User(username='testuser', email='testuser@example.com', password='password123')
        db.session.add(user)
        db.session.commit()
        
        # Log the user in
        client.post('/login', data={
            'email': 'testuser@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        
        yield user
        
        # Clean up
        db.session.delete(user)
        db.session.commit()

@pytest.fixture
def workout_template(app, authenticated_user):
    with app.app_context():
        template = Template(
            name='Test Workout',
            user_id=authenticated_user.id
        )
        db.session.add(template)
        db.session.flush()
        
        # Add exercises to template
        exercises = [
            TemplateExercise(template_id=template.id, exercise='Bench Press'),
            TemplateExercise(template_id=template.id, exercise='Squat'),
            TemplateExercise(template_id=template.id, exercise='Deadlift')
        ]
        db.session.add_all(exercises)
        db.session.commit()
        
        return template

def test_home_redirect_when_not_logged_in(client):
    response = client.get('/')
    assert response.status_code == 302  # redirect to login
    assert b'/login' in response.data

def test_login_page(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data

def test_register_page(client):
    response = client.get('/register')
    assert response.status_code == 200
    assert b'Register' in response.data

def test_successful_registration(client, app):
    # First, get the registration page to extract CSRF token if needed
    reg_page = client.get('/register')
    
    # Create registration data
    reg_data = {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    }
    
    # Submit the registration form
    response = client.post('/register', data=reg_data, follow_redirects=True)
    
    # Print response for debugging
    print(f"Response status: {response.status_code}")
    print(f"Response data: {response.data.decode()}")
    
    # Check response
    assert response.status_code == 200

    # Verify user was created
    with app.app_context():
        user = User.query.filter_by(email='newuser@example.com').first()
        if user is None:
            print("User not found in database")
        assert user is not None
        assert user.username == 'newuser'
