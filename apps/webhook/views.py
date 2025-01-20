from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import TradingViewAlertSerializer
from .models import TradingViewAlert
import asyncio
# from ib_insync import IB, Stock, MarketOrder

class TradingViewWebhook(APIView):
    def post(self, request, *args, **kwargs):
        serializer = TradingViewAlertSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            
            # Extract the action data
            ticker = serializer.validated_data['ticker']
            action = serializer.validated_data['action']
            price = serializer.validated_data['price']
            
            # Trigger IBKR order logic asynchronously
            asyncio.run(self.place_ib_order(ticker, action, price))
            
            return Response({"message": "Order received and processed"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # async def place_ib_order(self, ticker, action, price):
    #     ib = IB()
    #     await ib.connectAsync('127.0.0.1', 7497, clientId=123)
        
    #     contract = Stock(ticker, 'SMART', 'USD')
    #     await ib.qualifyContractsAsync(contract)
        
    #     order = MarketOrder(action, 1)  # Replace with actual quantity
    #     trade = ib.placeOrder(contract, order)
    #     await trade.orderStatusAsync()
    #     ib.disconnect()
