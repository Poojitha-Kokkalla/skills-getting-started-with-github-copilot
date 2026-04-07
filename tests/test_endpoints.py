"""
Integration tests for FastAPI activity management endpoints.

Tests all four main endpoints:
- GET / — root redirect
- GET /activities — retrieve all activities
- POST /activities/{activity_name}/signup — sign up a student
- DELETE /activities/{activity_name}/participants/{email} — remove a student
"""

import pytest


class TestRootEndpoint:
    """Tests for the GET / endpoint."""

    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to /static/index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for the GET /activities endpoint."""

    def test_get_all_activities_returns_dict(self, client, reset_activities):
        """Test that GET /activities returns a dictionary of activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) == 9

    def test_all_activities_have_required_fields(self, client, reset_activities):
        """Test that each activity has required fields."""
        response = client.get("/activities")
        activities = response.json()

        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_name, str)
            assert isinstance(activity_data, dict)
            assert required_fields.issubset(activity_data.keys())

    def test_activities_have_correct_structure(self, client, reset_activities):
        """Test that activities have the correct data types and structure."""
        response = client.get("/activities")
        activities = response.json()

        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)
            assert activity_data["max_participants"] > 0

    def test_default_activities_are_present(self, client, reset_activities):
        """Test that all 9 default activities are present."""
        response = client.get("/activities")
        activities = response.json()

        expected_activities = {
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Soccer Club",
            "Art Club",
            "Drama Club",
            "Debate Club",
            "Science Club"
        }
        
        assert set(activities.keys()) == expected_activities

    def test_activities_with_participants_match_initial_state(self, client, reset_activities):
        """Test that activities with participants have the correct initial participants."""
        response = client.get("/activities")
        activities = response.json()

        assert "michael@mergington.edu" in activities["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in activities["Chess Club"]["participants"]
        assert "emma@mergington.edu" in activities["Programming Class"]["participants"]
        assert "sophia@mergington.edu" in activities["Programming Class"]["participants"]


class TestSignupEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_success_happy_path(self, client, reset_activities, sample_email, empty_activity):
        """Test successful signup to an activity."""
        response = client.post(
            f"/activities/{empty_activity}/signup",
            params={"email": sample_email}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert sample_email in data["message"]
        assert empty_activity in data["message"]

    def test_signup_adds_participant_to_activity(self, client, reset_activities, sample_email, empty_activity):
        """Test that signup actually adds the participant to the activity."""
        client.post(
            f"/activities/{empty_activity}/signup",
            params={"email": sample_email}
        )
        
        response = client.get("/activities")
        activities = response.json()
        
        assert sample_email in activities[empty_activity]["participants"]

    def test_signup_nonexistent_activity_returns_404(self, client, reset_activities, sample_email):
        """Test that signing up for a nonexistent activity returns 404."""
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": sample_email}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate_returns_400(self, client, reset_activities):
        """Test that signing up twice returns an error."""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in Chess Club
        
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_multiple_different_activities(self, client, reset_activities, sample_email):
        """Test that a student can sign up for multiple different activities."""
        activities_to_join = ["Basketball Team", "Soccer Club", "Art Club"]
        
        for activity in activities_to_join:
            response = client.post(
                f"/activities/{activity}/signup",
                params={"email": sample_email}
            )
            assert response.status_code == 200
        
        # Verify all signups succeeded
        response = client.get("/activities")
        activities = response.json()
        for activity in activities_to_join:
            assert sample_email in activities[activity]["participants"]

    def test_signup_with_different_students_same_activity(self, client, reset_activities, empty_activity):
        """Test that multiple different students can join the same activity."""
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        
        for email in emails:
            response = client.post(
                f"/activities/{empty_activity}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify all students were added
        response = client.get("/activities")
        activities = response.json()
        for email in emails:
            assert email in activities[empty_activity]["participants"]


class TestRemoveParticipantEndpoint:
    """Tests for the DELETE /activities/{activity_name}/participants/{email} endpoint."""

    def test_remove_participant_success_happy_path(self, client, reset_activities):
        """Test successful removal of a participant from an activity."""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        response = client.delete(f"/activities/{activity_name}/participants/{email}")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_remove_participant_actually_removes(self, client, reset_activities):
        """Test that removal actually removes the participant from the activity."""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Remove the participant
        client.delete(f"/activities/{activity_name}/participants/{email}")
        
        # Verify removal
        response = client.get("/activities")
        activities = response.json()
        assert email not in activities[activity_name]["participants"]

    def test_remove_from_nonexistent_activity_returns_404(self, client, reset_activities):
        """Test that removing from a nonexistent activity returns 404."""
        response = client.delete(
            "/activities/Nonexistent Club/participants/test@mergington.edu"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_remove_nonexistent_participant_returns_404(self, client, reset_activities):
        """Test that removing a non-enrolled student returns 404."""
        activity_name = "Basketball Team"  # Empty activity
        email = "notaparticipant@mergington.edu"
        
        response = client.delete(f"/activities/{activity_name}/participants/{email}")
        
        assert response.status_code == 404
        data = response.json()
        assert "not signed up" in data["detail"]

    def test_remove_then_signup_again(self, client, reset_activities, sample_email, empty_activity):
        """Test that a student can be removed and then sign up again."""
        # First signup
        response1 = client.post(
            f"/activities/{empty_activity}/signup",
            params={"email": sample_email}
        )
        assert response1.status_code == 200
        
        # Remove
        response2 = client.delete(
            f"/activities/{empty_activity}/participants/{sample_email}"
        )
        assert response2.status_code == 200
        
        # Verify participant is gone
        response3 = client.get("/activities")
        activities = response3.json()
        assert sample_email not in activities[empty_activity]["participants"]
        
        # Sign up again
        response4 = client.post(
            f"/activities/{empty_activity}/signup",
            params={"email": sample_email}
        )
        assert response4.status_code == 200

    def test_remove_multiple_participants_from_activity(self, client, reset_activities):
        """Test removing multiple participants from an activity."""
        activity_name = "Chess Club"
        emails_to_remove = ["michael@mergington.edu", "daniel@mergington.edu"]
        
        for email in emails_to_remove:
            response = client.delete(f"/activities/{activity_name}/participants/{email}")
            assert response.status_code == 200
        
        # Verify both were removed
        response = client.get("/activities")
        activities = response.json()
        for email in emails_to_remove:
            assert email not in activities[activity_name]["participants"]


class TestIntegrationScenarios:
    """End-to-end integration scenarios."""

    def test_full_workflow_signup_and_removal(self, client, reset_activities, sample_email):
        """Test a complete workflow: signup, verify, remove, verify."""
        activity = "Drama Club"
        
        # Step 1: Sign up
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": sample_email}
        )
        assert response.status_code == 200
        
        # Step 2: Verify signup in activities list
        response = client.get("/activities")
        activities = response.json()
        assert sample_email in activities[activity]["participants"]
        
        # Step 3: Remove
        response = client.delete(
            f"/activities/{activity}/participants/{sample_email}"
        )
        assert response.status_code == 200
        
        # Step 4: Verify removal in activities list
        response = client.get("/activities")
        activities = response.json()
        assert sample_email not in activities[activity]["participants"]

    def test_signup_to_all_activities(self, client, reset_activities, sample_email):
        """Test signing up a single student to all activities."""
        # Get all activities
        response = client.get("/activities")
        all_activities = response.json()
        
        # Sign up for each activity
        for activity_name in all_activities.keys():
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": sample_email}
            )
            assert response.status_code == 200
        
        # Verify student is in all activities
        response = client.get("/activities")
        activities = response.json()
        for activity_name in activities.keys():
            assert sample_email in activities[activity_name]["participants"]

    def test_concurrent_manipulations(self, client, reset_activities):
        """Test that multiple people can join and be removed from the same activity."""
        activity = "Science Club"
        email1 = "user1@mergington.edu"
        email2 = "user2@mergington.edu"
        email3 = "user3@mergington.edu"
        
        # Join
        assert client.post(f"/activities/{activity}/signup", params={"email": email1}).status_code == 200
        assert client.post(f"/activities/{activity}/signup", params={"email": email2}).status_code == 200
        assert client.post(f"/activities/{activity}/signup", params={"email": email3}).status_code == 200
        
        # Verify all joined
        response = client.get("/activities")
        activities = response.json()
        assert len([e for e in [email1, email2, email3] if e in activities[activity]["participants"]]) == 3
        
        # Remove one
        assert client.delete(f"/activities/{activity}/participants/{email2}").status_code == 200
        
        # Verify correct removal
        response = client.get("/activities")
        activities = response.json()
        assert email1 in activities[activity]["participants"]
        assert email2 not in activities[activity]["participants"]
        assert email3 in activities[activity]["participants"]
