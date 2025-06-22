from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'restaurants', views.RestaurantViewSet)
router.register(r'menu', views.MenuItemViewSet, basename='menuitem')  # Added basename
router.register(r'orders', views.OrderViewSet, basename='order')  # Added basename
router.register(r'reservations', views.ReservationViewSet, basename='reservation')  # Added basename
router.register(r'inventory', views.InventoryViewSet, basename='inventory')  # Added basename
router.register(r'reports', views.ReportViewSet, basename='report')  # Added basename

urlpatterns = [
    path('', include(router.urls)),
]
