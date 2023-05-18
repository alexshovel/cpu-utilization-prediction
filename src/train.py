#!/usr/bin/env python3

import pandas as pd
import seaborn as sns
import math
import os
from settings import app_settings
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error
import pickle
from io import StringIO
from postgres import readDataset, writeModel, readBestModel
from argparse import ArgumentParser

script_args = None

def replace_lines(X, y):
    # head - remove last N rows
    # tail - remove first N rows
    return X.head(-1), y.tail(-1)


def train_selected_model(data: pd, step: int):
    global script_args
    target_metric = app_settings.get('target_metric')

    if script_args.regression_type in ['L', 'Linear', 'linear']:
        pg_key = 'linear_model'
        train_iters = 100
    elif script_args.regression_type in ['M', 'MLPRegressor', 'MLPR', 'mlpregressor']:
        pg_key = 'svr_model'
        train_iters = 4

    y = data[target_metric]
    X = data.drop(target_metric, axis=1)
    X, y = replace_lines(X, y)

    try:
        pg_best_model = readBestModel(f'{pg_key}-{step}')
        best_model = pickle.loads(pg_best_model.get('body'))
        best_score = pg_best_model.get('score')
    except BaseException:
        best_model = None
        best_score = -1

    print('Starting from', best_score)

    for i in range(train_iters):
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, train_size=0.8)

        if script_args.regression_type in ['L', 'Linear', 'linear']:
            lr = LinearRegression()
        elif script_args.regression_type in ['S', 'SVR', 'svr']:
            lr = SVR(kernel='rbf', gamma='auto')

        lr.fit(X_train, y_train)
        cur_score = lr.score(X_test, y_test)

        if best_score < cur_score:
            best_score = cur_score
            best_model = lr
        print(cur_score)

    if best_score:
        last_predict = lr.predict(X)
        best_predict = best_model.predict(X)

        writeModel(
            f'{pg_key}-{step}',
            best_model,
            list(
                X_train.columns),
            best_score)
    else:
        print('Too small dataset for step', step)


def run():
    global script_args

    for step in app_settings.get('predict_intervals', []):
        pg_data = readDataset(f"dataset-{step}")
        s = StringIO(pg_data.get('body'))
        data = pd.read_csv(s)
        train_selected_model(data, step)


if __name__ == '__main__':
    parser = ArgumentParser(
        description="Train regression models by regression type")

    parser.add_argument(
        "-m",
        "--model",
        dest="regression_type",
        required=True,
        help="set type of regression Linear or SVR"
    )

    script_args = parser.parse_args()
    run()
