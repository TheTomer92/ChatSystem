from flask import Flask, request, jsonify, make_response
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, join_room, leave_room, send, emit
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import os
import secrets
import jwt

app = Flask(__name__)

# Database configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:password@db:5432/chat')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
socketio = SocketIO(app, async_mode='eventlet')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    message = db.Column(db.String(200), nullable=False)
    room = db.Column(db.String(80), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now)

class MessageStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(80), nullable=False)
    seen = db.Column(db.Boolean, default=False)
    
with app.app_context():
    db.create_all()

def token_required(f):
    def decorator(*args, **kwargs):
        token = request.headers.get('x-access-tokens')
        if not token:
            return make_response(jsonify({'message': 'Token is missing'}), 401)
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(username=data['username']).first()
        except:
            return make_response(jsonify({'message': 'Token is invalid'}), 401)
        return f(current_user, *args, **kwargs)
    return decorator

class Register(Resource):
    def post(self):
        data = request.get_json()
        hashed_password = generate_password_hash(data['password'], method='scrypt')
        new_user = User(username=data['username'], password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return make_response(jsonify({'message': 'Registered successfully'}), 200)

class Login(Resource):
    def post(self):
        data = request.get_json()
        print(f"{data['username']} logs in.")
        user = User.query.filter_by(username=data['username']).first()
        if not user or not check_password_hash(user.password, data['password']):
            
            print(f"{data['username']} login failed.")
            return make_response(jsonify({'message': 'Login failed'}), 401)
        
        print(f"{data['username']} check.")
        token = jwt.encode({'username': user.username, 'exp': datetime.datetime.now() + datetime.timedelta(hours=1)}, app.config['SECRET_KEY'])
        
        print(f"{data['username']} verified.")
        return make_response(jsonify({'token': token}), 200)
    
class GetMessages(Resource):
    @token_required
    def get(self):
        room = request.args.get('room')
        if not room:
            return make_response(jsonify({'error': 'Room is required'}), 400)
        
        messages = Message.query.filter_by(room=room).order_by(Message.timestamp.asc()).all()
        messages_list = [{'username': m.username, 'message': m.message, 'timestamp': m.timestamp.isoformat()} for m in messages]
        return make_response(jsonify(messages_list), 200)

api = Api(app)
api.add_resource(Register, '/register')
api.add_resource(Login, '/login')
api.add_resource(GetMessages, '/get_messages')

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    token = data['token']

    print(f"{username} joining the room {room}.")

    try:
        jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
    except:
        send('Authentication error', to=request.sid)
        return
    
    join_room(room)

    print(f"{username} joined the room {room}.")
    
    send(f'{username} has joined the room.', to=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    token = data['token']

    print(f"{username} leaveing the room {room}.")

    try:
        jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
    except:
        send('Authentication error', to=request.sid)
        return
    
    leave_room(room)
    
    print(f"{username} left the room {room}.")

    send(f'{username} has left the room.', to=room)

@socketio.on('new_message')
def on_new_message(data):
    username = data.get('username')
    message = data.get('message')
    room = data.get('room')
    token = data.get('token')

    try:
        jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
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

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
    print(f"Server started.")
