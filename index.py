import serial
import json
import requests
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

seriales = [ser1,ser2,ser3,ser4]

def lectura():
    for ser in seriales:
        if ser.in_waiting > 0:
            arduino = ser.readline().decode().strip()
            datasjson = json.loads(arduino)
            for data in datasjson:
                dorequest(data)
                
def dorequest(data):
    url = "https://creepy-pink-lingerie.cyclic.app/log/"
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    resp = requests.post(url, json=data)
    print(resp)
    time.sleep(1)

def main():
    while True:
        lectura()

main()
