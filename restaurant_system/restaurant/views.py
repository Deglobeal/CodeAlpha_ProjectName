from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import *
from .serializers import *
from django.utils import timezone
from django.db.models import Sum, Q

class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer 

    
class MenuItemViewSet(viewsets.ModelViewSet):
    serializer_class = MenuItemSerializer
    
    def get_queryset(self):
        restaurant_id = self.request.query_params.get('restaurant_id')
        if restaurant_id:
            return MenuItem.objects.filter(restaurant_id=restaurant_id, is_available=True)
        return MenuItem.objects.filter(is_available=True)

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    
    def get_queryset(self):
        restaurant_id = self.request.query_params.get('restaurant_id')
        status = self.request.query_params.get('status')
        
        queryset = Order.objects.all()
        if restaurant_id:
            queryset = queryset.filter(restaurant_id=restaurant_id)
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get('status')
        
        if new_status and new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            return Response({'status': 'Status updated'})
        return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

class ReservationViewSet(viewsets.ModelViewSet):
    serializer_class = ReservationSerializer
    
    def get_queryset(self):
        restaurant_id = self.request.query_params.get('restaurant_id')
        date = self.request.query_params.get('date')
        
        queryset = Reservation.objects.all()
        if restaurant_id:
            queryset = queryset.filter(restaurant_id=restaurant_id)
        if date:
            queryset = queryset.filter(reservation_date=date)
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Check table availability
        if not self.is_table_available(
            serializer.validated_data['table'].id,
            serializer.validated_data['reservation_date'],
            serializer.validated_data['start_time'],
            serializer.validated_data['end_time']
        ):
            return Response(
                {'error': 'Table is not available at the requested time'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def is_table_available(self, table_id, date, start_time, end_time):
        conflicting_reservations = Reservation.objects.filter(
            table_id=table_id,
            reservation_date=date,
            start_time__lt=end_time,
            end_time__gt=start_time,
            status__in=['Confirmed', 'Completed']
        ).exists()
        return not conflicting_reservations

class InventoryViewSet(viewsets.ModelViewSet):
    serializer_class = InventorySerializer
    
    def get_queryset(self):
        restaurant_id = self.request.query_params.get('restaurant_id')
        if restaurant_id:
            return Inventory.objects.filter(restaurant_id=restaurant_id)
        return Inventory.objects.all()
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        restaurant_id = request.query_params.get('restaurant_id')
        queryset = Inventory.objects.filter(quantity__lt=F('alert_threshold'))
        if restaurant_id:
            queryset = queryset.filter(restaurant_id=restaurant_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class ReportViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['get'])
    def daily_sales(self, request):
        restaurant_id = request.query_params.get('restaurant_id')
        date = request.query_params.get('date', timezone.now().date())
        
        orders = Order.objects.filter(
            created_at__date=date, 
            status='Paid'
        )
        if restaurant_id:
            orders = orders.filter(restaurant_id=restaurant_id)
        
        total_sales = orders.aggregate(total=Sum('total_price'))['total'] or 0
        order_count = orders.count()
        
        return Response({
            'date': date,
            'total_sales': total_sales,
            'order_count': order_count
        })
    
    @action(detail=False, methods=['get'])
    def popular_items(self, request):
        restaurant_id = request.query_params.get('restaurant_id')
        days = int(request.query_params.get('days', 7))
        
        start_date = timezone.now() - timezone.timedelta(days=days)
        
        items = OrderItem.objects.filter(
            order__created_at__gte=start_date,
            order__status='Paid'
        )
        
        if restaurant_id:
            items = items.filter(order__restaurant_id=restaurant_id)
        
        popular_items = items.values(
            'menu_item__name', 
            'menu_item__id'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('subtotal')
        ).order_by('-total_quantity')[:10]
        
        return Response(popular_items)