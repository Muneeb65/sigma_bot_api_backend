from rest_framework import serializers
from .models import TradingViewAlert

class TradingViewAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = TradingViewAlert
        fields = ['ticker', 'action', 'price']
