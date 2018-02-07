
from socket_server import socketio
from app import app


if __name__ == '__main__':
    socketio.run(app,'0.0.0.0',8080)
    # app.run(debug=True)
