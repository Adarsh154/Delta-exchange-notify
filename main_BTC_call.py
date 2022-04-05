import time
from datetime import datetime, timedelta
import telegram
import logging

import utilities

log_file = str(datetime.utcnow().strftime('%d_%m_%Y')) + '.log'
logging.basicConfig(filename=log_file,
                    format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d:%H:%M:%S',
                    level=logging.INFO, filemode='a')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

if __name__ == "__main__":
    current_hour = datetime.now().hour
    message_sent = {current_hour: []}
    while True:
        time.sleep(78)
        # Get today's or tomorrow's date based on time
        day = (datetime.now()).strftime('%d-%m-%Y')
        if datetime.now().hour > 17 or (datetime.now().hour == 17 and datetime.now().minute >= 30):
            day = (datetime.now() + timedelta(1)).strftime('%d-%m-%Y')
        date_refined = '' if day[0] == '0' else day[0]
        date_refined = date_refined + day[1:3]
        date_refined = date_refined + '' if day[3] == '0' else day[3]
        date_refined = date_refined + day[4:]
        try:
            calls_buy, calls_sell = utilities.get_strike_prices("BTC", date_refined, "call")
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
