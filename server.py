import threading
import socket


ENCODING = 'utf-8'
SERVER_ADDRESS = ('127.0.0.1', 15662)
AUTHORIZED_ADMIN_CREDENTIALS = ['admin:adminpass', 'joe:secure']


class Participant:
    def __init__(self, nickname: str, client_socket: socket, is_admin=False):
        self.nickname = nickname
        self.client_socket = client_socket
        self.is_admin = is_admin


def broadcast(message: str, ignore_list=None, admin_only=False):
    if ignore_list is None:
        ignore_list = []
    for participant in participants:
        if participant not in ignore_list:
            if not admin_only or participant.is_admin:
                participant.client_socket.send(message.encode(ENCODING))


def send_to(participant: Participant, message: str):
    return participant.client_socket.send(message.encode(ENCODING))


def receive_from(participant: Participant, size: int = 1024):
    return participant.client_socket.recv(size).decode(ENCODING)


def kick_user(nickname: str):
    try:
        participant_idx = list(map(lambda p: p.nickname, participants)).index(nickname)
    except ValueError:
        print(f'Could not kick {nickname} -- user not found')
        return False
    participant_to_kick = participants[participant_idx]
    participants.remove(participant_to_kick)
    send_to(participant_to_kick, '-- You have been kicked by an admin')
    participant_to_kick.client_socket.close()
    print(f'Kicked {nickname}')
    broadcast(f'-- {nickname} has been kicked')
    return True


def handle_command(participant, message):
    print(f'Command by {participant.nickname}: "{message}"')
    command_message: str = message.strip()
    command_name = command_message.split(' ', 1)[0]
    # non-admin commands
    if command_name == '/admin':
        send_to(participant, '%PASS%')
        password = receive_from(participant)
        if f'{participant.nickname}:{password}' in AUTHORIZED_ADMIN_CREDENTIALS:
            participant.is_admin = True
            print(f'{participant.nickname} is now an admin')
            send_to(participant, '-- You are now an admin')
            broadcast(f'-- User {participant.nickname} is now an admin', [participant], True)
        else:
            send_to(participant, '-- Invalid password')
    elif command_name == '/quit' or command_name == '/exit':
        send_to(participant, '%QUIT%')
        participant.client_socket.close()
    elif command_name == '/online':
        send_to(participant, f'-- Currently online: {list(map(lambda p: p.nickname, participants))}')
    # admin commands
    elif not participant.is_admin:
        send_to(participant, '-- Admin privileges required')
    else:
        if command_name == '/kick':
            nickname_to_kick = command_message[6:]
            if kick_user(nickname_to_kick):
                broadcast(f'-- User {nickname_to_kick} kicked by {participant.nickname}', None, True)
            else:
                send_to(participant, f'-- Could not kick {nickname_to_kick}')
        elif command_name == '/ban':
            nickname_to_ban = command_message[5:]
            if kick_user(nickname_to_ban):
                banned_nicknames.append(nickname_to_ban)
                broadcast(f'-- User {nickname_to_ban} kicked and banned by {participant.nickname}', None, True)
            else:
                send_to(participant, f'-- Could not kick {nickname_to_ban}')
        elif command_name == '/unban':
            nickname_to_unban = command_message[7:]
            try:
                banned_nicknames.remove(nickname_to_unban)
                broadcast(f'-- User {nickname_to_unban} unbanned by {participant.nickname}', None, True)
            except ValueError:
                send_to(participant, f'-- User {nickname_to_unban} was not in ban list')
        elif command_name == '/banned':
            send_to(participant, f'-- Currently banned: {banned_nicknames}')
        else:
            send_to(participant, '-- Invalid command')


def handle(participant: Participant):
    """
    Handle each new input from participant;
    this method runs in a separate thread for each participant
    """
    while True:
        try:
            message = receive_from(participant)
            if message.startswith('/'):
                handle_command(participant, message)
            else:
                broadcast(f'{participant.nickname}: {message}', [participant])
        except Exception as e:
            print(e)
            try:
                participants.remove(participant)
                participant.client_socket.close()
                broadcast(f'-- {participant.nickname} left the chat')
            finally:
                break


def receive():
    """
    Main loop, add new clients to the chat room
    """
    while True:
        client_socket, address = server.accept()
        print(f'Connected with {str(address)}')

        client_socket.send('%NICK%'.encode(ENCODING))
        nickname = client_socket.recv(1024).decode(ENCODING)
        if nickname in banned_nicknames:
            print(f'Connection attempt with banned nickname: "{nickname}"')
            client_socket.send('%BANNED%'.encode(ENCODING))
        else:
            if nickname in list(map(lambda p: p.nickname, participants)):
                print(f'Connection attempt with existing nickname: "{nickname}"')
                client_socket.send('%DUPLICATE%'.encode(ENCODING))
            else:
                new_participant = Participant(nickname, client_socket)
                participants.append(new_participant)

                print(f'New participant: {nickname}')
                broadcast(f'-- User {nickname} joined!', [new_participant])
                send_to(new_participant, '-- Connected to server!')

                thread = threading.Thread(target=handle, args=(new_participant,))
                thread.start()


if __name__ == '__main__':
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(SERVER_ADDRESS)
    server.listen()

    participants = []
    banned_nicknames = []

    print('Server is listening... ')
    receive()
