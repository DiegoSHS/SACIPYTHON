from threading import Thread
from arduinoGlobal import inserts
from flask import Flask
from flask_cors import CORS

# Crear la aplicación de Flask
app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

# Malla Sombra
@app.route('/encender_malla', methods=['POST'])
def encender_malla():
    # Código para enviar el comando de encendido al Arduino
    arduino.write(f"7 0\n".encode())
    return {'message': 'La malla ha sido encendido.'}
    
@app.route('/apagar_malla', methods=['POST'])
def apagar_malla():
    arduino.write(f"7 1\n".encode())
    return {'message': 'La malla ha sido apagado.'}

# Aspersore
@app.route('/encender_aspersores', methods=['POST'])
def encender_aspersores():
    arduino.write(f"5 0\n".encode())
    return {'message': 'El aspersor ha sido encendido.'}

@app.route('/apagar_aspersores', methods=['POST'])
def apagar_aspersores():
    arduino.write(f"5 1\n".encode())
    return {'message': 'El aspersor ha sido apagado.'}

# Bomba de agua
@app.route('/encender_bomba', methods=['POST'])
def encender_bomba():
    arduino.write(f"6 0\n".encode())
    return {'message': 'La  bomba ha sido encendido.'}

@app.route('/apagar_bomba', methods=['POST'])
def apagar_bomba():
    arduino.write(f"6 1\n".encode())
    return {'message': 'La bomba ha sido apagado.'}

# Ejecutar la aplicación de Flask y el bucle principal en hilos separados
if __name__ == '__main__':
    # Crear el hilo para el bucle principal
    hilo_arduino = Thread(target=inserts)
    hilo_arduino.start()

    # Ejecutar la aplicación de Flask
    app.run()

