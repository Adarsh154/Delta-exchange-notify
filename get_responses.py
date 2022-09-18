import requests
from datetime import datetime

from dateutil.tz import gettz

import utilities
from utilities import logger

url = "https://p-api.delta.exchange/v2/tickers?contract_types=call_options,put_options"

payload = {}
headers = {}


# def get_dates():
#     date_refined = [""] * 2
#     initial_day = datetime.now(tz=gettz('Asia/Kolkata'))
#     i, j = 0, 3
#     if (initial_day.hour > 17) or (initial_day.hour == 17 and initial_day.minute >= 30):
#         if initial_day.weekday() ==4:
#             i=1
#             j=4
#         initial_day = initial_day + timedelta(1)
#     date_refined[0] = initial_day.strftime('%d-%m-%Y')
#     date_refined[1] = (initial_day + timedelta(1)).strftime('%d-%m-%Y')
#     friday = initial_day + timedelta(4 - initial_day.weekday())
#     while True:
#         if i == j:
#             break
#         next_friday = friday + i * timedelta(7)
#         if next_friday.strftime('%d-%m-%Y') not in date_refined:
#             date_refined.append(next_friday.strftime('%d-%m-%Y'))
#             i += 1
#
#     for i in range(2, 4):
#         last_day = (date(initial_day.year, initial_day.month + i, 1) - timedelta(days=1))
#         num = last_day.weekday() % 4
#         if last_day.weekday() < 4:
#             num = 3 + last_day.weekday()
#         x = (last_day - timedelta(num)).strftime('%d-%m-%Y')
#         if x not in date_refined:
#             date_refined.append(x)
#
#     for d in range(len(date_refined)):
#         day = date_refined[d]
#         new_date = '' if day[0] == '0' else day[0]
#         new_date = new_date + day[1:3]
#         #new_date = new_date + ('' if day[3] == '0' else day[3])
#         new_date = new_date + day[3:5]
#         new_date = new_date + day[8:]
#         date_refined[d] = new_date.replace("-", "")
#         # date_refined[d] = new_date
#
#     return date_refined


def get_strike_price_from_symbol(text, coin):
    new_text = text[text.find(coin) + 4:]
    return float(new_text[:new_text.find("-")])


def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start + len(needle))
        n -= 1
    return start


