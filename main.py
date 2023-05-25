import os
import json
import serial
import time
import requests
from requests.structures import CaseInsensitiveDict

apiurl = os.environ.get('API_URL')
# configurar los puertos serie para cada Arduino
arduino1_port = '/dev/ttyS0'
arduino2_port = '/dev/ttyS1'
arduino3_port = '/dev/ttyS2'
# configurar la velocidad de baudios para cada Arduino
baud_rate = 9600
# configurar los objetos de puerto serie para cada Arduino


def setSerials():
    try:
        ser1 = serial.Serial(arduino1_port, baud_rate)
        ser2 = serial.Serial(arduino2_port, baud_rate)
        ser3 = serial.Serial(arduino3_port, baud_rate)
        return {ser1, ser2, ser3}
    except Exception as e:
        print(e)
        return False


def createLog(id, value):
    log = {"id": id, "value": value}
    return log


def getsensorState(id):
    global apiurl
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    try:
        resp = requests.get(apiurl+'api/saci/sensor/'+id+'/enable')
        result = resp.json()
        return result
    except Exception as e:
        print(e)
        return e


def setsensorState(id, state):
    global apiurl
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    try:
        resp = requests.put(apiurl+'api/saci/sensor/'+id +
                            '/enable', json={'enable': state})
        result = resp.json()
        return result
    except Exception as e:
        print(e)
        return e


def insertLog(log):
    global apiurl
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    try:
        resp = requests.post(apiurl+'api/saci/logs/', json=log)
        result = resp.json()
        return result
    except Exception as e:
        print(e)
        return False


def ultrasonicState(arduinoPort):
    data = getsensorState("ultrasonico")
    state = data["state"]
    if state == True:
        arduinoPort.write(f"4 0\n".encode())  # Envía un byte con valor 1
    elif state == False:
        arduinoPort.write(f"4 1\n".encode())  # Envía un byte con valor 0
    return state


def pumpState(arduinoPort):
    data = getsensorState("actuador_bomba")
    state = data["state"]
    if state == True:
        arduinoPort.write(f"6 0\n".encode())  # Envía un byte con valor 1
    elif state == False:
        arduinoPort.write(f"6 1\n".encode())  # Envía un byte con valor 0
    return state


def sprinklerState(arduinoPort):
    data = getsensorState("aspersores")
    state = data["state"]
    if state == True:
        arduinoPort.write(f"5 0\n".encode())  # Envía un byte con valor 1
    elif state == False:
        arduinoPort.write(f"5 1\n".encode())  # Envía un byte con valor 0
    return state


def ceilingState(arduinoPort):
    data = getsensorState("malla_sombra")
    state = data["state"]
    if state == True:
        arduinoPort.write(f"7 0\n".encode())  # Envía un byte con valor 1
    elif state == False:
        arduinoPort.write(f"7 1\n".encode())  # Envía un byte con valor 0
    return state


def readArduino(port):
    try:
        line = port.readline().decode("utf-8").strip()
        print(line)
        htJson = json.loads(line)
        return htJson
    except Exception as e:
        print(e)
        return False


def arduinoReads1(arduinoPort):
    htJson = readArduino(arduinoPort)
    if htJson:
        H = htJson["Humedad"]
        T = htJson["Temperatura"]
        I = htJson["Intensidad"]
        D = htJson["Distancia"]
        logs = {
            createLog("humedad_aire", H),
            createLog("temperatura_aire", T),
            createLog("radiacion_solar_aire", I),
            createLog("ultrasonico", D),
        }
        return logs
    else:
        return False


def arduinoReads2(arduinoPort):
    htJson = readArduino(arduinoPort)
    if htJson:
        C = htJson["co2"]
        L = htJson["lum"]
        T = htJson["tds"]
        logs = {
            createLog("cantidad_co2", C),
            createLog("luminosidad", L),
            createLog("tds_agua", T),
        }
        return logs
    else:
        return False


def serialRead(serial, fn):
    logs = fn(serial)
    if logs:
        insertLog(logs)


def inserts(serials, interval=60):
    while True:
        pumpState(serials[0])
        ceilingState(serials[0])
        sprinklerState(serials[0])
        ultrasonicState(serials[0])
        serialRead(serials[0], arduinoReads1)
        serialRead(serials[1], arduinoReads2)
        time.sleep(interval)



def main():
    serials = setSerials()
    if serials:
        inserts(serials)
    else:
        print("No se pudo establecer conexión con los arduinos")

main()