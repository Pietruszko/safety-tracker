import pytest
from django.urls import reverse
from devices.models import Device, LocationPing
from users.models import User
from rest_framework.test import APIClient

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
def user_bob():
    return User.objects.create(
        first_name='Bob',
        last_name='Joe'
    )

@pytest.fixture
def device_001():
    return Device.objects.create(
        device_id='device_001'
    )

@pytest.fixture
def device_002():
    return Device.objects.create(
        device_id='device_002'
    )

@pytest.mark.django_db
class TestDeviceAssign:
    def test_initial_devices_state_unassigned_and_inactive(self, device_001, device_002):
        """Test that devices start unassigned and inactive."""
        assert device_001.assigned_user == None
        assert device_001.is_active == False
        assert device_002.assigned_user == None
        assert device_002.is_active == False

    def test_assign_device_success(self, api_client, user_john, device_001):
        """Test for assigning device to user and marking it active."""
        payload = {
            'user_id': user_john.id
        }
        url = reverse('device-assign', args=[device_001.id])
        response = api_client.post(url, payload, format='json')
        assert response.status_code == 200
        assert response.data['detail'] == 'Device assigned successfully.'
        device_001.refresh_from_db()
        assert device_001.assigned_user == user_john
        assert device_001.is_active == True

    def test_assign_second_device_fails(self, api_client, user_john, device_001, device_002):
        """Test that should fail (400 code) when trying to assign a second active device to same user."""
        payload = {
            'user_id': user_john.id
        }
        url = reverse('device-assign', args=[device_001.id])
        response = api_client.post(url, payload, format='json')
        assert response.status_code == 200

        url = reverse('device-assign', args=[device_002.id])
        response = api_client.post(url, payload, format='json')
        assert response.status_code == 400

    def test_assign_nonexistent_user_returns_404(self, api_client, device_001):
        """Test for 404 code if user_id doesn't exist in database."""
        payload = {
            'user_id': 123
        }
        url = reverse('device-assign', args=[device_001.id])
        response = api_client.post(url, payload, format='json')
        assert response.status_code == 404

    def test_assign_device_clear_previous_user(self, api_client, user_john, user_bob, device_001):
        """Test for assigning device to user and clearing it from previous user."""
        payload = {
            'user_id': user_john.id
        }
        payload_2 = {
            'user_id': user_bob.id
        }
        url = reverse('device-assign', args=[device_001.id])
        response = api_client.post(url, payload, format='json')
        assert response.status_code == 200
        device_001.refresh_from_db()
        assert device_001.assigned_user == user_john
        response = api_client.post(url, payload_2, format='json')
        assert response.status_code == 200
        device_001.refresh_from_db()
        assert device_001.assigned_user == user_bob

@pytest.fixture
def user_danny():
    return User.objects.create(
        first_name='Danny',
        last_name='Crow'
    )

@pytest.fixture
def inactive_device():
    return Device.objects.create(
        device_id='device_003'
    )

@pytest.fixture
def active_device(api_client, inactive_device, user_danny):
    payload = {
        'user_id': user_danny.id
    }
    url = reverse('device-assign', args=[inactive_device.id])
    api_client.post(url, payload, format='json')
    return inactive_device

@pytest.mark.django_db
class TestDeviceLocation:
    def test_send_location_success(self, api_client, active_device):
        """Test for sending a new location from the active device."""
        payload = {
            "latitude": 50.123,
            "longitude": 19.456,
            "ping_time": "2025-04-22T10:15:00Z"
        }
        url = reverse('device-location', args=[active_device.id])
        response = api_client.post(url, payload, format='json')
        assert response.status_code == 201
        assert response.data['latitude'] == 50.123
        assert response.data['longitude'] == 19.456
        assert response.data['device'] == active_device.id
        ping = LocationPing.objects.latest('id')
        assert ping.device == active_device
        assert ping.latitude == 50.123


    def test_send_location_fail(self, api_client, inactive_device):
        """Test that fails to send location from an inactive device."""
        payload = {
            "latitude": 50.123,
            "longitude": 19.456,
            "ping_time": "2025-04-22T10:15:00Z"
        }
        url = reverse('device-location', args=[inactive_device.id])
        response = api_client.post(url, payload, format='json')
        assert response.status_code == 400

@pytest.fixture
def location_ping_1(active_device):
    return LocationPing.objects.create(
        device=active_device,
        latitude=50.123,
        longitude=19.456,
        ping_time="2025-04-22T10:15:00Z"
    )

@pytest.fixture
def location_ping_2(active_device):
    return LocationPing.objects.create(
        device=active_device,
        latitude=51.123,
        longitude=20.456,
        ping_time="2025-04-22T10:20:00Z"
    )

@pytest.mark.django_db
class TestMapView:
    def test_empty_map_with_no_devices(self, api_client):
        """Test empty response when no devices are assigned."""
        url = reverse('map-view')
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data == []

    def test_map_with_one_active_device(self, api_client, user_danny, active_device, location_ping_1, location_ping_2):
        """Test map response with one active device and two pings so it needs to choose latest one."""
        url = reverse('map-view')
        response = api_client.get(url)
        
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0] == {
            "user": {"id": user_danny.id, "name": f"{user_danny.first_name} {user_danny.last_name}"},
            "device_id": "device_003",
            "latitude": 51.123,
            "longitude": 20.456,
            "timestamp": "2025-04-22T10:20:00Z"
        }

    