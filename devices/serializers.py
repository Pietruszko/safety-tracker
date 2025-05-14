from rest_framework import serializers
from .models import LocationPing, Device
from users.models import User
from django.shortcuts import get_object_or_404

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ['id', 'device_id', 'assigned_user', 'assigned_at', 'is_active']
        extra_kwargs = {
            'assigned_user': {'read_only': True}
        }

class LocationPingSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationPing
        fields = ['id', 'device', 'latitude', 'longitude', 'ping_time']

    def validate(self, data):
        device = data['device']
        if not device.is_active or not device.assigned_user:
            raise serializers.ValidationError("Device is not assigned or not active.")
        return data

class AssignDeviceSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()

    def validate(self, data):
        user = get_object_or_404(User, id=data['user_id'])

        # Check if user has any active devices
        if Device.objects.filter(assigned_user=user, is_active=True).exists():
            raise serializers.ValidationError("User can have only one active SOS device.")
        
        data['user'] = user
        return data
    
    def save(self, device):
        # Unassign device from previous user (if any)
        device.assigned_user = self.validated_data['user']
        device.is_active = True
        device.save()
        return device
    
class MapSerializer(serializers.Serializer):
    user = serializers.SerializerMethodField()
    device_id = serializers.CharField()
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    timestamp = serializers.SerializerMethodField()

    def get_user(self, obj):
        return {
            "id": obj.assigned_user.id,
            "name": f"{obj.assigned_user.first_name} {obj.assigned_user.last_name}"
        }
    
    def get_latest_ping(self, device):
        latest = device.location_pings.order_by('-ping_time').first()
        if not latest:
            raise serializers.ValidationError(f"Device {device.device_id} has no location pings")
        return latest

    def get_latitude(self, obj):
        return self.get_latest_ping(obj).latitude

    def get_longitude(self, obj):
        return self.get_latest_ping(obj).longitude

    def get_timestamp(self, obj):
        return self.get_latest_ping(obj).ping_time.strftime("%Y-%m-%dT%H:%M:%SZ")

    class Meta:
        fields = ['user', 'device_id', 'latitude', 'longitude', 'timestamp']
