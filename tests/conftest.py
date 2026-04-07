"""
Shared test fixtures and configuration for the FastAPI test suite.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """
    Provides a TestClient connected to the FastAPI app.
    
    Returns:
        TestClient: A test client for making requests to the app.
    """
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """
    Resets the in-memory activities database to its initial state.
    
    This fixture ensures each test starts with a clean state of activities,
    preventing test pollution from signup/removal operations.
    
    Yields control back to the test, then resets afterward.
    """
    # Store original state
    original_activities = {
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
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Practice and compete in basketball games",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": []
        },
        "Soccer Club": {
            "description": "Train and play soccer matches",
            "schedule": "Wednesdays and Saturdays, 3:00 PM - 5:00 PM",
            "max_participants": 22,
            "participants": []
        },
        "Art Club": {
            "description": "Explore various art forms and create masterpieces",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": []
        },
        "Drama Club": {
            "description": "Act in plays and improve theatrical skills",
            "schedule": "Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 20,
            "participants": []
        },
        "Debate Club": {
            "description": "Engage in debates and develop critical thinking",
            "schedule": "Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": []
        },
        "Science Club": {
            "description": "Conduct experiments and learn about science",
            "schedule": "Tuesdays, 4:30 PM - 6:00 PM",
            "max_participants": 14,
            "participants": []
        }
    }
    
    yield
    
    # Reset activities to original state
    activities.clear()
    activities.update(original_activities)


@pytest.fixture
def sample_email():
    """
    Provides a sample email for testing signup/removal operations.
    
    Returns:
        str: A test email address not already in the Chess Club.
    """
    return "testuser@mergington.edu"


@pytest.fixture
def empty_activity():
    """
    Provides the name of an empty activity for testing.
    
    Returns:
        str: The name of an activity with no current participants.
    """
    return "Basketball Team"
