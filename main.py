import concurrent.futures
import requests
from datetime import datetime, timedelta

# Get tomorrow's date
tomorrow = (datetime.now() + timedelta(1)).strftime('%d-%m-%Y')
date_refined = ''
for i in range(5):
    if not (tomorrow[i] == '0' and tomorrow[i + 1] != '-'):
        date_refined = date_refined + tomorrow[i]
date_refined = date_refined + tomorrow[5:]


def get_prices(strike):
    return strike, requests.get('https://api.delta.exchange/v2/l2orderbook/{}'.format(strike), params={
    }, headers=headers).json()['result']['buy'][0]['price']


# Api call to get strike price symbols
headers = {
    'Accept': 'application/json'
}
r = requests.get('https://api.delta.exchange/v2/products', params={
}, headers=headers).json()['result']
calls = list()
puts = list()
for i in r:
    if (i['description'] == 'ETH put option expiring on {}'.format(date_refined) or i[
         'description'] == 'ETH call option expiring on {}'.format(date_refined)):
        if i['symbol'][0] == 'C':
            calls.append(i['symbol'])
        else:
            puts.append(i['symbol'])

with concurrent.futures.ThreadPoolExecutor() as executor:
    calls = list(executor.map(get_prices, calls))
    puts = list(executor.map(get_prices, puts))

calls.sort(key=lambda x: x[0])
puts.sort(key=lambda x: x[0])

c, p = 0, 1
while c < len(calls) - 1:
    if p == len(calls) - 1:
        c += 1
        p = c + 1
    else:
        if calls[c][1] < puts[p][1]:
            print(calls[c], puts[p])
        p += 1
