import concurrent.futures
import requests
from datetime import datetime, timedelta
import telegram
import logging

logging.basicConfig(filename="std.log",
                    format='%(asctime)s %(message)s',
                    filemode='a')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_prices(strike):
    try:
        headers = {
            'Accept': 'application/json'
        }
        if strike[0] == "C":
            return strike, requests.get('https://api.delta.exchange/v2/l2orderbook/{}'.format(strike), params={
            }, headers=headers).json()['result']['buy'][0]['price']
        else:
            return strike, requests.get('https://api.delta.exchange/v2/l2orderbook/{}'.format(strike), params={
            }, headers=headers).json()['result']['sell'][0]['price']
    except Exception as get_price:
        logger.error(get_price)


# Api call to get strike price symbols
def get_strike_prices(coin):
    all_calls = list()
    all_puts = list()

    try:
        headers = {
            'Accept': 'application/json'
        }
        r = requests.get('https://api.delta.exchange/v2/products', params={
        }, headers=headers).json()['result']

        for i in r:
            if i['description'] in ['{} put option expiring on {}'.format(coin, date_refined),
                                    '{} call option expiring on {}'.format(coin, date_refined)]:
                if i['symbol'][0] == 'C':
                    all_calls.append(i['symbol'])
                else:
                    all_puts.append(i['symbol'])

    except Exception as symbol_error:
        logger.error(symbol_error)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        all_calls = list(executor.map(get_prices, all_calls))
        all_puts = list(executor.map(get_prices, all_puts))

    all_calls.sort(key=lambda x: x[0])
    all_puts.sort(key=lambda x: x[0])
    return all_calls, all_puts


if __name__ == "__main__":
    # Get today's or tomorrow's date based on time
    day = (datetime.now()).strftime('%d-%m-%Y')
    if datetime.now().hour > 17 or (datetime.now().hour == 17 and datetime.now().minute > 30):
        day = (datetime.now() + timedelta(1)).strftime('%d-%m-%Y')
    date_refined = '' if day[0] == '0' else day[0]
    date_refined = date_refined + day[1:3]
    date_refined = date_refined + '' if day[3] == '0' else day[3]
    date_refined = date_refined + day[4:]

    calls, puts = get_strike_prices(coin="ETH")

    c, p = 0, 1
    while c < len(calls) - 1:
        if p == len(calls) - 1:
            c += 1
            p = c + 1
        else:
            if calls[c][1] > puts[p][1]:
                status, error_message = telegram.send_message(str(calls[c] + puts[p]))
                if not status:
                    logger.error(error_message)
            p += 1
