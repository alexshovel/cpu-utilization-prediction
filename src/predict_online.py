#!/usr/bin/env python3

from joblib import dump, load
from settings import app_settings
import requests
import pandas as pd

db_addr = app_settings.get('target_host', '127.0.0.1')
db_port = app_settings.get('prometheus_port', '9090')
api_url = f"http://{db_addr}:{db_port}/api/v1"
predict_intervals = app_settings.get('predict_intervals', [])


def get_current_metric(label):
    response = requests.get(
        f"{api_url}/query",
        params={
            'query': label}).json()
    return response


def get_current_cpu():
    res = get_current_metric(app_settings.get('target_metric'))
    return res['data']['result'][0]['value'][1]


def get_prediction_for_step(step: int):
    res = {}

    try:
        columns = load(f'models/predictor_columns-{step}.joblib')
        model = load(f'models/best_model-{step}.joblib')

        predictors = {}

        for label in columns:
            data = get_current_metric(label)['data']
            predictors.update({label: [data['result'][0]['value'][1], ]},)

        data = pd.DataFrame(predictors)
        return model.predict(data[:1])[0]
    except FileNotFoundError:
        return 0


def get_current_predictions():
    for step in predict_intervals:
        get_prediction_for_step(step)


def predict_cpu(step: int = 0):
    res = {
        'current_cpu': get_current_cpu(),
        'timestamp': 0,
        'predictions': {}}
    if step > 0:
        res['predictions'].update({f'{step}s': get_prediction_for_step(step), })
    else:
        for lstep in predict_intervals:
            res['predictions'].update({f'{lstep}s': get_prediction_for_step(lstep), })
        # get_current_cpu()
        get_current_predictions()
    return res


def run():
    predict_cpu()


if __name__ == '__main__':
    run()
