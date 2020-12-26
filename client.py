import socket
import threading

SERVER_ADDRESS = ('127.0.0.1', 15662)
ENCODING = 'utf-8'


def handle_server_instruction(message):
    # expected interaction
    if message == '%NICK%':
        client_socket.send(nickname.encode(ENCODING))
    elif message == '%PASS%':
        password = input('Password required: ')
        client_socket.send(password.encode(ENCODING))
    # expected termination
    elif message == '%BANNED%':
        print('You are currently banned')
        client_socket.close()
        exit(1)
    elif message == '%DUPLICATE%':
        print('This nickname is already taken, please reconnect with another one')
        client_socket.close()
        exit(1)
    elif message == '%QUIT%':
        print('Exiting...')
        client_socket.close()
        exit(0)
    else:
        print(f'Received unknown instruction "{message}" from server')


def receive():
    """Pool messages from server (runs in separate thread)"""
    while True:
        try:
            message = client_socket.recv(1024).decode(ENCODING)
            if message.startswith('%'):
                handle_server_instruction(message)
            else:
                print(message)
        except OSError:
            print('An error occurred!')
            client_socket.close()
            break


def write():
    """Hold open input for sending messages (runs in separate thread)"""
    while True:
        message = f'{input("")}'
        client_socket.send(message.encode(ENCODING))


if __name__ == '__main__':
    try:
        nickname = input("Choose a nickname: ")

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(SERVER_ADDRESS)
    except ConnectionRefusedError:
        print('Could not connect to the server. Exiting...')
        exit(1)

    receive_threat = threading.Thread(target=receive)
    receive_threat.start()

    write_thread = threading.Thread(target=write)
    write_thread.start()
