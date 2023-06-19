"""this is the SACI module of python"""
import os
import time
import json
import atexit
import socketio
import requests
from threading import Thread
from serial import Serial, SerialException
from requests.structures import CaseInsensitiveDict
API_URL = os.environ.get('API_URL')
# configurar los puertos serie para cada Arduino
ARDUINO1_PORT = '/dev/ttyS0'
ARDUINO2_PORT = '/dev/ttyS1'
ARDUINO3_PORT = '/dev/ttyS2'
# configurar la velocidad de baudios para cada Arduino
BAUD_RATE = 9600
SENSOR_LINES = {
    "ultrasonico": 4,
    "aspersores": 5,
    "actuador_bomba": 6,
    "malla_sombra": 7
}


client = socketio.Client()
serials = []


def setup_socket():
    try:
        if client.connected:
            return client
        client.connect(API_URL)
        print('connection established')
        return client
    except socketio.exceptions.ConnectionError as error:
        print(f"connection failed: {error}")
        return client


@client.on('recieve-newactuator')
def recieve_newactuator(data):
    serial = setup_serials()[0]
    name = data["name"]
    state = data["state"]
    set_sensor_state(serial, name, state)


def setup_serials():
    """stablish serial connection with Arduino and return a list of serials"""
    try:
        global serials
        if serials != []:
            return serials
        ser1 = Serial(ARDUINO1_PORT, BAUD_RATE)
        ser2 = Serial(ARDUINO2_PORT, BAUD_RATE)
        ser3 = Serial(ARDUINO3_PORT, BAUD_RATE)
        serials = [ser1, ser2, ser3]
        return serials
    except SerialException as error:
        print(f"serial connection failed: {error}")
        return False


def create_log(sensor: str, value: bool):
    """Create a log dict"""
    log = {"id": sensor, "value": value}
    return log


def get_sensor_state(id_sensor: str):
    """Get the state of a sensor"""
    try:
        url = f"{API_URL}api/saci/sensor/{id_sensor}/enable"
        resp = requests.get(url, timeout=5)
        result = resp.json()
        return result
    except requests.RequestException as error:
        print(error)
        return error


def send_sensor_state(id_sensor: str, state: bool):
    """Set the state of a sensor"""
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "plain/text"
    try:
        url = f"{API_URL}api/saci/sensor/{id_sensor}/enable"
        resp = requests.post(
            url, json={'enable': state}, timeout=5, headers=headers)
        result = resp.json()
        return result
    except requests.RequestException as error:
        print(error)
        return error


def insert_log(log: dict[str, any]):
    """Send a log to the API"""
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    try:
        url = f"{API_URL}api/saci/logs/"
        resp = requests.post(url, json=log, timeout=5)
        result = resp.json()
        return result
    except requests.RequestException as error:
        print(error)
        return False

# this function will replace the following functions in the future (ultrasonic_state, pump_state, sprinkler_state, ceiling_state)


def set_sensor_state(port: Serial, id_sensor: str, state: bool):
    """Change the state of a sensor"""
    byte = 1 if state else 0
    line = SENSOR_LINES[id_sensor]
    string = f"{line} {byte}\n"
    port.write(string.encode())
    return state


def read_arduino(port: Serial):
    """Read the serial port and return a json"""
    try:
        line = port.readline().decode("utf-8").strip()
        print(line)
        json_line = json.loads(line)
        return json_line
    except SerialException as error:
        print(error)
        return False


def arduino_reads1(port: Serial):
    """Read the lines of the serial port and return of a list of logs"""
    json_line = read_arduino(port)
    if json_line:
        hume = json_line["Humedad"]
        temp = json_line["Temperatura"]
        inte = json_line["Intensidad"]
        dist = json_line["Distancia"]
        logs = [
            create_log("humedad_aire", hume),
            create_log("temperatura_aire", temp),
            create_log("radiacion_solar_aire", inte),
            create_log("ultrasonico", dist),
        ]
        return logs
    return False


def arduino_reads2(port: Serial):
    """Read the lines of the serial port and return of a list of logs"""
    json_line = read_arduino(port)
    if json_line:
        co2 = json_line["co2"]
        lum = json_line["lum"]
        tds = json_line["tds"]
        logs = [
            create_log("cantidad_co2", co2),
            create_log("luminosidad", lum),
            create_log("tds_agua", tds),
        ]
        return logs
    return False


def serial_read(serial_port: Serial, fun: callable):
    """Read the serial port and send the logs to the API"""
    logs = fun(serial_port)
    if logs:
        insert_log(logs)


def inserts(serials: list[Serial], interval: int = 60):
    """Execute the functions for read and update data"""
    while True:
        serial_read(serials[0], arduino_reads1)
        serial_read(serials[1], arduino_reads2)
        time.sleep(interval)


def main():
    """Evaluate the connection with the arduinos and execute the functions"""
    all_serials = setup_serials()
    if not all_serials:
        print("Cannot connect to the arduinos")
    else:
        inserts(all_serials)


def exit():
    """Close the serial ports"""
    sers = setup_serials()
    for serial in sers:
        serial.close()
    logger_thread.join()

if __name__ == "__main__":
    atexit.register(exit)
    logger_thread = Thread(target=main)
    logger_thread.start()
    setup_socket()
