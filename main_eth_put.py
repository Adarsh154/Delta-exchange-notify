import concurrent.futures
import time
from copy import deepcopy

import requests
from datetime import datetime, timedelta
import telegram
import logging

logging.basicConfig(filename="eth_std_put.log",
                    format='%(asctime)s %(message)s',
                    filemode='a')
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
        return strike, r.json()['result'][mode][0]['price']
    except requests.exceptions.RequestException as e:
        logger.error("requests error:" + str(e))
        telegram.send_message(str(e))


# Api call to get strike price symbols
def get_strike_prices(coin):
    all_puts_sell = list()
    global count
    try:
        headers = {
            'Accept': 'application/json'
        }
        r = requests.get('https://api.delta.exchange/v2/products', params={
        }, headers=headers).json()['result']

        for i in r:
            if i['description'] == '{} put option expiring on {}'.format(coin, date_refined):
                all_puts_sell.append(i['symbol'])

    except requests.exceptions.RequestException as e:
        logger.error("requests at strike price error:" + str(e))
        telegram.send_message(str(e))

    all_puts_buy = deepcopy(all_puts_sell)
    count = len(all_puts_buy)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        all_puts_sell = list(executor.map(get_prices, all_puts_sell))
        all_puts_buy = list(executor.map(get_prices, all_puts_buy))

    all_puts_buy.sort(key=lambda x: x[0])
    all_puts_sell.sort(key=lambda x: x[0])
    return all_puts_buy, all_puts_sell


if __name__ == "__main__":
    current_hour = datetime.now().hour
    message_sent = {current_hour: []}
    while True:
        count = 0
        local_count = 0
        time.sleep(3)
        # Get today's or tomorrow's date based on time
        day = (datetime.now()).strftime('%d-%m-%Y')
        if datetime.now().hour > 17 or (datetime.now().hour == 17 and datetime.now().minute >= 30):
            day = (datetime.now() + timedelta(1)).strftime('%d-%m-%Y')
        date_refined = '' if day[0] == '0' else day[0]
        date_refined = date_refined + day[1:3]
        date_refined = date_refined + '' if day[3] == '0' else day[3]
        date_refined = date_refined + day[4:]
        puts_buy, puts_sell = get_strike_prices(coin="ETH")

        c, p = 0, 1
        while c < len(puts_buy) - 1:
            if p == len(puts_buy) - 1:
                c += 1
                p = c + 1
            else:
                if float(puts_buy[c][1]) > float(puts_sell[p][1]):
                    to_send = str(puts_buy[c] + puts_sell[p])
                    if datetime.now().hour == current_hour:
                        if to_send not in message_sent[current_hour]:
                            status, error_message = telegram.send_message(to_send)
                            message_sent[current_hour].append(to_send)
                            if not status:
                                logger.error("Message send error" + error_message)
                    else:
                        current_hour = datetime.now().hour
                        message_sent = {datetime.now().hour: []}
                        if to_send not in message_sent[current_hour]:
                            status, error_message = telegram.send_message(to_send)
                            message_sent[current_hour].append(to_send)
                            if not status:
                                logger.error("Message send error" + error_message)
                p += 1
