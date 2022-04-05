from datetime import datetime
import itertools
import requests
import telegram
import concurrent.futures
from copy import deepcopy
import logging

log_file = str(datetime.utcnow().strftime('%d_%m_%Y')) + '.log'
logging.basicConfig(filename=log_file,
                    format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d:%H:%M:%S',
                    level=logging.INFO, filemode='a')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_prices(strike, mode):
    headers = {
        'Accept': 'application/json'
    }
    try:
        r = requests.get('https://api.delta.exchange/v2/l2orderbook/{}'.format(strike), params={
        }, headers=headers)
        if not r.ok:
            r.raise_for_status()
        return strike, r.json()['result'][mode][0]['price']
    except requests.exceptions.RequestException as e:
        telegram.send_message(str(e))
        logger.error("requests error:" + str(e))


# Api call to get strike price symbols
def get_strike_prices(coin, date_refined, call_or_put):
    all_sell = list()
    try:
        headers = {
            'Accept': 'application/json'
        }
        r = requests.get('https://api.delta.exchange/v2/products', params={
        }, headers=headers).json()['result']

        for i in r:
            if i['description'] == '{} {} option expiring on {}'.format(coin, call_or_put, date_refined):
                all_sell.append(i['symbol'])

    except requests.exceptions.RequestException as e:
        telegram.send_message(str(e))
        logger.error("requests at strike price error:" + str(e))

    all_buy = deepcopy(all_sell)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        all_sell = list(executor.map(get_prices, all_sell, itertools.repeat("sell")))
        all_buy = list(executor.map(get_prices, all_buy, itertools.repeat("buy")))

    if call_or_put == "call":
        all_buy.sort(key=lambda x: x[0], reverse=True)
        all_sell.sort(key=lambda x: x[0], reverse=True)
    else:
        all_buy.sort(key=lambda x: x[0])
        all_sell.sort(key=lambda x: x[0])
    return all_buy, all_sell
