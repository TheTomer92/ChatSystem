from flask import request, jsonify, make_response
from flask_restful import Resource, Api
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import jwt
from .config import Config
from .models import db, User, Message


def token_required(f):
    def decorator(*args, **kwargs):
        token = request.headers.get('x-access-tokens')
        if not token:
            return make_response(jsonify({'message': 'Token is missing'}), 401)
        try:
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
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
        token = jwt.encode({'username': user.username, 'exp': datetime.datetime.now() + datetime.timedelta(hours=1)}, Config.SECRET_KEY)
        
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
    

api = Api()
api.add_resource(Register, '/register')
api.add_resource(Login, '/login')
api.add_resource(GetMessages, '/get_messages')
