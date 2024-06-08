from dash import html, dcc, callback, Output, Input
import plotly.graph_objs as go
from app import app
import dash_bootstrap_components as dbc
import pickle
import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
from tqdm import tqdm
from pandas.tseries.holiday import USFederalHolidayCalendar as calendar


aggregated_df = pd.read_csv('data/aggregated_df.csv', index_col='date', parse_dates=True)

# # Load the best models per page
# with open('data/best_models_per_page.pkl', 'rb') as f:
#     best_models_per_page = pickle.load(f)

def smape(actual, forecast):
    return 100 * np.mean(2 * np.abs(forecast - actual) / (np.abs(actual) + np.abs(forecast)))

def plot_forecast_vs_actual(train_series, test_series, train_exog, test_exog, model):
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=train_series.index, y=train_series, mode='lines', name='Train'))
    fig.add_trace(go.Scatter(x=test_series.index, y=test_series, mode='lines', name='Test'))

    # In-sample forecast
    in_sample_forecast = model.fittedvalues
    fig.add_trace(go.Scatter(x=in_sample_forecast.index, y=in_sample_forecast, mode='lines', name='In-sample Forecast'))

    # Out-of-sample forecast
    forecast = model.get_forecast(steps=len(test_series), exog=test_exog)
    forecast_index = pd.date_range(start=test_series.index[0], periods=len(test_series), freq='D')
    forecast_series = pd.Series(forecast.predicted_mean, index=forecast_index)
    fig.add_trace(go.Scatter(x=forecast_series.index, y=forecast_series, mode='lines', name='Out-of-sample Forecast'))

    sMAPE_value = smape(test_series, forecast_series)
    fig.update_layout(
        title=f'Actual vs Forecasted Values (sMAPE: {sMAPE_value:.2f}%)',
        xaxis_title='Date',
        yaxis_title='Page Views',
        legend_title='Legend'
    )
    return fig

def plot_model_forecast(data, page_name, test_size):
    
    # if page_name not in best_models_per_page:
    #     return go.Figure()
    # best_model_info = best_models_per_page[page_name]
    # model = best_model_info['model']
    
    # Load the best model for the given page
    try:
        with open(f'data/best_agg_model_{page_name}.pkl', 'rb') as f:
            best_model_info = pickle.load(f)
    except FileNotFoundError:
        return go.Figure()
    
    model = best_model_info['model']
    
    
    time_series, exog = get_time_series_and_exog(data, page_name)

    if time_series is not None:
        train_series, test_series, train_exog, test_exog = train_test_split(time_series, exog, test_size)
        print(f"Size of train_series: {train_series.shape}, Size of test_series: {test_series.shape} Size of train_exog: {train_exog.shape}, Size of test_exog: {test_exog.shape}")
        forecast_fig = plot_forecast_vs_actual(train_series, test_series, train_exog, test_exog, model)
        return forecast_fig
    return go.Figure()

def get_time_series_and_exog(data, page_name):
    time_series = data[page_name]
    time_series = time_series.asfreq('D')
    
    # Day of the week
    day_of_week = pd.to_datetime(time_series.index).dayofweek
    exog_dow = pd.get_dummies(day_of_week, prefix='dow').astype(int)
    exog_dow.index = time_series.index
    
    # Month of the year
    month_of_year = pd.to_datetime(time_series.index).month
    exog_month = pd.get_dummies(month_of_year, prefix='month').astype(int)
    exog_month.index = time_series.index
    
    # Is weekend
    is_weekend = (day_of_week >= 5).astype(int)
    exog_weekend = pd.DataFrame(is_weekend, index=time_series.index, columns=['is_weekend'])
    
    # Is holiday
    holidays = calendar().holidays(start=time_series.index.min(), end=time_series.index.max())
    is_holiday = time_series.index.isin(holidays).astype(int)
    exog_holiday = pd.DataFrame(is_holiday, index=time_series.index, columns=['is_holiday'])
    
    # Combine all exogenous features
    exog = pd.concat([exog_dow, exog_month, exog_weekend, exog_holiday], axis=1)
    
    return time_series, exog

def train_test_split(series, exog, test_size):
    train = series[:-test_size]
    test = series[-test_size:]
    train_exog = exog[:-test_size]
    test_exog = exog[-test_size:]
    return train, test, train_exog, test_exog

layout = dbc.Container([
    html.H1('Page 1 - Model Forecasting with SARIMAX [Wikipedia Article Clusters based on API Data]'),
    dcc.Dropdown(
        id='cluster-dropdown',
        options=[{'label': f'Cluster {i}', 'value': i} for i in aggregated_df.columns],
        value=aggregated_df.columns[0],
    ),
    dcc.Graph(id='forecast-graph'),
], fluid=True)

@app.callback(
    Output('forecast-graph', 'figure'),
    Input('cluster-dropdown', 'value')
)
def update_forecast(selected_cluster):
    test_size = 30  
    return plot_model_forecast(aggregated_df, selected_cluster, test_size)
