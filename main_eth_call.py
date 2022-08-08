import time
from dateutil.tz import gettz
from datetime import datetime, timedelta
import utilities
from utilities import logger

if __name__ == "__main__":
    current_hour = datetime.now(tz=gettz('Asia/Kolkata')).hour
    message_sent = {current_hour: []}

    while True:
        time.sleep(39)
        # Get today's or tomorrow's date based on time
        day = (datetime.now(tz=gettz('Asia/Kolkata'))).strftime('%d-%m-%Y')
        if datetime.now(tz=gettz('Asia/Kolkata')).hour > 15:
            day = (datetime.now(tz=gettz('Asia/Kolkata')) + timedelta(1)).strftime('%d-%m-%Y')
        date_refined = '' if day[0] == '0' else day[0]
        date_refined = date_refined + day[1:3]
        date_refined = date_refined + '' if day[3] == '0' else day[3]
        date_refined = date_refined + day[4:]
        try:
            calls_buy, calls_sell = utilities.get_strike_prices("ETH", date_refined, "call")
        except Exception as e:
            logger.error(str(e))
            # utilities.send_message(str(e))
            continue

        c, p = 0, 1
        while c < len(calls_buy) - 1:
            if p == len(calls_buy) - 1:
                c += 1
                p = c + 1
            else:
                diff_plain = float(int((float(calls_buy[c][1]) - float(calls_sell[p][1])) * 100) / 100)
                if diff_plain >= 0.0:
                    diff_with_charges = diff_plain - ((float(calls_buy[c][1]) + float(calls_sell[p][1])) * 0.1)
                    to_send = "Sell-" + str(calls_buy[c]) + ", Buy -" + str(calls_sell[p]) + \
                              " \n Diff_plain = {}\nDiff_with_charges = {}".format(
                                  diff_plain, diff_with_charges)
                    if datetime.now(tz=gettz('Asia/Kolkata')).hour == current_hour:
                        if to_send not in message_sent[current_hour]:
                            status, error_message = utilities.send_message(to_send, False)
                            message_sent[current_hour].append(to_send)
                            if not status:
                                logger.error("Message send error" + error_message)
                    else:
                        del message_sent[current_hour]
                        current_hour = datetime.now(tz=gettz('Asia/Kolkata')).hour
                        message_sent = {current_hour: []}
                        if to_send not in message_sent[current_hour]:
                            status, error_message = utilities.send_message(to_send, False)
                            message_sent[current_hour].append(to_send)
                            if not status:
                                logger.error("Message send error" + error_message)
                p += 1
