from django.urls import path
from .views import TradingViewWebhook

urlpatterns = [
    path('webhook/', TradingViewWebhook.as_view(), name='tradingview_webhook'),
]
