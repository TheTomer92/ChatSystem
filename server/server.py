from flask import Flask, request, jsonify
from flask_restful import Resource, Api
import datetime

app = Flask(__name__)
api = Api(app)

messages = []

class SendMessage(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        message = data.get('message')
        
        print(f"Server received message {message} from user {username}")

        if not username or not message:
            return {'error': 'Username and message are required'}, 400
        
        message_entry = {
            'username': username,
            'message': message,
            'timestamp': datetime.datetime.utcnow().isoformat()
        }
        messages.append(message_entry)
        return {'message': 'Message sent successfully'}, 201

class GetMessages(Resource):
    def get(self):
        return jsonify(messages)

api.add_resource(SendMessage, '/send_message')
api.add_resource(GetMessages, '/get_messages')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
    print(f"Server started.")
