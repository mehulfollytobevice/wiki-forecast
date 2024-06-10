import re
import os
import json
from collections import defaultdict
import requests
import pandas as pd
from datetime import datetime, timedelta
from data_utils import get_page_to_article_domain_mapping

from config import START_DATE, END_DATE, META_DATA_FOLDER_PATH, PAGE_TO_CATEGORY_FILE

page_to_article_domain = get_page_to_article_domain_mapping()


def get_meta_data(page_name, page_to_article_domain=page_to_article_domain):
    article, domain = page_to_article_domain[page_name]
    sanitized_article = sanitize_filename(article)
    meta_data_fp = os.path.join(META_DATA_FOLDER_PATH, f"{sanitized_article}_{domain}.csv")
    if not os.path.exists(meta_data_fp):
        return None
    meta_df = pd.read_csv(meta_data_fp)
    meta_df = meta_df.drop(columns = [
         'mw-undo',
         'mw-rollback',
         'android app edit',
         'ios app edit',
         'mw-new-redirect',
         'mw-removed-redirect',
         'mw-blank',
         'mw-changed-redirect-target'
    ])
    meta_df['date'] = pd.to_datetime(meta_df['date'])
    
    meta_df = meta_df[(meta_df['date'] >= START_DATE) & (meta_df['date'] <= END_DATE)]

    if len(meta_df) == 0:
        return None
    
    # Extract the total_bytes_added of the first row before adding missing dates
    first_nonzero_idx = meta_df['end_of_day_size'].ne(0).idxmax()
    initial_total_bytes_added = meta_df.loc[first_nonzero_idx, 'end_of_day_size'] - meta_df.loc[first_nonzero_idx, 'total_bytes_added']

    # Set the date range to fill missing dates
    all_dates = pd.date_range(start=START_DATE, end=END_DATE, freq='D')
    meta_df = meta_df.set_index('date').reindex(all_dates).reset_index().rename(columns={'index': 'date'})

    # Fill missing values with 0 for the specified columns
    fill_values = {col: 0 for col in ['total_edits', 'total_bytes_added', 'unique_editors', 'mobile edit',
                                      'mobile web edit', 'visualeditor', 'mw-reverted', 'mobile app edit',
                                      'contenttranslation', 'visualeditor-switched']}
    meta_df.fillna(value=fill_values, inplace=True)

    # Forward fill for 'end_of_day_size'
    meta_df['end_of_day_size'] = meta_df['end_of_day_size'].replace(0, pd.NA).ffill()

    # Assign initial_total_bytes_added to initial zeros in 'end_of_day_size'
    initial_zero_indices = meta_df.loc[meta_df['end_of_day_size'].isna()].index
    meta_df.loc[initial_zero_indices, 'end_of_day_size'] = initial_total_bytes_added
    
    meta_df.set_index('date', inplace=True)

    return meta_df


def sanitize_filename(filename):
    return re.sub(r'[\\/:"*?<>|]+', '_', filename)

def fetch_revision_data(article_title, domain, start_date, end_date):
    start_date_str = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
    end_date_str = end_date.strftime('%Y-%m-%dT%H:%M:%SZ')
    revisions = []
    rvcontinue = None

    while True:
        params = {
            'action': 'query',
            'format': 'json',
            'prop': 'revisions',
            'titles': article_title,
            'rvstart': end_date_str,
            'rvend': start_date_str,
            'rvlimit': 'max',
            'rvprop': 'ids|timestamp|user|userid|size|comment|tags',
        }
        if rvcontinue:
            params['rvcontinue'] = rvcontinue

        url = f'https://{domain}/w/api.php'
        response = requests.get(url, params=params)
        data = response.json()

        pages = data['query']['pages']
        for page_id, page_data in pages.items():
            if 'revisions' in page_data:
                revisions.extend(page_data['revisions'])

        if 'continue' in data:
            rvcontinue = data['continue']['rvcontinue']
        else:
            break

    return revisions

def calculate_bytes_added(df):
    df = df.sort_values(by='timestamp').copy()
    df['prev_size'] = df.groupby('date')['size'].shift(1).fillna(df['size'])
    df['bytes_added'] = df['size'] - df['prev_size']
    return df

def aggregate_daily_data(revisions):
    if not revisions:
        return pd.DataFrame()
    df = pd.DataFrame(revisions)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['date'] = df['timestamp'].dt.date

    tag_columns = [
        'mobile edit', 'mobile web edit', 'visualeditor', 'mw-reverted', 'mw-undo',
        'mw-rollback', 'mobile app edit', 'android app edit', 'ios app edit',
        'contenttranslation', 'visualeditor-switched', 'mw-new-redirect',
        'mw-removed-redirect', 'mw-blank', 'mw-changed-redirect-target'
    ]

    for tag in tag_columns:
        df[tag] = df['tags'].apply(lambda tags: tag in tags if isinstance(tags, list) else False)

    df = calculate_bytes_added(df)

    daily_aggregation = df.groupby('date').agg(
        total_edits=('revid', 'count'),
        total_bytes_added=('bytes_added', 'sum'),
        unique_editors=('userid', pd.Series.nunique),
        **{tag: (tag, 'sum') for tag in tag_columns},
        end_of_day_size=('size', 'last')
    ).reset_index()
    
    return daily_aggregation

def read_categories_from_json(file_path=PAGE_TO_CATEGORY_FILE):
    with open(file_path, 'r') as json_file:
        category_dict = json.load(json_file)
    return category_dict

def get_cat_to_articles(file_path=PAGE_TO_CATEGORY_FILE):
    category_dict = read_categories_from_json(file_path=file_path)
    
    # Reverse the dictionary to map categories to articles
    category_to_articles = defaultdict(list)
    for article, categories in category_dict.items():
        for category in categories:
            category_to_articles[category].append(article)
            
    return category_to_articles

