from rest_framework import serializers
from .models import Event, Registration

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registration
        fields = ['id', 'event', 'user', 'status', 'registration_date']
        read_only_fields = ['user', 'registration_date']

    def validate(self, data):
        # Handle both create and update operations
        event = data.get('event')
        
        # For updates, get event from existing instance
        if not event and self.instance:
            event = self.instance.event
            
        # Only check capacity for active registrations
        if event and data.get('status', 'active') == 'active':
            active_registrations = event.registration_set.filter(status='active').count()
            
            # Check if event is full
            if active_registrations >= event.capacity:
                raise serializers.ValidationError("Event is full")
                
        return data