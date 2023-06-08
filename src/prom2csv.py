#!/usr/bin/env python3

import requests
import os
import pandas as pd
from settings import app_settings
import time
from io import StringIO
from postgres import writeDataset


def getMetric(api_url: str, label: str, start: str, end: str, step: int=90):
    ''' Parsing metrics from prometheus '''
    valid_answer = False
    date_chunks = 2

    while not valid_answer:
        date_list = []
        delta = (end - start)/date_chunks

        for i in range(1, date_chunks + 1):
            date_list.append((start+i*delta).isoformat("T")+"Z")
        date_pairs = []

        for idx, date in enumerate(date_list):
            if idx > 0:
                date_pairs.append((date_list[idx-1], date_list[idx]))

        response = requests.get(
            f"{api_url}/query_range",
            params={
                'query': label,
                'start': date_pairs[0][0],
                'end': date_pairs[0][1],
                'step': f'{step}s'}).json()

        if response['status'] == 'success':
            valid_answer = True
        else:
            date_chunks += 1


    res = { 'times': [], 'vals':[] }

    for pair in date_pairs:
        response = requests.get(
            f"{api_url}/query_range",
            params={
                'query': label,
                'start': pair[0],
                'end': pair[1],
                'step': f'{step}s'}).json()

        #print('RESULT_LEN', label, len(response['data']['result']))
        #time.sleep(0.1)
        try:
            for vals in response['data']['result'][0]['values']:
                res['times'].append(vals[0])
                res['vals'].append(vals[1])
        except IndexError:
            pass

    return res


def run():
    ''' main run '''
    db_addr = app_settings.get('target_host', '127.0.0.1')
    db_port = app_settings.get('prometheus_port', '9090')
    api_url = f"http://{db_addr}:{db_port}/api/v1"

    response = requests.get(f"{api_url}/label/__name__/values").json()

    if 'success' in response.get('status', 'failed'):
        labels = response.get('data', [])

    # generating train CSV
    for step in app_settings.get('predict_intervals', []):
        res = {}
        start = app_settings.get("first_train_date")
        end = app_settings.get("last_train_date")
        target_data = getMetric(api_url, app_settings.get('target_metric'), start, end, step)
        len_of_metric = len(target_data['times'])
        res.update({'timestamp': target_data['times']})
        res.update({app_settings.get('target_metric'):target_data['vals']})

        for lbl in labels:
            try:
                data = getMetric(api_url, lbl, start, end, step)
                if lbl not in app_settings.get('ignoring_metrics') and len_of_metric == len(data['times']) and len(set(data['vals'])) > 2:
                    res.update({lbl:data['vals'],})
            except Exception as e:
                pass
                #print('ERROR', e)

        if not os.path.exists('datasets'):
            os.makedirs('datasets')

        if len(res) > 2 and False:
            s = StringIO()
            pd.DataFrame.from_dict(res).drop('timestamp', axis=1).to_csv(s, index=False)
            writeDataset(f'dataset-{step}', s.getvalue())

if __name__ == '__main__':
    run()

