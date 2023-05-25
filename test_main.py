import os
import json
import serial
import time
import requests
from requests.structures import CaseInsensitiveDict

API_URL = os.environ.get('API_URL')
# configurar los puertos serie para cada Arduino
ARDUINO1_PORT = '/dev/ttyS0'
ARDUINO2_PORT = '/dev/ttyS1'
ARDUINO3_PORT = '/dev/ttyS2'
# configurar la velocidad de baudios para cada Arduino
BAUD_RATE = 9600

def set_serials():
    try:
        ser1 = serial.Serial(ARDUINO1_PORT, BAUD_RATE)
        ser2 = serial.Serial(ARDUINO2_PORT, BAUD_RATE)
        ser3 = serial.Serial(ARDUINO3_PORT, BAUD_RATE)
        return {ser1, ser2, ser3}
    except serial.SerialException as error:
        print(error)
        return False


def createLog(sensor, value):
    log = {"id": sensor, "value": value}
    return log


def getsensor_state(id_sensor):
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    try:
        url = API_URL+'api/saci/sensor/'+id_sensor+'/enable'
        resp = requests.get(url)
        result = resp.json()
        return result
    except requests.RequestException as error:
        print(error)
        return error


def setsensor_state(id_sensor, state):
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    try:
        url = API_URL+'api/saci/sensor/'+id_sensor+'/enable'
        resp = requests.put(url, json={'enable': state})
        result = resp.json()
        return result
    except requests.RequestException as error:
        print(error)
        return error


def insert_log(log):
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    try:
        url = API_URL+'api/saci/logs/'
        resp = requests.post(url, json=log)
        result = resp.json()
        return result
    except requests.RequestException as error:
        print(error)
        return False


def ultrasonic_state(port):
    data = getsensor_state("ultrasonico")
    state = data["state"]
    if state:
        port.write(f"{4} {0}\n".encode())  # Envía un byte con valor 1
    elif not state:
        port.write(f"{4} {1}\n".encode())  # Envía un byte con valor 0
    return state


def pump_state(port):
    data = getsensor_state("actuador_bomba")
    state = data["state"]
    if state:
        port.write(f"{6} {0}\n".encode())  # Envía un byte con valor 1
    elif not state:
        port.write(f"{6} {1}\n".encode())  # Envía un byte con valor 0
    return state


def sprinkler_state(port):
    data = getsensor_state("aspersores")
    state = data["state"]
    if state:
        port.write(f"{5} {0}\n".encode())  # Envía un byte con valor 1
    elif not state:
        port.write(f"{5} {1}\n".encode())  # Envía un byte con valor 0
    return state


def ceiling_state(arduinoPort):
    data = getsensor_state("malla_sombra")
    state = data["state"]
    if state:
        arduinoPort.write(f"{7} {0}\n".encode())  # Envía un byte con valor 1
    elif not state:
        arduinoPort.write(f"{7} {1}\n".encode())  # Envía un byte con valor 0
    return state


def read_arduino(port):
    try:
        line = port.readline().decode("utf-8").strip()
        print(line)
        htJson = json.loads(line)
        return htJson
    except serial.SerialException as error:
        print(error)
        return False


def arduino_reads1(port):
    htJson = read_arduino(port)
    if htJson:
        hume = htJson["Humedad"]
        temp = htJson["Temperatura"]
        inte = htJson["Intensidad"]
        dist = htJson["Distancia"]
        logs = {
            createLog("humedad_aire", hume),
            createLog("temperatura_aire", temp),
            createLog("radiacion_solar_aire", inte),
            createLog("ultrasonico", dist),
        }
        return logs
    else:
        return False


def arduino_reads2(port):
    htJson = read_arduino(port)
    if htJson:
        co2 = htJson["co2"]
        lum = htJson["lum"]
        tds = htJson["tds"]
        logs = {
            createLog("cantidad_co2", co2),
            createLog("luminosidad", lum),
            createLog("tds_agua", tds),
        }
        return logs
    else:
        return False


def serial_read(serial, fun):
    logs = fun(serial)
    if logs:
        insert_log(logs)


def inserts(serials, interval=60):
    while True:
        pump_state(serials[0])
        ceiling_state(serials[0])
        sprinkler_state(serials[0])
        ultrasonic_state(serials[0])
        serial_read(serials[0], arduino_reads1)
        serial_read(serials[1], arduino_reads2)
        time.sleep(interval)



def test_main():
    serials = set_serials()
    if not serials:
        print("No se pudo establecer conexión con los arduinos")
    else:
        inserts(serials, 60)

test_main()