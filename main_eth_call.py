import time
from dateutil.tz import gettz
from datetime import datetime, timedelta
import telegram_code
import utilities
import logging

log_file = str(datetime.utcnow().strftime('%d_%m_%Y')) + '.log'
logging.basicConfig(filename=log_file,
                    format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d:%H:%M:%S',
                    level=logging.DEBUG, filemode='a')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    current_hour = datetime.now(tz=gettz('Asia/Kolkata')).hour
    message_sent = {current_hour: []}

    while True:
        time.sleep(70)
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
            telegram_code.send_message(str(e))
            continue

        c, p = 0, 1
        while c < len(calls_buy) - 1:
            if p == len(calls_buy) - 1:
                c += 1
                p = c + 1
            else:
                diff = float(int((float(calls_buy[c][1]) - float(calls_sell[p][1]))*100)/100)
                if diff >= 0.05 and diff > ((float(calls_buy[c][1]) + float(calls_sell[p][1])) * 0.1):
                    to_send = str(calls_buy[c] + calls_sell[p])+ " Diff = {}".format(
                        diff - ((float(calls_buy[c][1]) + float(calls_sell[p][1])) * 0.1))
                    if datetime.now(tz=gettz('Asia/Kolkata')).hour == current_hour:
                        if to_send not in message_sent[current_hour]:
                            status, error_message = telegram_code.send_message(to_send, False)
                            message_sent[current_hour].append(to_send)
                            if not status:
                                logger.error("Message send error" + error_message)
                    else:
                        current_hour = datetime.now(tz=gettz('Asia/Kolkata')).hour
                        message_sent = {datetime.now(tz=gettz('Asia/Kolkata')).hour: []}
                        if to_send not in message_sent[current_hour]:
                            status, error_message = telegram_code.send_message(to_send, False)
                            message_sent[current_hour].append(to_send)
                            if not status:
                                logger.error("Message send error" + error_message)
                p += 1
