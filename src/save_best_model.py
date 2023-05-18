#!/usr/bin/env python3

import psycopg2
from postgres import setTargetModel
from settings import app_settings

def choose_best_models():
    for step in app_settings.get('predict_intervals', []):
        setTargetModel(step)

if __name__ == '__main__':
    choose_best_models()
