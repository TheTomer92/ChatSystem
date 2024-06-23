from flask import request
from flask_socketio import SocketIO, join_room, leave_room, send, emit
import jwt
from .config import Config
from .models import db, Message, MessageStatus


socketio = SocketIO(async_mode='eventlet')


@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    token = data['token']

    print(f"{username} joining the room {room}.")

    try:
        jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
    except:
        send('Authentication error', to=request.sid)
        return
    
    join_room(room)
    print(f"{username} joined the room {room}.")


@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    token = data['token']

    print(f"{username} leaveing the room {room}.")

    try:
        jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
    except:
        send('Authentication error', to=request.sid)
        return
    
    leave_room(room)
    print(f"{username} left the room {room}.")


@socketio.on('new_message')
def on_new_message(data):
    username = data.get('username')
    message = data.get('message')
    room = data.get('room')
    token = data.get('token')

    try:
        jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
    except:
        send('Authentication error', to=request.sid)
        return

    print(f"Server received message {message} from user {username} in room {room}")

    message_entry = Message(username=username, message=message, room=room)
    db.session.add(message_entry)
    db.session.commit()

    print(f"Server stored message {message} from user {username} in room {room}")

    emit('new_room_message', {
        'username': username,
        'message': message,
        'room': room,
        'timestamp': message_entry.timestamp.isoformat(),
        'message_id': message_entry.id
    }, to=room)

    print(f"Server sent message {message} from user {username} to room {room}")


@socketio.on('message_seen')
def on_message_seen(data):
    message_id = data.get('message_id')
    username = data.get('username')
    room = data.get('room')

    status = MessageStatus.query.filter_by(message_id=message_id, username=username).first()
    if not status:
        status = MessageStatus(message_id=message_id, username=username, seen=True)
        db.session.add(status)
    else:
        status.seen = True
    db.session.commit()

    emit('message_seen_ack', {
        'username': username,
        'message_id': message_id,
        'room': room
    }, to=room)
