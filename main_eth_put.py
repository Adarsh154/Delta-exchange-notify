import concurrent.futures
import time

import ETH
import get_responses

if __name__ == "__main__":

    while True:
        time.sleep(10)
        btc_call_club, btc_puts_club, eth_call_club, eth_puts_club = get_responses.get_master_response()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(ETH.ev_eth, eth_puts_club)
