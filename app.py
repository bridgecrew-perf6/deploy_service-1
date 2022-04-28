import json
import os
from flask import Flask, request, jsonify, Response

from docker_utils import docker_handler
from handlers import process_request, get_image_name

app = Flask(__name__)
AUTH_TOKEN = os.getenv('AUTH_TOKEN', None)


@app.route('/', methods=['POST'])
def process_webhook() -> tuple[Response, int]:
    if request.headers.get('Authorization', '') != AUTH_TOKEN:
        return jsonify({'message': 'Bad token'}), 401

    request_data = json.loads(request.data)
    if not process_request(request_data):
        return jsonify({'message': 'Bad request'}), 401

    owner = request_data.get('owner')
    repository = request_data.get('repository')
    tag = request_data.get('tag')
    ports = request_data.get('ports')
    path = request_data.get('path')
    build = request_data.get('build')

    image_name, container_name = get_image_name(owner=owner, repository=repository, tag=tag)
    docker_handler.start(image_name=image_name, container_name=container_name, ports=ports, path=path, build=build)
    return jsonify({'message': 'Deploy complete'}), 200


if __name__ == '__main__':
    if AUTH_TOKEN is None:
        print('Need Auth Token')
        exit(1)

    from logger import init_logger

    init_logger('Deploy service')
    app.run(host='0.0.0.0', port=5000)
