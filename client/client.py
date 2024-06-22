import requests
import threading
import time

# Server URL
SERVER_URL = "http://server:5000"

# Track the last printed timestamp
last_printed_timestamp = None

def get_messages(room):
    try:
        global last_printed_timestamp
        response = requests.get(f"{SERVER_URL}/get_messages", params={"room": room})
        if response.status_code == 200:
            messages = response.json()
            new_messages = []

            for message in messages:
                message_timestamp = message['timestamp']
                if last_printed_timestamp is None or message_timestamp > last_printed_timestamp:
                    new_messages.append(message)
            
            if new_messages:
                last_printed_timestamp = new_messages[-1]['timestamp']
                for message in new_messages:
                    print(f"[{message['timestamp']}] {message['username']}: {message['message']}")
        else:
            print("Failed to get messages")
    except requests.ConnectionError as ex:
        print(f"Error connecting to server: {ex}")


def send_message(username, message, room):
    print(f"Sending message {message} from user {username} to room {room}")
    try:
        payload = {'username': username, 'message': message, 'room': room}    
        response = requests.post(f"{SERVER_URL}/send_message", json=payload)
        if response.status_code != 201:
            print(f"Failed to send message {message} from user {username} to room {room}")
    except requests.ConnectionError as ex:
        print(f"Error connecting to server: {ex}")

def message_listener(room):
    while True:
        get_messages(room)
        time.sleep(1)

def main():
    time.sleep(5)
    print("Client started.")
    username = input("Enter your username: ")
    room = input("Enter the room you want to join: ")

    # Start the message listener thread
    threading.Thread(target=message_listener, daemon=True, args=(room,)).start()

    while True:
        time.sleep(1)
        message = input()
        send_message(username, message, room)

if __name__ == "__main__":
    main()
