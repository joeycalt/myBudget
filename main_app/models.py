from django.db.models import Model
from django.db import models
from django.contrib.auth.models import User
import datetime

class Purchased(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=500)
    price = models.CharField(max_length=8)
    date = models.CharField(max_length=500)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    def __str__(self):
        return self.name
    class Meta:
        ordering = ['name']

class Budget(models.Model):
    title = models.CharField(max_length=10)
    month = models.CharField(max_length=15)
    purch = models.ForeignKey(
        Purchased, on_delete=models.CASCADE, related_name="buys", null="True")

    def __str__(self):
        return self.title

class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.CharField(max_length=8)
    date = models.CharField(max_length=500)
    buys = models.ManyToManyField(Purchased)

    def __str__(self):
        return self.title