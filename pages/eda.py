import dash
from dash import dcc, html

dash.register_page(__name__, name='Exploratory Data Analysis', path='/eda')

layout = html.Div(
    [
        dcc.Markdown('Start by Uploading Your Data')
    ]
)
