from dash import html, dcc
from dash.dependencies import Input, Output
from app import app
from pages import home, page1, page2
import dash_bootstrap_components as dbc

app.layout = dbc.Container([
    dcc.Location(id='url', refresh=False),
    dbc.NavbarSimple(
        children=[
            dbc.NavItem(dcc.Link('Home', href='/', className='nav-link')),
            dbc.NavItem(dcc.Link('Page 1', href='/page1', className='nav-link')),
            dbc.NavItem(dcc.Link('Page 2', href='/page2', className='nav-link')),
        ],
        brand='Wikipedia Web Traffic Dashboard',
        brand_href='/',
        color='primary',
        dark=True,
    ),
    html.Div(id='page-content')
], fluid=True)

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/page1':
        return page1.layout
    elif pathname == '/page2':
        return page2.layout
    elif pathname == '/':
        return home.layout
    else:
        return '404 - Page not found'

if __name__ == '__main__':
    app.run_server(debug=True)
