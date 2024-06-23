from flask import Flask
from app.config import Config
from app.models import db
from app.routes import api
from app.events import socketio


if __name__ == '__main__':
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    api.init_app(app)
    socketio.init_app(app, async_mode='eventlet')

    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
    print(f"Server started.")
