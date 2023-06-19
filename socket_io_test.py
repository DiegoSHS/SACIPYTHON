import os
import socketio
API_URL = os.environ.get('API_URL')
sio = socketio.Client()

def setup_socket():
    sio.connect(API_URL)
    print('connection established')

@sio.on('recieve-newactuator')
def recieve_newactuator(data):
    print('New actuator: ', data)
    print(data["name"])
    print(data["state"])

def socket_test():
    setup_socket()
    sio.wait()

if __name__ == '__main__':
    socket_test()