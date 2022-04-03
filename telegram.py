import requests, os


def send_message(text):
    token = os.getenv("ttoken")
    url = "https://api.telegram.org/bot{}/sendMessage?chat_id=-712571332&text" \
          "={}".format(token, text)

    response = requests.get(url)
    if not response.ok:
        return False, "Status code: {}, error {}". format(response.status_code, response.text)

    return True, ""
