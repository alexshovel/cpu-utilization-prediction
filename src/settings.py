from datetime import datetime

app_settings = {
    "target_host": "194.35.127.114",
    "prometheus_port": "9090",
    "target_metric": "gala_gopher_cpu_total_used_per",
    "first_train_date": datetime(2023, 4, 18, 12),
    "last_train_date": datetime(2023, 5, 4, 9),
    "predict_intervals": [30, 60, 300], # 30s, 1min, 5min predictions
    "ignoring_metrics": ['up',]
}
