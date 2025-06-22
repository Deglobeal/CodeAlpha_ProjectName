from django.contrib import admin
from .models import *

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'restaurant', 'table', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'restaurant')
    search_fields = ('customer_name', 'customer_phone')
    readonly_fields = ('created_at', 'total_price')

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'restaurant', 'table', 'reservation_date', 'start_time', 'status')
    list_filter = ('status', 'restaurant')
    search_fields = ('customer_name', 'customer_phone')

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'category', 'price', 'is_available')
    list_filter = ('category', 'restaurant')
    search_fields = ('name',)

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'quantity', 'unit', 'is_low_stock')
    list_filter = ('restaurant',)
    search_fields = ('name',)
    actions = ['generate_low_stock_report']

    def is_low_stock(self, obj):
        return obj.is_low_stock
    is_low_stock.boolean = True

    def generate_low_stock_report(self, request, queryset):
        low_stock_items = queryset.filter(quantity__lt=F('alert_threshold'))
        # In a real implementation, you might generate a PDF or send email here
        self.message_user(request, f"Found {low_stock_items.count()} low stock items")
    generate_low_stock_report.short_description = "Generate low stock report"

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('table_number', 'restaurant', 'capacity', 'is_occupied')
    list_filter = ('restaurant',)
    search_fields = ('table_number',)

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('menu_item', 'ingredient', 'quantity_used', 'unit')
    list_filter = ('menu_item__restaurant',)

admin.site.register(Restaurant)