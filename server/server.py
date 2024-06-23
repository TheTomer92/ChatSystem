from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, join_room, leave_room, send, emit
import datetime
import os

app = Flask(__name__)

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:password@db:5432/chat')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
socketio = SocketIO(app, async_mode='eventlet')

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    message = db.Column(db.String(200), nullable=False)
    room = db.Column(db.String(80), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now)

with app.app_context():
    db.create_all()

class GetMessages(Resource):
    def get(self):
        room = request.args.get('room')
        if not room:
            return {'error': 'Room is required'}, 400
        
        messages = Message.query.filter_by(room=room).order_by(Message.timestamp.asc()).all()
        messages_list = [{'username': m.username, 'message': m.message, 'timestamp': m.timestamp.isoformat()} for m in messages]
        return jsonify(messages_list)

api = Api(app)
api.add_resource(GetMessages, '/get_messages')

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']

    print(f"{username} joining the room {room}.")

    join_room(room)
    
    print(f"{username} joined the room {room}.")
    
    send(f'{username} has joined the room.', to=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']

    print(f"{username} leaveing the room {room}.")

    leave_room(room)

    print(f"{username} left the room {room}.")

    send(f'{username} has left the room.', to=room)

@socketio.on('new_message')
def on_new_message(data):
    username = data.get('username')
    message = data.get('message')
    room = data.get('room')

    print(f"Server received message {message} from user {username} in room {room}")

    if not username or not message or not room:
        return {'error': 'Username, message, and room are required'}, 400
    
    message_entry = Message(username=username, message=message, room=room)
    db.session.add(message_entry)
    db.session.commit()

    print(f"Server stored message {message} from user {username} in room {room}")

    emit('new_room_message', {
        'username': username,
        'message': message,
        'room': room,
        'timestamp': message_entry.timestamp.isoformat()
    }, to=room)

    print(f"Server sent message {message} from user {username} to room {room}")

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
    print(f"Server started.")
