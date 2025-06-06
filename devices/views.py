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
    
    @action(detail=True, methods=['post'], url_path='unassign')
    def unassign(self, request, pk=None):
        device = self.get_object()
        device.assigned_user = None
        device.is_active = False
        device.save()
        
        serializer = self.get_serializer(device)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class MapView(generics.ListAPIView):
    serializer_class = MapSerializer

    def get_queryset(self):
        queryset = Device.objects.filter(
            is_active=True,
            assigned_user__isnull=False
        ).select_related('assigned_user')

        user_id = self.request.query_params.get('user_id')
        device_id = self.request.query_params.get('device_id')

        if user_id:
            queryset = queryset.filter(assigned_user__id=user_id)
        if device_id:
            queryset = queryset.filter(device_id=device_id)
        
        return queryset
        
    


        