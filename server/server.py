from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
import datetime
import os

app = Flask(__name__)

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:password@db:5432/chat')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    message = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

with app.app_context():
    db.create_all()

class SendMessage(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        message = data.get('message')
      
        print(f"Server received message {message} from user {username}")

        if not username or not message:
            return {'error': 'Username and message are required'}, 400
        
        message_entry = Message(username=username, message=message)
        db.session.add(message_entry)
        db.session.commit()

        print(f"Server stored message {message} from user {username}")

        return {'message': 'Message sent successfully'}, 201

class GetMessages(Resource):
    def get(self):
        messages = Message.query.order_by(Message.timestamp.asc()).all()
        messages_list = [{'username': m.username, 'message': m.message, 'timestamp': m.timestamp.isoformat()} for m in messages]
        return jsonify(messages_list)

api = Api(app)
api.add_resource(SendMessage, '/send_message')
api.add_resource(GetMessages, '/get_messages')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
    print(f"Server started.")
