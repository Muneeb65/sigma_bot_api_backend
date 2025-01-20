from django.db import models

class TradingViewAlert(models.Model):
    ticker = models.CharField(max_length=10)
    action = models.CharField(max_length=10, choices=[('buy', 'Buy'), ('sell', 'Sell')])
    price = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.action} {self.ticker} at {self.price}"