def get_master_response():
    try:
        response = requests.get(url, headers=headers, data=payload)
        BTC_call_buy_master = dict()
        BTC_put_buy_master = dict()
        BTC_call_sell_master = dict()
        BTC_put_sell_master = dict()

        ETH_call_buy_master = dict()
        ETH_put_buy_master = dict()
        ETH_call_sell_master = dict()
        ETH_put_sell_master = dict()

        for r in response.json()['result']:
            date = r['symbol'][find_nth(r['symbol'], "-", 3) + 1:]
            if 'BTC' in r['symbol']:
                if r['contract_type'] == "call_options":
                    if date not in BTC_call_buy_master:
                        BTC_call_buy_master[date] = list()
                        BTC_call_sell_master[date] = list()
                    BTC_call_buy_master[date].append(
                        (r['symbol'], r['quotes']['best_bid'], 'size={}'.format(r['quotes']['bid_size'])))
                    BTC_call_sell_master[date].append(
                        (r['symbol'], r['quotes']['best_ask'], 'size={}'.format(r['quotes']['ask_size'])))
                else:
                    if date not in BTC_put_buy_master:
                        BTC_put_buy_master[date] = list()
                        BTC_put_sell_master[date] = list()
                    BTC_put_buy_master[date].append(
                        (r['symbol'], r['quotes']['best_bid'], 'size={}'.format(r['quotes']['bid_size'])))
                    BTC_put_sell_master[date].append(
                        (r['symbol'], r['quotes']['best_ask'], 'size={}'.format(r['quotes']['ask_size'])))
            elif 'ETH' in r['symbol']:
                if r['contract_type'] == "call_options":
                    if date not in ETH_call_buy_master:
                        ETH_call_buy_master[date] = list()
                        ETH_call_sell_master[date] = list()
                    ETH_call_buy_master[date].append(
                        (r['symbol'], r['quotes']['best_bid'], 'size={}'.format(r['quotes']['bid_size'])))
                    ETH_call_sell_master[date].append(
                        (r['symbol'], r['quotes']['best_ask'], 'size={}'.format(r['quotes']['ask_size'])))
                else:
                    if date not in ETH_put_buy_master:
                        ETH_put_buy_master[date] = list()
                        ETH_put_sell_master[date] = list()
                    ETH_put_buy_master[date].append(
                        (r['symbol'], r['quotes']['best_bid'], 'size={}'.format(r['quotes']['bid_size'])))
                    ETH_put_sell_master[date].append(
                        (r['symbol'], r['quotes']['best_ask'], 'size={}'.format(r['quotes']['ask_size'])))

        # call_buy.sort(key=lambda x: my_func(x[0], 'BTC'), reverse=True)
        # call_sell.sort(key=lambda x: my_func(x[0], 'BTC'), reverse=True)
        for i in BTC_call_sell_master.keys():
            BTC_call_buy_master[i].sort(key=lambda x: get_strike_price_from_symbol(x[0], "BTC"), reverse=True)
            BTC_call_sell_master[i].sort(key=lambda x: get_strike_price_from_symbol(x[0], "BTC"), reverse=True)
            BTC_put_buy_master[i].sort(key=lambda x: get_strike_price_from_symbol(x[0], "BTC"))
            BTC_put_sell_master[i].sort(key=lambda x: get_strike_price_from_symbol(x[0], "BTC"))

            ETH_call_buy_master[i].sort(key=lambda x: get_strike_price_from_symbol(x[0], "ETH"), reverse=True)
            ETH_call_sell_master[i].sort(key=lambda x: get_strike_price_from_symbol(x[0], "ETH"), reverse=True)
            ETH_put_buy_master[i].sort(key=lambda x: get_strike_price_from_symbol(x[0], "ETH"))
            ETH_put_sell_master[i].sort(key=lambda x: get_strike_price_from_symbol(x[0], "ETH"))

        btc_call_club = []
        btc_puts_club = []
        eth_call_club = []
        eth_puts_club = []
        for i in BTC_call_sell_master.keys():
            btc_call_club.append([BTC_call_buy_master[i], BTC_call_sell_master[i], i])
            btc_puts_club.append([BTC_put_buy_master[i], BTC_put_sell_master[i], i])

            eth_call_club.append([ETH_call_buy_master[i], ETH_call_sell_master[i], i])
            eth_puts_club.append([ETH_put_buy_master[i], ETH_put_sell_master[i], i])
        return btc_call_club, btc_puts_club, eth_call_club, eth_puts_club

    except Exception as e:
        logger.error(str(e))


def ev(data, coin):
    buy, sell, date = data
    send_list = []
    c, p = 0, 1
    while c < len(buy) - 1:
        if p == len(buy) - 1:
            c += 1
            p = c + 1
        else:
            try:
                diff_plain = float(int((float(buy[c][1]) - float(sell[p][1])) * 100) / 100)
                if diff_plain >= -5 and (float(buy[c][1]) // 10 > 0):
                    if coin == "BTC" and not ((min(float(buy[c][2][5:]), float(sell[p][2][5:])) > 50) and not (
                            float(buy[c][1]) == float(sell[p][1]) == 2.5) and diff_plain >= -10 and (
                            float(buy[c][1]) // 100 > 0)):
                        p += 1
                        continue
                    if coin == "ETH" and not (float(sell[p][1]) > 20):
                        p += 1
                        continue
                    diff_with_charges = diff_plain - ((float(buy[c][1]) + float(sell[p][1])) * 0.1)
                    to_send = date + "\nSell-" + str(buy[c]) + ", Buy-" + str(sell[p]) + \
                        "\n Diff_plain = {}\nDiff_with_charges " "= {}".format(
                                  diff_plain, diff_with_charges)
                    send_list.append(to_send)
                p += 1
            except TypeError as e:
                p += 1
                continue
    return send_list
