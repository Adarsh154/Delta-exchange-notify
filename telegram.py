import requests, os


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
        return False, "Status code: {}, error {}".format(response.status_code, response.text)

    return True, ""
