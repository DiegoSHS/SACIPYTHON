
from flask import Flask
from flask_cors import CORS
# Crear la aplicación de Flask
app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

# Malla Sombra


@app.route('/encender_malla', methods=['POST'])
def encender_malla():
    return {'message': 'La malla ha sido encendido.'}


@app.route('/apagar_malla', methods=['POST'])
def apagar_malla():
    return {'message': 'La malla ha sido apagado.'}

# Aspersore


@app.route('/encender_aspersores', methods=['POST'])
def encender_aspersores():
    return {'message': 'El aspersor ha sido encendido.'}


@app.route('/apagar_aspersores', methods=['POST'])
def apagar_aspersores():
    return {'message': 'El aspersor ha sido apagado.'}

# Bomba de agua


@app.route('/encender_bomba', methods=['POST'])
def encender_bomba():
    return {'message': 'La  bomba ha sido encendido.'}


@app.route('/apagar_bomba', methods=['POST'])
def apagar_bomba():
    return {'message': 'La bomba ha sido apagado.'}


# Ejecutar la aplicación de Flask y el bucle principal en hilos separados
if __name__ == '__main__':
    # Crear el hilo para el bucle principal

    # Ejecutar la aplicación de Flask
    app.run()
