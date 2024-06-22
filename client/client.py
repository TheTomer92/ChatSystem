import requests
import threading
import time

# Server URL
SERVER_URL = "http://server:5000"

# Track the last printed timestamp
last_printed_timestamp = None

def get_messages():
    global last_printed_timestamp
    response = requests.get(f"{SERVER_URL}/get_messages")
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

def send_message(username, message):
    payload = {'username': username, 'message': message}
    print(f"Sending message {message} from user {username}")
    response = requests.post(f"{SERVER_URL}/send_message", json=payload)
    if response.status_code != 201:
        print(f"Failed to send message {message} from user {username}")

def message_listener():
    while True:
        get_messages()
        time.sleep(1)

def main():
    time.sleep(5)
    print("Client started.")
    username = input("Enter your username: ")

    # Start the message listener thread
    threading.Thread(target=message_listener, daemon=True).start()

    while True:
        time.sleep(1)
        message = input()
        send_message(username, message)

if __name__ == "__main__":
    main()
