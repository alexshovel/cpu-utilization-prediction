#!/usr/bin/env python3

import pandas as pd
import seaborn as sns
import math
import os
from settings import app_settings
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import pickle
from io import StringIO
from postgres import readDataset, writeModel, readBestModel


def replace_lines(X, y):
    # head - remove last N rows
    # tail - remove first N rows
    return X.head(-1), y.tail(-1)


def build_linear_regression_models(data: pd, step: int):
    target_metric = app_settings.get('target_metric')

    y = data[target_metric]
    X = data.drop(target_metric, axis=1)
    X, y = replace_lines(X, y)

    # print(data.columns)
    try:
        pg_best_model = readBestModel(f'linear_model-{step}')
        #best_model = load(f'models/best_model-{step}.joblib')
        best_model = pickle.load(pg_best_model.get('body'))
        best_score = best_model.score(X, y)
    except BaseException:
        best_model = None
        best_score = 0

    print('Starting from', best_score)
    for i in range(1000):
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, train_size=0.8)

        lr = LinearRegression()
        lr.fit(X_train, y_train)

        if best_score < lr.score(X_test, y_test):
            best_score = lr.score(X_test, y_test)
            best_model = lr
            print(lr.score(X_test, y_test))

    if not os.path.exists('models'):
        os.makedirs('models')

    if best_score:
        #data_new = X_train[:10]
        last_predict = lr.predict(X)
        #print('last_prediction', last_predict)
        #print('last_valid', y_train[:10])
        #print('Last_predict deviation', math.sqrt(mean_squared_error(y, last_predict)))
        best_predict = best_model.predict(X)
        #print('best_prediction', best_predict)
        #print('best_valid', y_train[:10])
        #print('Best_predict deviation', math.sqrt(mean_squared_error(y, best_predict)))
        # print(list(X_train.columns))

        writeModel(
            f'linear_model-{step}',
            best_model,
            list(
                X_train.columns),
            best_score)
    else:
        print('Too small dataset for step', step)


def run():
    for step in app_settings.get('predict_intervals', []):
        pg_data = readDataset(f"dataset-{step}")
        s = StringIO(pg_data.get('body'))
        data = pd.read_csv(s)
        build_linear_regression_models(data, step)


if __name__ == '__main__':
    run()
