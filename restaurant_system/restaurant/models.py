from django.db import models
from django.db.models import F

class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    category = models.CharField(max_length=50, blank=True, null=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Table(models.Model):
    table_number = models.IntegerField(unique=True)
    capacity = models.IntegerField()
    is_occupied = models.BooleanField(default=False)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='tables')

    def __str__(self):
        return f"Table {self.table_number} ({self.capacity} seats)"

class Reservation(models.Model):
    STATUS_CHOICES = [
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
        ('Completed', 'Completed'),
    ]
    
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=15)
    reservation_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    special_requests = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Confirmed')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_name} - {self.reservation_date} {self.start_time}"

class MenuItem(models.Model):
    CATEGORY_CHOICES = [
        ('Appetizer', 'Appetizer'),
        ('Main Course', 'Main Course'),
        ('Dessert', 'Dessert'),
        ('Drink', 'Drink'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Preparing', 'Preparing'),
        ('Served', 'Served'),
        ('Paid', 'Paid'),
        ('Cancelled', 'Cancelled'),
    ]
    
    table = models.ForeignKey(Table, null=True, blank=True, on_delete=models.SET_NULL)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=100, blank=True, null=True)
    customer_phone = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    reservation = models.ForeignKey(Reservation, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"Order #{self.id} - {self.get_status_display()}"

    def save(self, *args, **kwargs):
        # Calculate total price before saving
        if not self.pk:  # New order
            super().save(*args, **kwargs)  # Save first to get ID
        else:
            self.total_price = sum(item.subtotal for item in self.items.all())
            super().save(*args, **kwargs)
        
        # Update inventory when order is paid
        if self.status == 'Paid':
            for item in self.items.all():
                # Deduct inventory based on recipe mapping
                for ingredient_usage in item.menu_item.ingredients.through.objects.filter(menuitem=item.menu_item):
                    ingredient = ingredient_usage.ingredient
                    ingredient.quantity -= ingredient_usage.quantity_used * item.quantity
                    ingredient.save()

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name}"

    def save(self, *args, **kwargs):
        self.subtotal = self.menu_item.price * self.quantity
        super().save(*args, **kwargs)
        # Update order total when item is saved
        self.order.save()

class Inventory(models.Model):
    UNIT_CHOICES = [
        ('kg', 'Kilograms'),
        ('g', 'Grams'),
        ('l', 'Liters'),
        ('ml', 'Milliliters'),
        ('unit', 'Units'),
    ]
    
    name = models.CharField(max_length=100)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES)
    alert_threshold = models.DecimalField(max_digits=10, decimal_places=2)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='inventory')

    def __str__(self):
        return f"{self.name} ({self.quantity} {self.unit})"
    
    @property
    def is_low_stock(self):
        return self.quantity < self.alert_threshold

class Recipe(models.Model):
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='ingredients')
    ingredient = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name='used_in')
    quantity_used = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.menu_item.name} - {self.quantity_used}{self.unit} {self.ingredient.name}"