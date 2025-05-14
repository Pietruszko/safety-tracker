import pytest
from django.urls import reverse
from users.models import User
from devices.models import Device, LocationPing
from rest_framework.test import APIClient
from datetime import datetime, timedelta

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user_john():
    return User.objects.create(
        first_name='John',
        last_name='Doe'
    )

@pytest.fixture
def johns_device(user_john):
    return Device.objects.create(
        device_id='device_001',
        assigned_user = user_john,
        is_active = True
    )

@pytest.mark.django_db
class TestUserLocation:
    def test_fetching_last_known_user_location(self, api_client, user_john, johns_device):
        """Test that the endpoint returns the most recent location ping for a user."""
        # Create older ping
        LocationPing.objects.create(
            device=johns_device,
            latitude=40.0,
            longitude=20.0,
            ping_time="2025-04-22T10:10:00Z"
        )
        # Create most recent ping
        latest_ping = LocationPing.objects.create(
            device=johns_device,
            latitude=50.0,
            longitude=30.00,
            ping_time="2025-04-22T10:20:00Z"
        )

        url = reverse('user-location', args=[user_john.id])
        response = api_client.get(url)

        assert response.status_code == 200
        assert response.data['latitude'] == latest_ping.latitude
        assert response.data['longitude'] == latest_ping.longitude
        assert response.data['timestamp'] == latest_ping.ping_time

        