from django.db.models import Model
from django.db import models
from django.contrib.auth.models import User
import datetime

class Budget(models.Model):
    amount = models.CharField(max_length=10)
    month = models.CharField(max_length=15)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return self.amount

class Purchased(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=500)
    price = models.CharField(max_length=8)
    date = models.CharField(max_length=500)
    budget = models.ForeignKey(
        Budget, on_delete=models.CASCADE, related_name="budget", null=True)
    def __str__(self):
        return self.name
    class Meta:
        ordering = ['name']


class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.CharField(max_length=8)
    date = models.CharField(max_length=500)
    buys = models.ManyToManyField(Purchased, blank=True, related_name='buys')

    def __str__(self):
        return self.title