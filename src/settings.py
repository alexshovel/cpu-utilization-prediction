from datetime import datetime

app_settings = {
    "target_host": "194.35.127.114",
    "prometheus_port": "9090",
    "target_metric": "gala_gopher_cpu_total_used_per",
    "first_train_date": datetime(2023, 4, 29, 21),
    #"first_train_date": datetime(2023, 5, 10, 21),
    "last_train_date": datetime(2023, 5, 14, 12),
    "predict_intervals": [30, 60, 300], # 30s, 1min, 5min predictions
    "ignoring_metrics": ['up',],
    "retrain_day_period": 1,
    "db_server": "194.35.127.114",
    "db_name": "postgres",
    "trainer_sql_login": "cpu_trainer",
    "trainer_sql_pass": "IuRaec4Ou0oh",
    "predictor_sql_login": "cpu_predictor",
    "predictor_sql_pass": "eVohmai1woo5",
}
