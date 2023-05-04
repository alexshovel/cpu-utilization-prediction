#!/usr/bin/env python3

import bottle
from bottle import (
    default_app, hook, response, request,
    get)
from predict_online import predict_cpu

bottle.BaseRequest.MEMFILE_MAX = 1024 * 1024
app = default_app()

@get('/api/cpu')
def get_prediction():
    return predict_cpu()

@get('/api/cpu/<step:int>')
def get_prediction_by_step(step: int):
    return predict_cpu(step)


@hook('before_request')
def strip_path():
    request.environ['PATH_INFO'] = request.environ['PATH_INFO'].rstrip('/')


@hook('after_request')
def add_useful_headers():
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Authorization, Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=49800)
