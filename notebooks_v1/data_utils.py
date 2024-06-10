import pandas as pd
from statsmodels.tsa.stattools import adfuller


from config import (
    RAW_DATA_FILE_PATH,
    INCOMPLETE_ROW_REMOVAL_THRESHOLD
)

def load_data(transpose=False, remove_inactive_articles=False, file_path=RAW_DATA_FILE_PATH):
    data = pd.read_csv('../data/train_2.csv')
    data.rename(columns={
        'Page': 'page'
    }, inplace=True)

    if remove_inactive_articles:
        data = remove_incomplete_rows(data)
    
    if transpose:
        data.set_index('page', inplace=True)
        data = data.T
        data.index = pd.to_datetime(data.index)
        
    return data

def extract_page_components(page_name):
    parts = page_name.split('_')
    agent = parts.pop()
    access = parts.pop()
    domain = parts.pop()
    locale = domain.split('.')[0]
    article = '_'.join(parts)
    return article, domain, locale, access, agent


def extract_main_domain(domain):
    if 'wikipedia' in domain:
        return 'wikipedia'
    elif 'wikimedia' in domain:
        return 'wikimedia'
    elif 'mediawiki' in domain:
        return 'mediawiki'
    else:
        return 'other'


def get_date_columns(data):
    date_columns = data.filter(regex=r'\d{4}-\d{2}-\d{2}').columns
    return date_columns

def get_page_info_df(remove_inactive_articles=True):
    raw_data = load_data(remove_inactive_articles=remove_inactive_articles)
    raw_data[['article', 'domain', 'locale', 'access', 'agent']] = raw_data['page'].apply(lambda x: pd.Series(extract_page_components(x)))
    raw_data['main_domain'] = raw_data['domain'].apply(extract_main_domain)
    return raw_data[['page', 'article', 'domain', 'locale', 'access', 'agent', 'main_domain']]

def get_page_to_article_domain_mapping(remove_inactive_articles=True):
    page_info_df = get_page_info_df(remove_inactive_articles=remove_inactive_articles)
    page_to_article_domain = page_info_df.set_index('page')[['article', 'domain']].apply(tuple, axis=1).to_dict()
    return page_to_article_domain

def get_unique_articles(remove_inactive_articles=True):
    page_df_info = get_page_info_df(remove_inactive_articles)
    unique_articles = page_df_info['article'].unique()
    return unique_articles

def get_article_domain_tuples(remove_inactive_articles=True):
    page_info_df = get_page_info_df(remove_inactive_articles)
    unique_article_domain_combinations = page_info_df[['article', 'domain']].drop_duplicates()
    article_domain_tuples = list(unique_article_domain_combinations.itertuples(index=False, name=None))
    return article_domain_tuples

def remove_incomplete_rows(data):
    date_columns = get_date_columns(data)
    data['total_nans'] = data[date_columns].isna().sum(axis=1)
    data = data[data['total_nans'] <= INCOMPLETE_ROW_REMOVAL_THRESHOLD]
    data = data.drop(columns=['total_nans'])
    return data

def check_stationarity(series):
    result = adfuller(series.dropna(), autolag='AIC')
    return result[1] < 0.05 

def filter_articles(cat_to_articles, df):
    valid_articles = set(df.columns)

    for cat, articles in cat_to_articles.items():
        cat_to_articles[cat] = list(set(articles) & valid_articles)
    
    return cat_to_articles
