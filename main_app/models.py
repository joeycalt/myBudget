from django.db.models import Model
from django.db import models
from django.contrib.auth.models import User
import calendar
from datetime import datetime
from decimal import Decimal

class Budget(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.CharField(max_length=15)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    spend = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def get_date_range(self):
        """Return the full date range for the month (e.g., 'January 1-31')."""
        try:
            month_num = list(calendar.month_name).index(self.month.capitalize())
            if month_num:
                year = datetime.now().year  # Default to current year; adjust if needed
                _, days_in_month = calendar.monthrange(year, month_num)
                return f"{self.month} 1-{days_in_month}"
        except ValueError:
            return "Invalid month"
        return "Unknown month"
    
    def get_spent_amount(self):
        # Sum prices of related Items
        total = self.buys.aggregate(total=models.Sum('price'))['total']
        return Decimal(total) if total is not None else Decimal('0.00')

    def get_remaining_amount(self):
        return self.amount - self.get_spent_amount()

    def __str__(self):
        return self.month
    
class Expense(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

class Purchased(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    budget = models.ForeignKey(
        Budget, on_delete=models.CASCADE, related_name="budget", default=1)


class Item(models.Model):
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    date = models.CharField(max_length=500)
    buys = models.ManyToManyField(Budget, related_name='buys')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['name']