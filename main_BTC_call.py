import concurrent.futures
import itertools
import time
from utilities import logger
import get_responses

if __name__ == "__main__":

    while True:
        time.sleep(10)
        try:
            btc_call_club, btc_puts_club, eth_call_club, eth_puts_club = get_responses.get_master_response()
        except Exception as e:
            logger.error(str(e))
            continue
        with concurrent.futures.ThreadPoolExecutor() as executor:
            f = executor.map(get_responses.ev, btc_call_club, itertools.repeat("BTC"))
