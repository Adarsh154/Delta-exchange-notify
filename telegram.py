import requests
import os
from datetime import datetime
import logging

log_file = str(datetime.utcnow().strftime('%d_%m_%Y')) + '.log'
logging.basicConfig(filename=log_file,
                    format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d:%H:%M:%S',
                    level=logging.INFO, filemode='a')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def send_message(text, error_message=True):
    token = os.getenv("ttoken")
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
