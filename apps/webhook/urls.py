from django.urls import path
from .views import TradingViewWebhook, webhookView

urlpatterns = [
    path('webhook/', webhookView, name='tradingview_webhook'),
]
