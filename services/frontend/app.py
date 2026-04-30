from flask import Flask, send_file, send_from_directory
import os

app = Flask(__name__)


@app.route('/<path:name>')
def serve(name):
    return send_from_directory('static', name)


@app.route('/')
def serve_index():
    return send_file('static/index.html')


if __name__ == '__main__':
    host = '0.0.0.0' if os.getenv('DOCKER_ENV') == 'true' else '127.0.0.1'
    app.run(host=host, port=8002, debug=True)
