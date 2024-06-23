import requests
import time
import socketio
import signal
import sys

SERVER_URL = "http://server:5000"

sio = socketio.Client()
token = None
username = None
room = None


@sio.event
def connect():
    print("Connected to the server")


@sio.event
def disconnect():
    print("Disconnected from the server")


@sio.event
def new_room_message(data):
    print(f"[{data['timestamp']}] {data['username']}: {data['message']}")

    sio.emit('message_seen', {
        'username': username,
        'message_id': data['message_id'],
        'room': room,
        'token': token
    })


@sio.event
def message_seen_ack(data):
    print(f"Message {data['message_id']} seen by {data['username']}")


def register():
    global username
    print("### Register ###")
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    response = requests.post(f"{SERVER_URL}/register", json={'username': username, 'password': password})
    print(response.json())


def login():
    global token, username
    print("### Log in ###")
    while True:
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        response = requests.post(f"{SERVER_URL}/login", json={'username': username, 'password': password})
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            if token:
                print("Logged in successfully")
                break
        else:
            print("Login failed. Please try again.")


def cleanup(signum, frame):
    global username, room, token
    if sio.connected:
        sio.emit('leave', {'username': username, 'room': room, 'token': token})
        sio.disconnect()
    sys.exit(0)

def main():
    global room, username, token

    signal.signal(signal.SIGINT, cleanup)  # Capture Ctrl+C signal and call cleanup

    while True:
        choice = input("Do you want to (1) Register or (2) Login? Enter 1 or 2: ")
        if choice == '1':
            register()
            login()
            break
        elif choice == '2':
            login()
            break
        else:
            print("Invalid choice. Please try again.")

    room = input("Enter the room you want to join: ")

    sio.connect(SERVER_URL)
    sio.emit('join', {'username': username, 'room': room, 'token': token})

    try:
        while True:
            message = input()
            sio.emit('new_message', {'username': username, 'message': message, 'room': room, 'token': token})
            time.sleep(1)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
