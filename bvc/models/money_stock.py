from django.db import models

class MoneyStock(models.Model):
    treasury = models.PositiveIntegerField(default=0)
    sold_cash = models.PositiveIntegerField(default=0)
    sold_check = models.PositiveIntegerField(default=0)
    