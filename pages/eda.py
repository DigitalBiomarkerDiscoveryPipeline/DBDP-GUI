import dash
from dash import dcc, html

dash.register_page(
    __name__, name='Exploratory Data Analysis', path='/eda', order=2)

layout = html.Div(
    [
        dcc.Markdown('Start by Uploading Your Data')
    ]
)
