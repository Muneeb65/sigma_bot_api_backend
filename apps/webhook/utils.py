import random
import math
from ib_insync import *


async def get_ib_connection(ib: IB):
    clientId = random.randint(1, 1000)
    try:
        await ib.connectAsync('127.0.0.1', 7497, clientId=clientId)  # Await the async function
    except Exception as e:
        print(f"Error connecting to IB: {e}")
        await ib.disconnect()  # Ensure disconnect is awaited as well if necessary
    return ib

def calculate_contract_quantity(contract_cost, account_balance, percentage_to_spend):
    max_contracts = int(
        account_balance * (percentage_to_spend / 100) / contract_cost)
    if max_contracts <= 0:
        raise ValueError('Not enough funds to place order')
    max_contracts = 1  # Limiting to 1 contract, as in the original code
    return max_contracts


async def get_contract(ib, expiry, action, spyValue, order_id, market_position, market_position_size,
                       prev_market_position_size, position_size, include_Expired):
    spy = Stock('SPY', 'ARCA')
    ind = await ib.qualifyContractsAsync(spy)
    ib.reqMarketDataType(4)
    chains = await ib.reqSecDefOptParamsAsync(spy.symbol, '', spy.secType, spy.conId)

    chain = next(c for c in chains if c.tradingClass == 'SPY' and c.exchange == 'SMART')
    expirations = sorted(exp for exp in chain.expirations)[:2]
    rights = ['P', 'C']
    my_contract = None

    if expiry == 'same_day' and action == 'buy' and order_id == 'Long' and market_position == 'long' and market_position_size == '1' and prev_market_position_size == '0' and position_size == '1':
        exp1 = expirations[0]
        exp2 = expirations[1]
        my_contract = Option('SPY', expirations[0], math.floor(spyValue) + 1, rights[1], 'SMART', tradingClass='SPY')
    elif expiry == 'same_day' and action == 'sell' and order_id == 'ShortEntry' and market_position == 'short' and market_position_size == '1' and prev_market_position_size == '0' and position_size == '-1':
        my_contract = Option('SPY', expirations[0], math.floor(spyValue) - 1, rights[0], 'SMART', tradingClass='SPY')

    # Next Day Orders
    if expiry == 'next_day1' and action == 'buy' and order_id == 'LongEntry' and market_position == 'long' and market_position_size == '1' and prev_market_position_size == '0' and position_size == '1':
        my_contract = Option('SPY', expirations[1], math.floor(spyValue) + 1, rights[1], 'SMART', tradingClass='SPY')
    elif expiry == 'next_day1' and action == 'sell' and order_id == 'Close entry(s) order LongEntry' and market_position_size == '0' and prev_market_position_size == '1' and market_position == 'flat':
        trades = ib.fills()
        for trade in trades:
            if trade.execution.orderId == Option_orders[0]:
                Option_orders.pop()
                order = MarketOrder('sell', trade.execution.shares)
                trade = ib.placeOrder(trade.contract, order)
                ib.disconnect()
                return 'exit'
    elif expiry == 'next_day1' and action == 'sell' and order_id == 'ShortEntry' and market_position == 'short' and market_position_size == '1' and prev_market_position_size == '0' and position_size == '-1':
        my_contract = Option('SPY', expirations[1], math.floor(spyValue), rights[0], 'SMART', tradingClass='SPY')
    elif expiry == 'next_day1' and action == 'buy' and order_id == 'Close entry(s) order ShortEntry' and market_position_size == '0' and prev_market_position_size == '1' and market_position == 'flat':
        trades = ib.fills()
        for trade in trades:
            if trade.execution.orderId == Option_orders[0]:
                Option_orders.pop()
                order = MarketOrder('sell', trade.execution.shares)
                trade = ib.placeOrder(trade.contract, order)
                ib.disconnect()
                return 'exit'

    if my_contract:
        contracts = await ib.qualifyContractsAsync(my_contract)
        return my_contract
    return 'no contract'


def get_fil_px(ib, main_order_id, strike_price, contract_id):
    trades = ib.fills()

    if not trades:
        return 'N/A'

    trade = trades[-1]
    return trade.execution.price


def place_my_order(ib, my_contract, order_action, order_contracts, order_price):
    ticker = ib.reqTickersAsync(my_contract)
    print('ask price', ticker[0].ask)

    price = ticker[0].ask
    main_order = Order()
    main_order.action = order_action
    main_order.orderType = "MKT"  # Change to "LMT" for a limit order
    # main_order.lmtPrice = order_price
    main_order.totalQuantity = order_contracts

    # # stop_loss_order
    # stopLoss = 0.1
    # stop = int(order_price * (1-stopLoss))
    # stop_loss_order = Order()
    # stop_loss_order.action = "sell" if order_action == "buy" else "buy"
    # stop_loss_order.orderType = "STP"
    # stop_loss_order.auxPrice = stop
    # stop_loss_order.totalQuantity = stop
    # stop_loss_order.transmit = False

    # Assign unique orderIds
    main_order.orderId = ib.client.getReqId()

    trade = ib.placeOrder(my_contract, main_order)

    main_order_strike_price = trade.contract.strike
    main_order_contract_id = trade.contract.conId

    # time.sleep(10)

    # fill_px = get_fil_px(ib,main_order.orderId,main_order_strike_price,main_order_contract_id)

    # if fill_px == 'N/A':
    #     return 'Only Main Order Placed'
    # trade.execution.avgPrice

    take_profit = price * (1 + 0.1)

    r_take_profit = round(take_profit, 2)

    print("take_profit", r_take_profit)

    take_profit_order = Order()
    take_profit_order.action = "sell" if order_action == "buy" else "buy"
    take_profit_order.orderType = "LMT"
    take_profit_order.lmtPrice = r_take_profit
    take_profit_order.totalQuantity = main_order.totalQuantity
    take_profit_order.parentId = main_order.orderId
    take_profit_order.orderId = main_order.orderId + 1

    tk = ib.placeOrder(my_contract, take_profit_order)

    print('tk', tk)

    return 'order placed'




