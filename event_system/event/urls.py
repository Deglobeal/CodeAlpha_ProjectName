from django.urls import path
from .views import (
    EventListView,
    EventDetailView,
    RegistrationListView,
    RegistrationCreateView,
    RegistrationCancelView
)

urlpatterns = [
    path('events/', EventListView.as_view(), name='event-list'),
    path('events/<int:pk>/', EventDetailView.as_view(), name='event-detail'),
    path('register/', RegistrationCreateView.as_view(), name='registration-create'),
    path('my-registrations/', RegistrationListView.as_view(), name='registration-list'),
    path('cancel-registration/<int:pk>/', RegistrationCancelView.as_view(), name='registration-cancel'),
]