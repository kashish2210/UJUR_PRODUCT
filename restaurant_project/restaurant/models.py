from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random
import string
from django.db import models
from django.utils import timezone

# Function to generate a random order ID
def generate_order_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

# Order model
class Order(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    order_id = models.CharField(max_length=8, unique=True, default=generate_order_id)
    products = models.ManyToManyField('Product', through='OrderItem')
    date_ordered = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Order({self.user.username} - {self.order_id})"

# Other models remain as before


# Custom user model for Manager and Customer
class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('manager', 'Manager'),
        ('customer', 'Customer'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='customer')
    is_manager = models.BooleanField(default=False)  # Add default to avoid NOT NULL errors

    groups = models.ManyToManyField(
        'auth.Group', 
        related_name='restaurant_user_groups', 
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission', 
        related_name='restaurant_user_permissions', 
        blank=True
    )

    def __str__(self):
        return self.username


# Product model
class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.FloatField()
    discount = models.FloatField(default=0)  # Discount percentage
    image = models.ImageField(upload_to='products/')

    def discounted_price(self):
        return self.price - (self.price * (self.discount / 100))

    def __str__(self):
        return self.name


# Cart model
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Use the default User model

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    instruction = models.TextField(blank=True, null=True)

    def total_price(self):
        return self.product.discounted_price() * self.quantity

    def __str__(self):
        return f"Cart({self.user.username} - {self.product.name})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.FloatField()
    total_price = models.FloatField()

    def __str__(self):
        return f"OrderItem({self.order.order_id} - {self.product.name})"
