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
        return data
    
    def save(self, **kwargs):
        device = self.context['device']
        user = get_object_or_404(User, id=self.validated_data['user_id'])

        # Unassign device from previous user (if any)
        device.assigned_user = user
        device.is_active = True
        device.save()

        return device