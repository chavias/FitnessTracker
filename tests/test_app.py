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
    response = client.post('/register', data={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200
    
    # Check that user was created in the database
    with app.app_context():
        user = User.query.filter_by(email='newuser@example.com').first()
        assert user is not None
        assert user.username == 'newuser'

def test_home_page_when_authenticated(client, authenticated_user):
    response = client.get('/', follow_redirects=True)
    assert response.status_code == 200
    assert b'Dashboard' in response.data

def test_profile_page(client, authenticated_user):
    response = client.get('/profile')
    assert response.status_code == 200
    assert authenticated_user.username.encode() in response.data

def test_logout(client, authenticated_user):
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data

def test_create_workout_template(client, authenticated_user):
    response = client.post('/workout_templates/new', data={
        'name': 'New Template'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'New Template' in response.data

def test_add_exercise_to_template(client, authenticated_user, workout_template):
    response = client.post(f'/workout_templates/{workout_template.id}/add_exercise', data={
        'exercise': 'Pull-up'
    }, follow_redirects=True)
    assert response.status_code == 200
    
    # Verify exercise was added
    with client.application.app_context():
        template_exercises = TemplateExercise.query.filter_by(
            template_id=workout_template.id, 
            exercise='Pull-up'
        ).all()
        assert len(template_exercises) == 1

def test_start_training_session(client, authenticated_user, workout_template):
    response = client.post('/workout_sessions/new', data={
        'template_id': workout_template.id
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Training Session' in response.data

def test_progression_api(client, authenticated_user, app):
    # Create some test data for exercise progression
    with app.app_context():
        # Create training sessions with different dates
        for i in range(3):
            date = datetime.utcnow() - timedelta(days=10-i)
            session = TrainingSession(
                date=date,
                user_id=authenticated_user.id
            )
            db.session.add(session)
            db.session.flush()
            
            # Add bench press exercise to each session
            bench_press = Exercise(
                session_id=session.id,
                exercise_name='Bench Press'
            )
            db.session.add(bench_press)
            db.session.flush()
            
            # Add sets with increasing weights
            for j in range(3):
                details = ExerciseDetails(
                    exercise_id=bench_press.id,
                    repetitions=8,
                    weight=60 + (i*5)  # Weight increases over sessions
                )
                db.session.add(details)
        
        db.session.commit()
    
    # Test the API endpoint
    response = client.get('/api/progression?exercise=Bench Press')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) > 0
    
    # Check data structure
    assert 'date' in data[0] or 'Date' in data[0]
    assert 'weight' in data[0] or 'Weight' in data[0]
    
    # Check data is in ascending date order
    dates = [entry.get('date', entry.get('Date')) for entry in data]
    assert dates == sorted(dates)
    
    # Check weights are increasing
    weights = [entry.get('weight', entry.get('Weight')) for entry in data]
    assert weights[-1] > weights[0]

def test_view_training_history(client, authenticated_user, app):
    # Set up some training history
    with app.app_context():
        # Create a test session
        session = TrainingSession(
            date=datetime.utcnow(),
            user_id=authenticated_user.id
        )
        db.session.add(session)
        db.session.flush()
        
        # Add exercises to the session
        squat = Exercise(
            session_id=session.id,
            exercise_name='Squat'
        )
        db.session.add(squat)
        db.session.flush()
        
        # Add details for the squat
        details = ExerciseDetails(
            exercise_id=squat.id,
            repetitions=5,
            weight=100
        )
        db.session.add(details)
        db.session.commit()
    
    # Test viewing training history
    response = client.get('/workout_sessions')
    assert response.status_code == 200
    assert b'Squat' in response.data

def test_exercise_statistics(client, authenticated_user, app):
    # Create test data
    with app.app_context():
        # Create sessions on different dates
        dates = [
            datetime.utcnow() - timedelta(days=14),
            datetime.utcnow() - timedelta(days=7),
            datetime.utcnow()
        ]
        
        for date in dates:
            session = TrainingSession(
                date=date,
                user_id=authenticated_user.id
            )
            db.session.add(session)
            db.session.flush()
            
            # Add deadlift to each session with increasing weight
            deadlift = Exercise(
                session_id=session.id,
                exercise_name='Deadlift'
            )
            db.session.add(deadlift)
            db.session.flush()
            
            # Index to track position in dates list
            i = dates.index(date)
            
            # Weight increases in each session
            details = ExerciseDetails(
                exercise_id=deadlift.id,
                repetitions=5,
                weight=120 + (i * 10)  # 120, 130, 140
            )
            db.session.add(details)
        
        db.session.commit()
    
    # Test statistics endpoint
    response = client.get('/workout_statistics')
    assert response.status_code == 200
    
    # Check for progress indicators
    assert b'Deadlift' in response.data
    
    # Test specific exercise statistics
    response = client.get('/workout_statistics/exercise/Deadlift')
    assert response.status_code == 200
    assert b'Deadlift' in response.data