from app import app
from dash.dependencies import Input, Output

# Example callback
@app.callback(Output('example-output', 'children'), [Input('example-input', 'value')])
def update_output(value):
    return f'You have entered {value}'
