from django.db import models

class DeliveryBoy(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name