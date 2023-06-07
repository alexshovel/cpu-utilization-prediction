#!/usr/bin/env python3

import psycopg2
from psycopg2.extras import RealDictCursor, DictCursor, RealDictRow
import pickle
from settings import *

class DBManager:
    def __init__(self, dbname, user, password, host, port):
        self._dbname = dbname
        self._user = user
        self._password = password
        self._host = host
        self._port = port
        self._connection = None

    def _get_connection(self):
        if not self._connection or self._connection.closed:
            self._connection = psycopg2.connect(
                dbname=self._dbname,
                user=self._user,
                password=self._password,
                host=self._host,
                port=self._port
            )
        return self._connection

    def fetch(self, query: str, variables: dict or tuple = None, verbose=True, fetchall=False, raise_if_empty=True):
        cursor_factory = RealDictCursor if verbose else DictCursor
        connection = self._get_connection()
        try:
            with connection.cursor(cursor_factory=cursor_factory) as cursor:
                cursor.execute(query, variables)
                db_result = cursor.fetchall() if fetchall else cursor.fetchone()
            connection.commit()
        except Exception as e:
            if not connection.closed:
                connection.rollback()
            raise e

        if not db_result:
                return []

        return db_result

    def fetchone(self, query: str, variables: dict or tuple = None, verbose=True) -> RealDictRow:
        db_result = self.fetch(query, variables, verbose, fetchall=False)
        return db_result

    def fetchall(self, query: str, variables: dict or tuple = None, verbose=True, raise_if_empty=True):
        db_result = self.fetch(query, variables, verbose, fetchall=True, raise_if_empty=raise_if_empty)
        return db_result

    def query(self, query: str, variables: dict or tuple = None, verbose=True, fetch=False):
        cursor_factory = RealDictCursor if verbose else DictCursor
        connection = self._get_connection()
        try:
            with connection.cursor(cursor_factory=cursor_factory) as cursor:
                cursor.execute(query, variables)
                db_result = cursor.fetchone() if fetch else cursor.statusmessage
            connection.commit()
        except Exception as e:
            connection.rollback()
            raise e

        return db_result

def writeDataset(dset_name, dset_body):
    dbmanager = DBManager(app_settings.get('db_name','postgres'), app_settings.get('trainer_sql_login'), app_settings.get('trainer_sql_pass'), app_settings.get('db_server'), 5432)
    query = 'INSERT INTO datasets (dataset_name, body) VALUES (%s, %s)'
    db_result = dbmanager.query(query, (dset_name, dset_body))
    return db_result

def readDataset(dset_name):
    dbmanager = DBManager(app_settings.get('db_name','postgres'), app_settings.get('trainer_sql_login'), app_settings.get('trainer_sql_pass'), app_settings.get('db_server'), 5432)
    query = 'SELECT * FROM datasets WHERE dataset_name=%s ORDER BY cdate DESC LIMIT 1'
    db_result = dbmanager.fetchone(query, (dset_name,))
    return db_result

def writeModel(model_name, model_body, model_columns, model_score):
    dbmanager = DBManager(app_settings.get('db_name','postgres'), app_settings.get('trainer_sql_login'), app_settings.get('trainer_sql_pass'), app_settings.get('db_server'), 5432)
    query = 'INSERT INTO models (model_name, body, score, columns) VALUES (%s, %s, %s, %s)'
    db_result = dbmanager.query(query, (model_name, pickle.dumps(model_body), model_score, pickle.dumps(model_columns)))
    return {}

def readBestModel(step):
    dbmanager = DBManager(app_settings.get('db_name','postgres'), app_settings.get('predictor_sql_login'), app_settings.get('predictor_sql_pass'), app_settings.get('db_server'), 5432)
    query = "SELECT * FROM models WHERE model_name LIKE %s ORDER BY score DESC LIMIT 1"
    print(step, query)
    db_result = dbmanager.fetchone(query, (step,))
    return db_result

def readLastModel(step):
    dbmanager = DBManager(app_settings.get('db_name','postgres'), app_settings.get('predictor_sql_login'), app_settings.get('predictor_sql_pass'), app_settings.get('db_server'), 5432)
    query = 'SELECT * FROM models WHERE model_name LIKE %s ORDER BY cdate DESC LIMIT 1'
    db_result = dbmanager.fetchone(query, (step,))
    return db_result

def setTargetModel(step):
    dbmanager = DBManager(app_settings.get('db_name','postgres'), app_settings.get('trainer_sql_login'), app_settings.get('trainer_sql_pass'), app_settings.get('db_server'), 5432)
    best_model = readBestModel(step)
    query = "UPDATE models SET is_target = False WHERE model_name LIKE '%%-%s'"
    dbmanager.query(query, (step,))
    query = 'UPDATE models SET is_target = True WHERE id=%s'
    dbmanager.query(query, (best_model.get('id'),))



if __name__ == '__main__':
    """
    writeDataset('test', 'test')
    ff = readDataset()
    print(ff)
    with open('models/predictor_columns-300.joblib', 'rb') as f:
        content = f.read()
        writeModel('test_model_name', content, content, 0.3333)
    print(readBestModel(30))
    # print(readLastModel(30))
    """



