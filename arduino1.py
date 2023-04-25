import json
import requests
from utils import createLog
from requests.structures import CaseInsensitiveDict
from index import apiurl

def ultrasonicState(arduinoPort):
    global apiurl
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    response = requests.get(apiurl+"/estado")
    state = response["state"]
    if state == "1":
        arduinoPort.write(f"4 0\n".encode())  # Envía un byte con valor 1
    elif state == "0":
        arduinoPort.write(f"4 1\n".encode())  # Envía un byte con valor 0
    return state

def arduinoReads(arduinoPort):
    line = arduinoPort.readline().decode("utf-8").strip()
    print(line)
    htJson = json.loads(line)
    H = htJson["Humedad"]
    T = htJson["Temperatura"]
    I = htJson["Intensidad"]
    D = htJson["Distancia"]
    logs = {
        createLog("humedad_aire",H),
        createLog("temperatura_aire",T),
        createLog("radiacion_solar_aire",I),
    }
    return logs

