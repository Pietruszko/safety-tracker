from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=True, methods=['get'], url_path='location')
    def location(self, request, pk=None):
        user = self.get_object()

        device = user.devices.filter(is_active=True).first()
        if not device:
            return Response({"detail": "User has no active device."}, 
                            status=status.HTTP_404_NOT_FOUND)
        
        last_ping = device.location_pings.order_by('-ping_time').first()
        if not last_ping:
            return Response({"detail": "No location data available."}, 
                            status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            "latitude": last_ping.latitude,
            "longitude": last_ping.longitude,
            "timestamp": last_ping.ping_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }, status=status.HTTP_200_OK)
