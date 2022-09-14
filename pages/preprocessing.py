import dash
import pandas as pd
from dash import html, callback, Input, Output, dash_table
import dash_bootstrap_components as dbc

dash.register_page(__name__, name='Preprocessing',
                   path='/preprocessing', order=1)

layout = html.Div(
    [
        html.Div(id='data-table')
    ]
)


def generate_data_table(df, filename):
    return html.Div([
        html.H5(filename),

        dash_table.DataTable(
            df.to_dict('records'),
            [{'name': i, 'id': i} for i in df.columns],
            page_size=8,
        )
    ])


@callback(
    Output('data-table', 'children'),
    Input('data-store', 'data'),
    Input('filename', 'data')
)
def update(user_uploaded_data, filename):
    df = pd.read_json(user_uploaded_data)
    table = generate_data_table(df, filename['filename'])

    return table
