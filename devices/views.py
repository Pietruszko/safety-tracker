from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Device
from .serializers import DeviceSerializer, AssignDeviceSerializer, LocationPingSerializer, MapSerializer

class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer

    @action(detail=True, methods=['post'], url_path='assign')
    def assign(self, request, pk=None):
        device = self.get_object()
        serializer = AssignDeviceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(device=device)
            return Response({'detail': 'Device assigned successfully.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='location')
    def location(self, request, pk=None):
        device = self.get_object()

        data = request.data.copy()
        data['device'] = device.id

        serializer = LocationPingSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class MapView(generics.ListAPIView):
    serializer_class = MapSerializer

    def get_queryset(self):
        active_devices = Device.objects.filter(
            is_active=True,
            assigned_user__isnull=False
        ).select_related('assigned_user')
        
        return active_devices
        
    


        