from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import AllowAny
from .serializers import TradingViewAlertSerializer
from .models import TradingViewAlert
from asgiref.sync import async_to_sync
import asyncio
from ib_insync import IB, Stock, MarketOrder
from .utils import get_contract, get_ib_connection, place_my_order

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



@api_view(['POST'])
@permission_classes([AllowAny])
def webhookView(request):
    return async_to_sync(webhook_async)(request)

async def webhook_async(request):
    try:
        _ib = IB()
        ib = await get_ib_connection(_ib)  # Properly await this
        if not ib.isConnected():
            return Response({
                'code': 'error',
                'message': 'Not connected to Interactive Brokers API'
            })

        webhook_data = request.data  # Use request.data for DRF
        symbol = webhook_data.get('ticker')
        order_action = webhook_data['strategy'].get('order_action')
        contract_price = float(webhook_data['strategy'].get('order_price'))
        market_position = webhook_data['strategy'].get('market_position')
        market_position_size = webhook_data['strategy'].get('market_position_size')
        prev_market_position_size = webhook_data['strategy'].get('prev_market_position_size')
        expiry = webhook_data['strategy'].get('expiry')
        order_id = webhook_data['strategy'].get('order_id')
        position_size = webhook_data['strategy'].get('position_size')
        include_Expired = webhook_data['strategy'].get('includeExpired')

        # Fetch account summaries and calculate balance
        account_summaries = await ib.accountSummaryAsync()
        filtered_summaries = [
            summary for summary in account_summaries if summary.tag == 'BuyingPower'
        ]
        account_balance = float(filtered_summaries[0].value)

        # Example calculations for max contracts
        one_by_four_balance = int(account_balance * 0.25)
        percentage_to_spend = 50
        max_contracts = 1

        # Validate the required data
        if symbol and order_action and contract_price and expiry and order_id and market_position and market_position_size and prev_market_position_size and position_size and include_Expired:
            my_contract = await get_contract(
                ib, expiry, order_action, contract_price, order_id,
                market_position, market_position_size, prev_market_position_size,
                position_size, include_Expired
            )

            if my_contract == 'no contract':
                return Response({'message': 'No contract found'}, status=404)

            if order_action == 'sell' and order_id == 'ShortEntry' and market_position != 'flat':
                order_action = 'buy'
                await place_my_order(ib, my_contract, order_action, max_contracts, contract_price)
                await ib.disconnect()
                return Response({'message': 'Order placed'})

            elif order_action == 'buy' and order_id == 'Long':
                await place_my_order(ib, my_contract, order_action, max_contracts, contract_price)
                await ib.disconnect()
                return Response({'message': 'Order placed'})

        else:
            return Response({'message': 'Invalid request data'}, status=400)

    except Exception as e:
        print(f"Error processing webhook request: {e}")
        return Response({'code': 'error', 'message': 'Internal server error'}, status=500)
