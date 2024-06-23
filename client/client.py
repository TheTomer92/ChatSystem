# import requests
# import threading
import time
import socketio

# Server URL
SERVER_URL = "http://server:5000"

sio = socketio.Client()

@sio.event
def connect():
    print("Connected to the server")

@sio.event
def disconnect():
    print("Disconnected from the server")

@sio.event
def new_room_message(data):
    print(f"[{data['timestamp']}] {data['username']}: {data['message']}")

def main():
    # time.sleep(5)
    username = input("Enter your username: ")
    room = input("Enter the room you want to join: ")

    sio.connect(SERVER_URL, wait_timeout=5, retry=True)
    sio.emit('join', {'username': username, 'room': room})

    try:
        while True:
            message = input()
            sio.emit('new_message', {'username': username, 'message': message, 'room': room})
            time.sleep(1)
    except KeyboardInterrupt:
        sio.emit('leave', {'username': username, 'room': room})
        sio.disconnect()

if __name__ == "__main__":
    main()
