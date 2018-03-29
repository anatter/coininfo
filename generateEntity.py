import csv
import datetime
import json
import urllib
import os
from flask import Flask, request, make_response

def getCoinMarketCapData():
    link = "https://api.coinmarketcap.com/v1/ticker/"
    response = urllib.request.urlopen(link)
    data = json.loads(response.read().decode())
    print("Request to coinmarketcap.com successful")
    return data

data = getCoinMarketCapData()
myFile = open('entities.csv', 'w')
for i in range(0,99):
    myFile.write("\""+data[i]['name']+"\",\""+data[i]['name']+"\",\""+data[i]['symbol']+"\"\n")
myFile.close()
