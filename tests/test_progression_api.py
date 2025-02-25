def test_progression_api(client, authenticated_user):
    # Create some test data
    # ... add code to create test training data
    
    # Test the API endpoint
    response = client.get('/api/progression?exercise=Bench Press')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert 'Weight' in data[0]