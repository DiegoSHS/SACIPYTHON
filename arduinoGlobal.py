import serial
import time
import arduino1
import arduino4
from utils import dorequest

apiurl = "https://creepy-pink-lingerie.cyclic.app/api"
# configurar los puertos serie para cada Arduino
arduino1_port = 'COM3'
arduino2_port = 'COM4'
arduino3_port = 'COM5'
arduino4_port = 'COM6'
# configurar la velocidad de baudios para cada Arduino
baud_rate = 9600
# configurar los objetos de puerto serie para cada Arduino
ser1 = serial.Serial(arduino1_port, baud_rate)
ser2 = serial.Serial(arduino2_port, baud_rate)
ser3 = serial.Serial(arduino3_port, baud_rate)
ser4 = serial.Serial(arduino4_port, baud_rate)

serials = [ser1,ser2,ser3,ser4]

def serread1():
    arduino1.ultrasonicState(ser1)
    logs = arduino1.arduinoReads(ser1)
    dorequest("/manylogs",logs)

def serread2():
    arduino4.arduinoReads(ser4)
    logs = arduino4.arduinoReads(ser4)
    dorequest("/manylogs",logs)

def inserts():
    while True:
        serread1()
        serread2()
        time.sleep(60)