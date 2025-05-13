from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Device
from .serializers import DeviceSerializer, AssignDeviceSerializer, LocationPingSerializer

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
