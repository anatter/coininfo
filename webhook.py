#coding: utf8

import os
import json
import urllib
import time
import atexit

from flask import Flask, request, make_response
from flask_assistant import Assistant, ask, tell, context_manager
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime

app = Flask(__name__)
assist = Assistant(app, '/')
data = ""

@assist.action('getCryptoPriceSpecific', mapping={'currency': 'Cryptocurrency'})
def getCryptoPriceSpecific(currency):
    req = request.get_json(silent=True, force=True)
    print(req)
    speech = "leer"

    for i in range(0,99):
        coin = data[i]
        name = coin['name']
        if currency == name:
            priceUSD = "{0:.2f}".format(float(data[i]['price_usd'])).replace('.', ',')
            price = name + " steht aktuell bei " + priceUSD + "$. "
            percentChange = "Der Preis ist in den letzten 24 Stunden um "

            if float(coin['percent_change_24h']) < 0:
                percentChange += coin['percent_change_24h'].replace('.', ',') + "% gefallen. "
            else:
                percentChange += coin['percent_change_24h'].replace('.', ',') + "% gestiegen. "

            speech = price + percentChange + "Möchtest du mehr über " + name + " wissen?"
            break

    return ask(speech)

@assist.action('getCryptoPriceSpecificMORE')
@assist.action('getCryptoPriceSpecificYES')
def getAllInfoFromSpecificCoin():
    req = request.get_json(silent=True, force=True)
    contexts = req['result']['contexts']
    for c in contexts:
        if c['name'] == 'currencyname':
            currencyname = c['parameters']['Cryptocurrency']

    for i in range(0,99):
        coin = data[i]
        if currencyname == coin['name']:
            symbol = coin['symbol']
            rank = coin['rank']
            priceUSD = coin['price_usd']
            volume24h = "{0:,.0f}".format(int(float(coin['24h_volume_usd']))).replace(',', '.')
            marketCap = "{0:,.0f}".format(int(float(coin['market_cap_usd']))).replace(',', '.')
            percentChange24h = coin['percent_change_24h']
            percentChange7d = coin['percent_change_7d']

            speechOne = "Hier sind die aktuellen Daten von " + currencyname + ". "
            speechTwo = "Die Marktkapitalisierung liegt bei " + marketCap +"$ was Platz " + rank + \
            " unter allen Kryptowährungen entspricht. " + "In den letzten 24 Stunden wurden " + symbol + " im Wert von " + volume24h + "$ gehandelt. " 

            speechThree = "Der Preis ist in den letzten 24 Stunden um "
            if float(percentChange24h) < 0:
                speechThree += percentChange24h.replace('.', ',') + "% gefallen. "
            else:
                speechThree += percentChange24h.replace('.', ',') + "% gestiegen. "

            speechFour = "In den letzten 7 Tagen ist der Preis um "
            if float(percentChange7d) < 0:
                speechFour += percentChange7d.replace('.', ',') + "% gefallen. "
            else:
                speechFour += percentChange7d.replace('.', ',') + "% gestiegen. "
            break
 
    return tell(speechOne + speechTwo + speechThree + speechFour + "Das war's.")

def getCoinMarketCapData():
    link = "https://api.coinmarketcap.com/v1/ticker/"
    try:
        response = urllib.request.urlopen(link)
        global data
        data = json.loads(response.read().decode())
        print(str(datetime.now()) + ": Request to coinmarketcap.com successful")
    except:
        print("Error accessing coinmarketcap.com")

scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(
    func=getCoinMarketCapData,
    trigger=IntervalTrigger(seconds=600),
    id='getCoinMarketCapData_job',
    name='get cryptocurrency prices',
    replace_existing=True)
# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())



if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting webhook on port %d" % port)
    getCoinMarketCapData()
    app.run(debug=True, port=port, host='0.0.0.0')