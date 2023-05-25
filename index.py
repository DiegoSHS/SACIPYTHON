import os
import json
import serial
import time
import requests
from threading import Thread
from flask import Flask
from flask_cors import CORS
from datetime import datetime
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


def dorequest(endpoint, data):
    global apiurl
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    try:
        resp = requests.post(apiurl+endpoint, json=data)
        result = resp.json()
        return result
    except Exception as e:
        print(e)
        return False


def ultrasonicState(arduinoPort):
    global apiurl
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    try:
        resp = requests.get(apiurl+'/estado_sensor')
        result = resp.json()
        state = result[0]["state"]
        if state == 1:
            arduinoPort.write(f"4 0\n".encode())  # Envía un byte con valor 1
        elif state == 0:
            arduinoPort.write(f"4 1\n".encode())  # Envía un byte con valor 0
        return state
    except Exception as e:
        print(e)
        return False


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


def serread1(serials):
    ser1 = serials[0]
    ultrasonicState(ser1)
    logs = arduinoReads1(ser1)
    if logs:
        dorequest("/manylogs", logs)


def serread2(serials):
    ser2 = serials[1]
    logs = arduinoReads2(ser2)
    if logs:
        dorequest("/manylogs", logs)


def inserts():
    while True:
        serread1()
        serread2()
        time.sleep(60)


# Crear la aplicación de Flask
app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

# Malla Sombra


@app.route('/encender_malla', methods=['POST'])
def encender_malla():
    # Código para enviar el comando de encendido al Arduino
    ser1.write(f"7 0\n".encode())
    return {'message': 'La malla ha sido encendido.'}


@app.route('/apagar_malla', methods=['POST'])
def apagar_malla():
    ser1.write(f"7 1\n".encode())
    return {'message': 'La malla ha sido apagado.'}

# Aspersore


@app.route('/encender_aspersores', methods=['POST'])
def encender_aspersores():
    ser1.write(f"5 0\n".encode())
    return {'message': 'El aspersor ha sido encendido.'}


@app.route('/apagar_aspersores', methods=['POST'])
def apagar_aspersores():
    ser1.write(f"5 1\n".encode())
    return {'message': 'El aspersor ha sido apagado.'}

# Bomba de agua


@app.route('/encender_bomba', methods=['POST'])
def encender_bomba():
    ser1.write(f"6 0\n".encode())
    return {'message': 'La  bomba ha sido encendido.'}


@app.route('/apagar_bomba', methods=['POST'])
def apagar_bomba():
    ser1.write(f"6 1\n".encode())
    return {'message': 'La bomba ha sido apagado.'}


# Ejecutar la aplicación de Flask y el bucle principal en hilos separados
if __name__ == '__main__':
    # Crear el hilo para el bucle principal
    hilo_arduino = Thread(target=inserts)
    hilo_arduino.start()

    # Ejecutar la aplicación de Flask
    app.run()
