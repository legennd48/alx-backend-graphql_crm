from django.db import models
from django.core.validators import RegexValidator, EmailValidator
from decimal import Decimal
from django.core.exceptions import ValidationError
import re


class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$|^\d{3}-\d{3}-\d{4}$',
                message="Phone number must be in format: '+999999999' or '999-999-9999'"
            )
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.email})"

    def clean(self):
        if self.phone:
            # Clean phone number format
            phone_clean = re.sub(r'[^\d+\-]', '', self.phone)
            if not re.match(r'^\+?1?\d{9,15}$|^\d{3}-\d{3}-\d{4}$', phone_clean):
                raise ValidationError({'phone': 'Invalid phone number format'})


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - ${self.price}"

    def clean(self):
        if self.price <= 0:
            raise ValidationError({'price': 'Price must be positive'})


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    products = models.ManyToManyField(Product, related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    order_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.customer.name}"

    def calculate_total(self):
        """Calculate total amount from associated products"""
        return sum(product.price for product in self.products.all())

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.products.exists():
            self.total_amount = self.calculate_total()
            super().save(update_fields=['total_amount'])
