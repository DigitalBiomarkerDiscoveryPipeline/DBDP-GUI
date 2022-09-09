import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__, name='Preprocessing', path='/preprocessing')

layout = html.Div(
    [
        dbc.Col(
            [

            ]
        )
    ]
)
