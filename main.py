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
    """stablish serial connection with Arduino and return a list of serials"""
    try:
        ser1 = serial.Serial(ARDUINO1_PORT, BAUD_RATE)
        ser2 = serial.Serial(ARDUINO2_PORT, BAUD_RATE)
        ser3 = serial.Serial(ARDUINO3_PORT, BAUD_RATE)
        return {ser1, ser2, ser3}
    except serial.SerialException as error:
        print(error)
        return False


def create_log(sensor, value):
    """Create a log dict"""
    log = {"id":sensor,"value":value}
    return log


def getsensor_state(id_sensor):
    """Get the state of a sensor"""
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    try:
        url = API_URL+'api/saci/sensor/'+id_sensor+'/enable'
        resp = requests.get(url,timeout=5)
        result = resp.json()
        return result
    except requests.RequestException as error:
        print(error)
        return error


def setsensor_state(id_sensor, state):
    """Set the state of a sensor"""
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    try:
        url = API_URL+'api/saci/sensor/'+id_sensor+'/enable'
        resp = requests.put(url, json={'enable': state}, timeout=5)
        result = resp.json()
        return result
    except requests.RequestException as error:
        print(error)
        return error


def insert_log(log):
    """Send a log to the API"""
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    try:
        url = API_URL+'api/saci/logs/'
        resp = requests.post(url, json=log, timeout=5)
        result = resp.json()
        return result
    except requests.RequestException as error:
        print(error)
        return False


def ultrasonic_state(port):
    """Get the state of the ultrasonic sensor and send it to the Arduino"""
    data = getsensor_state("ultrasonico")
    state = data["state"]
    if state:
        port.write(f"{4} {0}\n".encode())  # Envía un byte con valor 1
    elif not state:
        port.write(f"{4} {1}\n".encode())  # Envía un byte con valor 0
    return state


def pump_state(port):
    """Get the state of the pump and send it to the Arduino"""
    data = getsensor_state("actuador_bomba")
    state = data["state"]
    if state:
        port.write(f"{6} {0}\n".encode())  # Envía un byte con valor 1
    elif not state:
        port.write(f"{6} {1}\n".encode())  # Envía un byte con valor 0
    return state


def sprinkler_state(port):
    """Get the state of the sprinkler and send it to the Arduino"""
    data = getsensor_state("aspersores")
    state = data["state"]
    if state:
        port.write(f"{5} {0}\n".encode())  # Envía un byte con valor 1
    elif not state:
        port.write(f"{5} {1}\n".encode())  # Envía un byte con valor 0
    return state


def ceiling_state(port):
    """Get the state of the ceiling and send it to the Arduino"""
    data = getsensor_state("malla_sombra")
    state = data["state"]
    if state:
        port.write(f"{7} {0}\n".encode())  # Envía un byte con valor 1
    elif not state:
        port.write(f"{7} {1}\n".encode())  # Envía un byte con valor 0
    return state


def read_arduino(port):
    """Read the serial port and return a json"""
    try:
        line = port.readline().decode("utf-8").strip()
        print(line)
        json_line = json.loads(line)
        return json_line
    except serial.SerialException as error:
        print(error)
        return False


def arduino_reads1(port):
    """Read the lines of the serial port and return of a list of logs"""
    json_line = read_arduino(port)
    if json_line:
        hume = json_line["Humedad"]
        temp = json_line["Temperatura"]
        inte = json_line["Intensidad"]
        dist = json_line["Distancia"]
        logs = {
            create_log("humedad_aire", [[hume]]),
            create_log("temperatura_aire", temp),
            create_log("radiacion_solar_aire", inte),
            create_log("ultrasonico", dist),
        }
        return logs
    return False


def arduino_reads2(port):
    """Read the lines of the serial port and return of a list of logs"""
    json_line = read_arduino(port)
    if json_line:
        co2 = json_line["co2"]
        lum = json_line["lum"]
        tds = json_line["tds"]
        logs = {
            create_log("cantidad_co2", co2),
            create_log("luminosidad", lum),
            create_log("tds_agua", tds),
        }
        return logs
    return False


def serial_read(serial, fun):
    """Read the serial port and send the logs to the API"""
    logs = fun(serial)
    if logs:
        insert_log(logs)


def inserts(serials, interval=60):
    """Execute the functions for read and update data"""
    while True:
        pump_state(serials[0])
        ceiling_state(serials[0])
        sprinkler_state(serials[0])
        ultrasonic_state(serials[0])
        serial_read(serials[0], arduino_reads1)
        serial_read(serials[1], arduino_reads2)
        time.sleep(interval)



def main():
    """Evaluate the connection with the arduinos and execute the functions"""
    all_serials = set_serials()
    if not all_serials:
        print("No se pudo establecer conexión con los arduinos")
    else:
        inserts(all_serials)

main()
