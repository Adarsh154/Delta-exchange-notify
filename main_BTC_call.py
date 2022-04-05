import concurrent.futures
import time
from copy import deepcopy

import requests
from datetime import datetime, timedelta
import telegram
import logging

logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d:%H:%M:%S',
                    level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_prices(strike):
    global count, local_count
    mode = "sell" if local_count < count else "buy"
    headers = {
        'Accept': 'application/json'
    }
    local_count += 1
    try:
        r = requests.get('https://api.delta.exchange/v2/l2orderbook/{}'.format(strike), params={
        }, headers=headers)
        if not r.ok:
            r.raise_for_status()
        return strike, r.json()['result'][mode][0]['price']
    except requests.exceptions.RequestException as e:
        logger.error("requests error:" + str(e))
        telegram.send_message(str(e))


# Api call to get strike price symbols
def get_strike_prices(coin):
    all_calls_sell = list()
    global count
    try:
        headers = {
            'Accept': 'application/json'
        }
        r = requests.get('https://api.delta.exchange/v2/products', params={
        }, headers=headers).json()['result']

        for i in r:
            if i['description'] == '{} call option expiring on {}'.format(coin, date_refined):
                all_calls_sell.append(i['symbol'])

    except requests.exceptions.RequestException as e:
        logger.error("requests at strike price error:" + str(e))
        telegram.send_message(str(e))

    all_calls_buy = deepcopy(all_calls_sell)
    count = len(all_calls_buy)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        all_calls_sell = list(executor.map(get_prices, all_calls_sell))
        all_calls_buy = list(executor.map(get_prices, all_calls_buy))

    all_calls_buy.sort(key=lambda x: x[0], reverse=True)
    all_calls_sell.sort(key=lambda x: x[0], reverse=True)
    return all_calls_buy, all_calls_sell


if __name__ == "__main__":
    current_hour = datetime.now().hour
    message_sent = {current_hour: []}
    while True:
        count = 0
        local_count = 0
        time.sleep(156)
        # Get today's or tomorrow's date based on time
        day = (datetime.now()).strftime('%d-%m-%Y')
        if datetime.now().hour > 17 or (datetime.now().hour == 17 and datetime.now().minute >= 30):
            day = (datetime.now() + timedelta(1)).strftime('%d-%m-%Y')
        date_refined = '' if day[0] == '0' else day[0]
        date_refined = date_refined + day[1:3]
        date_refined = date_refined + '' if day[3] == '0' else day[3]
        date_refined = date_refined + day[4:]
        try:
            calls_buy, calls_sell = get_strike_prices(coin="BTC")
        except Exception as e:
            logger.error(str(e))
            telegram.send_message(str(e))
            continue

        c, p = 0, 1
        while c < len(calls_buy) - 1:
            if p == len(calls_buy) - 1:
                c += 1
                p = c + 1
            else:
                diff = float(calls_buy[c][1]) - float(calls_sell[p][1])
                if diff >= 2 and diff > ((float(calls_buy[c][1]) + float(calls_sell[p][1])) * 0.1):
                    to_send = str(calls_buy[c] + calls_sell[p])
                    if datetime.now().hour == current_hour:
                        if to_send not in message_sent[current_hour]:
                            status, error_message = telegram.send_message(to_send, False)
                            message_sent[current_hour].append(to_send)
                            if not status:
                                logger.error("Message send error" + error_message)
                    else:
                        current_hour = datetime.now().hour
                        message_sent = {datetime.now().hour: []}
                        if to_send not in message_sent[current_hour]:
                            status, error_message = telegram.send_message(to_send, False)
                            message_sent[current_hour].append(to_send)
                            if not status:
                                logger.error("Message send error" + error_message)
                p += 1
