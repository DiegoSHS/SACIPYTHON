import json
from utils import createLog

def arduinoReads(arduinoPort):
    line = arduinoPort.readline().decode("utf-8").strip()
    print(line)
    htJson = json.loads(line)
    C = htJson["co2"]
    L = htJson["lum"]
    T = htJson["tds"]
    logs = {
        createLog("cantidad_co2",C),
        createLog("luminosidad",L),
        createLog("tds_agua",T),
    }
    return logs

