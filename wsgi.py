from app import app, socketio

# Gunicorn production entry point
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)