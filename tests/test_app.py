import pytest
from datetime import datetime, timedelta
from fitnesstracker import create_app, db, bcrypt
from fitnesstracker.models import User, Template, TemplateExercise, TrainingSession, Exercise, ExerciseDetails

@pytest.fixture
def app():
    app = create_app(environment='testing')
    with app.app_context():
        db.create_all()  # This is where the database is created
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def authenticated_user(app, client):
    with app.app_context():
        # Create a test user
        user = User(username='testuser', email='testuser@example.com', password=bcrypt.generate_password_hash('password123'))
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
        
        yield template
        
        # Clean up
        db.session.delete(template)
        # Also delete related exercises
        TemplateExercise.query.filter_by(template_id=template.id).delete()
        db.session.commit()

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
    response = client.get('/register')
    response = client.post('/register', data={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'password123',
        'confirm_password': 'password123',

    }, follow_redirects=True)
    
    assert response.status_code == 200
    with app.app_context():
        user = User.query.filter_by(email='newuser@example.com').first()
        assert user is not None

def test_profile_page(client, authenticated_user):
    response = client.get('/account')
    assert response.status_code == 200
    assert authenticated_user.username.encode() in response.data

def test_logout(client, authenticated_user):
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data

def test_create_workout_template(client, authenticated_user):
    response = client.post('/create_template', data={
        'template_name': 'New Template',
        'exercises-0-exercise_name' : 'New Exercise'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'New Template' in response.data
    assert b'New Exercise' in response.data


def test_start_training_session(client, authenticated_user, workout_template):
    response = client.post('/create_session', data={
        'template_id': workout_template.id,
    }, follow_redirects=True)
    assert response.status_code == 200
    print(f"{response.data}")
    assert b'Test Workout' in response.data


# def test_progression_api(client, authenticated_user, app):
#     # Create some test data for exercise progression
#     with app.app_context():
#         # Create training sessions with different dates
#         for i in range(3):
#             date = datetime.utcnow() - timedelta(days=10-i)
#             session = TrainingSession(
#                 date=date,
#                 user_id=authenticated_user.id
#             )
#             db.session.add(session)
#             db.session.flush()
            
#             # Add bench press exercise to each session
#             bench_press = Exercise(
#                 session_id=session.id,
#                 exercise_name='Bench Press'
#             )
#             db.session.add(bench_press)
#             db.session.flush()
            
#             # Add sets with increasing weights
#             for j in range(3):
#                 details = ExerciseDetails(
#                     exercise_id=bench_press.id,
#                     repetitions=8,
#                     weight=60 + (i*5)  # Weight increases over sessions
#                 )
#                 db.session.add(details)
        
#         db.session.commit()

#             # Test the API endpoint
#     response = client.get('/api/progression?exercise=Bench Press')
#     assert response.status_code == 200
#     data = response.get_json()
#     assert isinstance(data, list)
#     assert len(data) > 0
    
#     # Check data structure
#     assert 'date' in data[0] or 'Date' in data[0]
#     assert 'weight' in data[0] or 'Weight' in data[0]
    
#     # Check data is in ascending date order
#     dates = [entry.get('date', entry.get('Date')) for entry in data]
#     assert dates == sorted(dates)
    
#     # Check weights are increasing
#     weights = [entry.get('weight', entry.get('Weight')) for entry in data]
#     assert weights[-1] > weights[0]