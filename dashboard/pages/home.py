from dash import html
import dash_bootstrap_components as dbc

layout = dbc.Container([
    html.H1('Wikipedia Web Traffic Forecasting'),
    html.P('Welcome to the Wikipedia Web Traffic Forecasting Dashboard.'),
], fluid=True)
