from datetime import datetime
import requests
from requests.structures import CaseInsensitiveDict
from index import apiurl

def createDatetime():
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    hour = now.strftime("%H:%M:%S")
    return {date, hour}

def createLog(id,value):
    date, hour = createDatetime()
    log = {"id": id,"date": date,"hour":hour,"value": str(value)}
    return log

def dorequest(endpoint,data):
    global apiurl
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    resp = requests.post(apiurl+endpoint, json=data)
    print(resp)