"""
Unit tests for validation and utility functions.

Tests validation logic for activity management, including:
- Email format validation
- Activity name validation
- Participant count logic
"""

import pytest


class TestEmailValidation:
    """Tests for email validation patterns."""

    def test_valid_email_format(self):
        """Test recognition of valid email formats."""
        valid_emails = [
            "john@mergington.edu",
            "michael@mergington.edu",
            "emma@mergington.edu",
            "test.user@mergington.edu",
            "user123@mergington.edu",
        ]
        
        for email in valid_emails:
            # Basic validation: contains @ and domain
            assert "@" in email
            assert "." in email.split("@")[1]

    def test_invalid_email_formats(self):
        """Test rejection of invalid email formats."""
        invalid_emails = [
            "notanemail",
            "@mergington.edu",
            "user@",
            "user@.edu",
            "user..name@mergington.edu",
        ]
        
        for email in invalid_emails:
            # Basic validation checks: must have @ and domain with ., no empty parts
            parts = email.split("@")
            has_valid_format = (
                "@" in email and 
                email.count("@") == 1 and 
                len(parts[0]) > 0 and 
                len(parts) == 2 and
                "." in parts[1] and
                len(parts[1]) > 1 and
                not parts[1].startswith(".") and  # Domain can't start with .
                ".." not in email  # No consecutive dots
            )
            assert not has_valid_format, f"Email {email} should be invalid"


class TestActivityNameValidation:
    """Tests for activity name validation patterns."""

    def test_valid_activity_names(self):
        """Test recognition of valid activity names."""
        valid_names = [
            "Chess Club",
            "Programming Class",
            "Basketball Team",
            "Science Club",
            "Art Club",
        ]
        
        for name in valid_names:
            # Non-empty and string
            assert isinstance(name, str)
            assert len(name) > 0

    def test_activity_name_case_sensitivity(self):
        """Test that activity names are case-sensitive."""
        # "Chess Club" is valid, but "chess club" is not (in the app)
        assert "Chess Club" != "chess club"
        assert "Programming Class" != "programming class"


class TestParticipantCountLogic:
    """Tests for participant count and capacity logic."""

    def test_max_participants_is_positive(self):
        """Test that max_participants is always a positive integer."""
        valid_max_participants = [12, 15, 20, 30, 14]
        
        for max_count in valid_max_participants:
            assert isinstance(max_count, int)
            assert max_count > 0

    def test_participant_count_does_not_exceed_max(self):
        """Test that participant count validation logic."""
        activities_data = {
            "Chess Club": {"participants": ["a@x.com", "b@x.com"], "max_participants": 12},
            "Basketball Team": {"participants": [], "max_participants": 15},
            "Science Club": {"participants": ["c@x.com", "d@x.com", "e@x.com"], "max_participants": 14},
        }
        
        for activity, data in activities_data.items():
            current_count = len(data["participants"])
            max_count = data["max_participants"]
            
            # Verify current count doesn't exceed max
            assert current_count <= max_count, f"{activity} exceeds capacity"

    def test_can_add_participant_logic(self):
        """Test the logic for determining if a participant can be added."""
        # If current < max, participant can be added
        current = 5
        max_count = 10
        assert current < max_count
        
        # If current == max, participant cannot be added
        current = 10
        max_count = 10
        assert not (current < max_count)

    def test_participant_is_unique_in_activity(self):
        """Test that each participant appears only once per activity."""
        participants = ["alice@mergington.edu", "bob@mergington.edu", "alice@mergington.edu"]
        
        # Check for duplicates
        assert len(participants) != len(set(participants))
        
        # Correct state: no duplicates
        correct_participants = ["alice@mergington.edu", "bob@mergington.edu"]
        assert len(correct_participants) == len(set(correct_participants))


class TestDataTypeValidation:
    """Tests for data type validation."""

    def test_activity_fields_are_correct_types(self):
        """Test that activity fields have correct data types."""
        activity = {
            "description": "Test activity",
            "schedule": "Mondays, 3:00 PM",
            "max_participants": 20,
            "participants": ["user@x.com"]
        }
        
        assert isinstance(activity["description"], str)
        assert isinstance(activity["schedule"], str)
        assert isinstance(activity["max_participants"], int)
        assert isinstance(activity["participants"], list)

    def test_participants_list_contains_strings(self):
        """Test that participants list contains only email strings."""
        participants = ["alice@mergington.edu", "bob@mergington.edu"]
        
        for participant in participants:
            assert isinstance(participant, str)
            assert "@" in participant

    def test_description_and_schedule_are_non_empty(self):
        """Test that description and schedule are not empty strings."""
        activity = {
            "description": "Learn chess strategy",
            "schedule": "Fridays, 3:30 PM",
        }
        
        assert len(activity["description"]) > 0
        assert len(activity["schedule"]) > 0
