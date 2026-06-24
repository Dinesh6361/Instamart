from django.db import models
import requests
from django.contrib.auth.models import User

PEXELS_API_KEY = "M9CnG8qa2DOpWGR8yBURCU9Yo4SeuTZGdoKfopF7esf12TT7k6VSBU6b"


class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.IntegerField()
    image_url = models.URLField(blank=True)
    category = models.CharField(max_length=100, default="Grocery")
    stock = models.IntegerField(default=10)

    def save(self, *args, **kwargs):

        if not self.image_url:

            headers = {
                "Authorization": PEXELS_API_KEY
            }

            url = f"https://api.pexels.com/v1/search?query={self.name}&per_page=1"

            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()

                if data["photos"]:
                    self.image_url = data["photos"][0]["src"]["medium"]

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def total_price(self):
        return self.product.price * self.quantity
    

    def __str__(self):
        return self.product.name
    
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.IntegerField()
    address = models.TextField()
    phone = models.CharField(max_length=15)
    payment_method = models.CharField(max_length=50, default="Cash on Delivery")
    payment_status = models.CharField(max_length=50, default="Pending")
    order_status = models.CharField(max_length=50, default="Placed")
    created_at = models.DateTimeField(auto_now_add=True)
    delivery_status = models.CharField(max_length=50, default="Order Placed")
    delivery_boy = models.CharField(max_length=100, default="Not Assigned")
    estimated_time = models.CharField(max_length=50, default="30 minutes")
    delivery_lat = models.FloatField(null=True, blank=True)
    delivery_lng = models.FloatField(null=True, blank=True)
    delivery_otp = models.CharField(max_length=6, blank=True)
    assigned_delivery_boy = models.ForeignKey("delivery.DeliveryBoy",on_delete=models.SET_NULL, null=True,blank=True)
    DELIVERY_STATUS = (("Order Placed", "Order Placed"),("Picked Up", "Picked Up"),("Out For Delivery", "Out For Delivery"),("Delivered", "Delivered"),)

    delivery_status = models.CharField( max_length=30,choices=DELIVERY_STATUS,default="Order Placed")

    def __str__(self):
        return self.user.username


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=100)
    price = models.IntegerField()
    quantity = models.IntegerField()

    def total_price(self):
        return self.price * self.quantity
    
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product.name
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return self.product.name
class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount = models.IntegerField()

    def __str__(self):
        return self.code
    
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message