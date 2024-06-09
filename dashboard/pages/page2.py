from dash import html, dcc
from app import app

layout = html.Div([
    html.H1('Page 2'),
    dcc.Link('Go to Page 1', href='/page1'),
    html.Div(id='page-2-content')
])
