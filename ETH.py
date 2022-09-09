from datetime import datetime

from dateutil.tz import gettz

import utilities
from utilities import logger


def ev_eth(data):
    eth_buy, eth_sell, date = data
    current_hour = datetime.now(tz=gettz('Asia/Kolkata')).hour
    message_sent = {current_hour: []}
    c, p = 0, 1
    while c < len(eth_buy) - 1:
        if p == len(eth_buy) - 1:
            c += 1
            p = c + 1
        else:
            diff_plain = float(int((float(eth_buy[c][1]) - float(eth_sell[p][1])) * 100) / 100)
            if diff_plain >= 0.00:
                diff_with_charges = diff_plain - ((float(eth_buy[c][1]) + float(eth_sell[p][1])) * 0.1)
                to_send = date + "\nSell-" + str(eth_buy[c]) + ", Buy-" + str(eth_sell[p]) + \
                    " \n Diff_plain = {}\nDiff_with_charges = {}".format(
                              diff_plain, diff_with_charges)
                if datetime.now(tz=gettz('Asia/Kolkata')).hour == current_hour:
                    if to_send not in message_sent[current_hour]:
                        status, error_message = utilities.send_message(to_send, False)
                        message_sent[current_hour].append(to_send)
                        if not status:
                            logger.error("Message send error" + error_message)
                else:
                    current_hour = datetime.now(tz=gettz('Asia/Kolkata')).hour
                    message_sent = {current_hour: []}
                    if to_send not in message_sent[current_hour]:
                        status, error_message = utilities.send_message(to_send, False)
                        message_sent[current_hour].append(to_send)
                        if not status:
                            logger.error("Message send error" + error_message)
            p += 1
