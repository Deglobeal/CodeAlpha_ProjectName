from django.shortcuts import render
from .models import Event, Registration
from .serializers import EventSerializer, RegistrationSerializer  
from rest_framework import generics, permissions, status
from rest_framework.response import Response

class EventListView(generics.ListCreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny]

class EventDetailView(generics.RetrieveUpdateDestroyAPIView):   
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

class RegistrationListView(generics.ListAPIView):  # Changed to ListAPIView
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filter by status='active' instead of non-existent is_cancelled
        return Registration.objects.filter(user=self.request.user, status='active')

class RegistrationCreateView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class RegistrationCancelView(generics.UpdateAPIView):
    queryset = Registration.objects.all()
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        # Set status to 'cancelled' instead of non-existent is_cancelled
        serializer.save(status='cancelled')