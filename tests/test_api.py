"""
Test cases for the Mergington High School API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": []
        }
    })


def test_root_redirect(client):
    """Test that root path redirects to static index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client):
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Science Club" in data
    assert len(data["Chess Club"]["participants"]) == 2
    assert len(data["Science Club"]["participants"]) == 0


def test_signup_new_participant(client):
    """Test signing up a new participant for an activity"""
    response = client.post(
        "/activities/Science Club/signup?email=john@mergington.edu"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Signed up john@mergington.edu for Science Club"
    
    # Verify participant was added
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert "john@mergington.edu" in activities_data["Science Club"]["participants"]


def test_signup_duplicate_participant(client):
    """Test signing up a participant who is already registered"""
    response = client.post(
        "/activities/Chess Club/signup?email=michael@mergington.edu"
    )
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Student is already signed up"


def test_signup_nonexistent_activity(client):
    """Test signing up for an activity that doesn't exist"""
    response = client.post(
        "/activities/Nonexistent Club/signup?email=john@mergington.edu"
    )
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"


def test_unregister_participant(client):
    """Test unregistering a participant from an activity"""
    response = client.delete(
        "/activities/Chess Club/unregister?email=michael@mergington.edu"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Unregistered michael@mergington.edu from Chess Club"
    
    # Verify participant was removed
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]


def test_unregister_nonexistent_participant(client):
    """Test unregistering a participant who is not registered"""
    response = client.delete(
        "/activities/Science Club/unregister?email=nonexistent@mergington.edu"
    )
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Student is not signed up for this activity"


def test_unregister_nonexistent_activity(client):
    """Test unregistering from an activity that doesn't exist"""
    response = client.delete(
        "/activities/Nonexistent Club/unregister?email=john@mergington.edu"
    )
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"


def test_signup_and_unregister_workflow(client):
    """Test the complete workflow of signing up and then unregistering"""
    email = "workflow@mergington.edu"
    activity = "Programming Class"
    
    # Sign up
    signup_response = client.post(
        f"/activities/{activity}/signup?email={email}"
    )
    assert signup_response.status_code == 200
    
    # Verify participant was added
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert email in activities_data[activity]["participants"]
    
    # Unregister
    unregister_response = client.delete(
        f"/activities/{activity}/unregister?email={email}"
    )
    assert unregister_response.status_code == 200
    
    # Verify participant was removed
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert email not in activities_data[activity]["participants"]
