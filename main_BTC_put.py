import time
from datetime import datetime, timedelta
import telegram_code
import logging

import utilities

log_file = str(datetime.utcnow().strftime('%d_%m_%Y')) + '.log'
logging.basicConfig(filename=log_file,
                    format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d:%H:%M:%S',
                    level=logging.DEBUG, filemode='a')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    current_hour = datetime.now().hour
    message_sent = {current_hour: []}
    while True:
        time.sleep(80)
        # Get today's or tomorrow's date based on time
        day = (datetime.now()).strftime('%d-%m-%Y')
        if datetime.now().hour > 15:
            day = (datetime.now() + timedelta(1)).strftime('%d-%m-%Y')
        date_refined = '' if day[0] == '0' else day[0]
        date_refined = date_refined + day[1:3]
        date_refined = date_refined + '' if day[3] == '0' else day[3]
        date_refined = date_refined + day[4:]
        try:
            puts_buy, puts_sell = utilities.get_strike_prices("BTC", date_refined, "put")
        except Exception as e:
            logger.error(str(e))
            telegram_code.send_message(str(e))
            continue

        c, p = 0, 1
        while c < len(puts_buy) - 1:
            if p == len(puts_buy) - 1:
                c += 1
                p = c + 1
            else:
                diff = float(puts_buy[c][1]) - float(puts_sell[p][1])
                if diff >= 2 and diff > ((float(puts_buy[c][1]) + float(puts_sell[p][1])) * 0.1):
                    to_send = str(puts_buy[c] + puts_sell[p]) + " Diff = {}".format(
                        diff - ((float(puts_buy[c][1]) + float(puts_sell[p][1])) * 0.1))
                    if datetime.now().hour == current_hour:
                        if to_send not in message_sent[current_hour]:
                            status, error_message = telegram_code.send_message(to_send, False)
                            message_sent[current_hour].append(to_send)
                            if not status:
                                logger.error("Message send error" + error_message)
                    else:
                        current_hour = datetime.now().hour
                        message_sent = {datetime.now().hour: []}
                        if to_send not in message_sent[current_hour]:
                            status, error_message = telegram_code.send_message(to_send, False)
                            message_sent[current_hour].append(to_send)
                            if not status:
                                logger.error("Message send error" + error_message)
                p += 1
