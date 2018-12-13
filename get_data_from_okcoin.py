"""Script to gather market data from OKCoin Spot Price API."""
import requests
from pytz import utc
from datetime import datetime
from pymongo import MongoClient
from apscheduler.schedulers.blocking import BlockingScheduler



client = MongoClient()
database = client['okcoindb']
collection = database['historical_data']


def tick():
    """Gather market data from OKCoin Spot Price API and insert them into a
       MongoDB collection."""
    ticker = requests.get('https://www.okcoin.com/api/v1/ticker.do?symbol=btc_usd').json()
    # {"date":"1538740508","ticker":{"high":"6591.58","vol":"29.00","last":"6548.66","low":"6510.43","buy":"6548.59","sell":"6549.36"}}
    depth = requests.get('https://www.okcoin.com/api/v1/depth.do?symbol=btc_usd&size=60').json()

    date = datetime.fromtimestamp(int(ticker['date']))
    price = float(ticker['ticker']['last'])
    v_bid = sum([bid[1] for bid in depth['bids']])
    v_ask = sum([ask[1] for ask in depth['asks']])
    collection.insert({'date': date, 'price': price, 'v_bid': v_bid, 'v_ask': v_ask})
    print(date, price, v_bid, v_ask)


def main():
    """Run tick() at the interval of every ten seconds."""
    scheduler = BlockingScheduler(timezone=utc)
    scheduler.add_job(tick, 'interval', seconds=10)
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == '__main__':
    main()
