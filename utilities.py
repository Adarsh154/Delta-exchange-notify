import os
from datetime import datetime
import itertools
import requests
import concurrent.futures
from copy import deepcopy
import logging
from datetime import datetime
from dateutil.tz import gettz

log_file = str(datetime.utcnow().strftime('%d_%m_%Y')) + '.log'
logging.basicConfig(filename=log_file,
                    format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d:%H:%M:%S',
                    level=logging.ERROR, filemode='a')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

token = os.getenv("ttoken")
for _ in logging.root.manager.loggerDict:
    logging.getLogger(_).disabled = True


def get_prices(strike, mode):
    headers = {
        'Accept': 'application/json'
    }
    try:
        r = requests.get('https://api.delta.exchange/v2/l2orderbook/{}'.format(strike), params={
        }, headers=headers)
        if not r.ok:
            r.raise_for_status()
        return strike, r.json()['result'][mode][0]['price'], "size={}".format(r.json()['result'][mode][0]['size'])
    except requests.exceptions.RequestException as e:
        if "Internal Server Error".lower() not in str(e).lower():
            send_message(str(e))
        logger.error("requests error:" + str(e))


def my_func(text, coin):
    new_text = text[text.find(coin) + 4:]
    return float(new_text[:new_text.find("-")])


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
        send_message(str(e))
        logger.error("requests at strike price error:" + str(e))

    all_buy = deepcopy(all_sell)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        all_sell = list(executor.map(get_prices, all_sell, itertools.repeat("sell")))
        all_buy = list(executor.map(get_prices, all_buy, itertools.repeat("buy")))

    if call_or_put == "call":
        all_buy.sort(key=lambda x: my_func(x[0], coin), reverse=True)
        all_sell.sort(key=lambda x: my_func(x[0], coin), reverse=True)
    else:
        all_buy.sort(key=lambda x: my_func(x[0], coin))
        all_sell.sort(key=lambda x: my_func(x[0], coin))
    return all_buy, all_sell


def send_message(text, error_message=True):
    if not error_message:
        url = "https://api.telegram.org/bot{}/sendMessage?chat_id=-712571332&text" \
              "={}".format(token, text)
    else:
        url = "https://api.telegram.org/bot{}/sendMessage?chat_id=-746042764&text" \
              "={}".format(token, text)

    response = requests.get(url)
    if not response.ok:
        logger.error("telegram response code: " + str(response.status_code) + "Error message" + response.text)

    return True, ""


def check_and_send(current_hour, message_sent, to_send):
    if datetime.now(tz=gettz('Asia/Kolkata')).hour == current_hour:
        if to_send not in message_sent[current_hour]:
            status, error_message = send_message(to_send, False)
            message_sent[current_hour].append(to_send)
            if not status:
                logger.error("Message send error" + error_message)
    else:
        current_hour = datetime.now(tz=gettz('Asia/Kolkata')).hour
        message_sent = {current_hour: []}
        if to_send not in message_sent[current_hour]:
            status, error_message = send_message(to_send, False)
            message_sent[current_hour].append(to_send)
            if not status:
                logger.error("Message send error" + error_message)
        return message_sent
