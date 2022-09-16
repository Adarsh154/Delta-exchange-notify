import concurrent.futures
import itertools
import time
from utilities import logger
import get_responses
from datetime import datetime
import utilities
from dateutil.tz import gettz

if __name__ == "__main__":

    current_hour = datetime.now(tz=gettz('Asia/Kolkata')).hour
    message_sent = {current_hour: []}
    while True:
        time.sleep(10)
        try:
            btc_call_club, btc_puts_club, eth_call_club, eth_puts_club = get_responses.get_master_response()
        except Exception as e:
            logger.error(str(e))
            continue
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(executor.map(get_responses.ev, btc_call_club, itertools.repeat("BTC")))
        if any(results):
            for messages in results:
                for to_send in messages:
                    message_sent = utilities.check_and_send(message_sent, to_send)
        if len(message_sent) > 3:
            del message_sent[list(message_sent.keys())[0]]
