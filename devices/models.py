from django.db import models
from users.models import User

class Device(models.Model):
    """Represents SOS Device that can be assigned to user,
    sending location with each ping.
    """
    device_id = models.CharField(max_length=100, unique=True)
    assigned_user = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='devices'
    )
    assigned_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.device_id
    
class LocationPing(models.Model):
    """Represents a single location ping from SOS devices."""
    device = models.ForeignKey(
        Device, on_delete=models.CASCADE,
        related_name='location_pings'
    )
    latitude = models.FloatField()
    longitude = models.FloatField()

    # Assuming SOS device sends actual time of ping,
    # Alternative would be created_at with auto_add_now=True

    ping_time = models.DateTimeField(db_index=True) # Query optimization

    def __str__(self):
        return f"{self.device.device_id} @ {self.ping_time}"