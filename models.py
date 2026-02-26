from django.db import models
from django.contrib.auth.models import User


class Cook(models.Model):
    name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=100, help_text="E.g., Italian, Homemade Sweets")
    bio = models.TextField()
    location = models.CharField(max_length=100, help_text="Neighborhood or Zip Code")
    contact_info = models.CharField(max_length=100, help_text="Phone number or email")
    profile_image = models.ImageField(upload_to='cooks/', blank=True, null=True)

    def __str__(self):
        return self.name

class Dish(models.Model):
    cook = models.ForeignKey(Cook, on_delete=models.CASCADE, related_name='dishes')
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='dishes/', blank=True, null=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} by {self.cook.name}"

class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )
    
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=20)
    customer_address = models.TextField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    
    # New requirements
    scheduled_time = models.DateTimeField(null=True, blank=True, help_text="When do you want this?")
    servings_count = models.PositiveIntegerField(default=1, help_text="For how many people?")
    special_instructions = models.TextField(blank=True, help_text="Any special requirements?")
    
    # Payment fields
    PAYMENT_METHOD_CHOICES = (
        ('COD', 'Cash on Delivery'),
        ('Online', 'Online Payment'),
    )
    PAYMENT_STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Failed', 'Failed'),
    )
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='COD')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Pending')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} by {self.customer_name}"

    @property
    def total_cost(self):
        return sum(item.cost for item in self.items.all())

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=6, decimal_places=2) # Price at time of order

    def __str__(self):
        return f"{self.quantity}x {self.dish.title}"

    @property
    def cost(self):
        if self.price is not None and self.quantity is not None:
            return self.price * self.quantity
        return 0

class UserProxy(User):
    class Meta:
        proxy = True
        verbose_name = 'Login Information (User)'
        verbose_name_plural = 'Login Information (Users)'
