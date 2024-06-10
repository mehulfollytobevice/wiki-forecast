import os
from datetime import datetime

START_DATE = datetime(2015, 7, 1)
END_DATE   = datetime(2017, 9, 10)

INCOMPLETE_ROW_REMOVAL_THRESHOLD = 0

RAW_DATA_FOLDER_PATH = './data/web-traffic-time-series-forecasting'
RAW_DATA_FILE_PATH = os.path.join(RAW_DATA_FOLDER_PATH, 'train_2.csv')

META_DATA_FOLDER_PATH = './data/meta_data'

BASELINE_MODEL_DIR = './models/baseline_arima'
BASELINE_META_MODEL_DIR = './models/baseline_arimax'
SARIMAX_CATEGORY_CLUSTER_DIR = './models/sarimax_cat_cluster'
SARIMAX_SUMMARY_CLUSTER_DIR = './models/sarimax_sum_cluster'

PAGE_TO_CATEGORY_FILE = './data/category_data.json'
ARTICLE_SUMMARIES_FILE = './data/article_summaries.csv'
