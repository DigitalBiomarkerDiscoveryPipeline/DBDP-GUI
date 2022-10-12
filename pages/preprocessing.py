import dash
import pandas as pd
from dash import html, dcc, callback, Input, Output, dash_table
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from sympy import false

dash.register_page(__name__, name='Preprocessing',
                   path='/preprocessing', order=1)

layout = html.Div(
    [
        dbc.Row([
                html.Div(id='data-table'),
                ]),
        dbc.Col([
            dbc.Button('Categorize Column', id='cat-button',
                       n_clicks=0, className='mb-3'),
            dcc.Dropdown(['Forward Fill', 'Backward Fill',
                          'Interpolate'], id='fill_na_dropdown', searchable=False)
        ]),
    ]
)


def generate_data_table(df, filename):
    return html.Div([
        html.H5(filename),

        dash_table.DataTable(
            df.to_dict('records'),
            [{'name': i, 'id': i} for i in df.columns],
            page_size=8,
            style_table={'overflowY': 'scroll'}
        )
    ])

# Column Categorization


def categorize_column(df):
    person_id = 'ID'
    time = []

    if len(time) == 0:
        df['Elapsed Time'] = df.index
        df['Elapsed Time'] = df.groupby(
            by=person_id)['Elapsed Time'].apply(lambda x: x - x.iloc[0])

    if len(person_id) == 0:
        df['person_id'] = '00-000'

    return df

# Missing Value Filling


def fill_missing_values(df, person_id_col, how='ffill', columns=[], limit_n=None):
    # df: dataframe to modify
    # person_id_col: name of the person_id column
    # how: users can choose from the following-- ‘backfill’, ‘bfill’, ‘pad’, ‘ffill’, 'interpolate'
    # columns: columns to modify (fill missing values)
    # limit_n: maximum number of consecutive NaN values to fill
    temp = df.copy()

    new_columns = ['filled ' + x for x in columns]
    if how == 'interpolate':
        temp[new_columns] = temp.groupby(person_id_col)[columns].apply(
            lambda x: x.interpolate(limit=limit_n))
    else:
        temp[new_columns] = temp.groupby(person_id_col)[
            columns].fillna(method=how, limit=limit_n)
    return temp


@callback(
    Output('data-table', 'children'),
    Input('data-store', 'data'),
    Input('filename', 'data'),
    Input('cat-button', 'n_clicks'),
    Input('fill_na_dropdown', 'value')

)
def update_data_table(user_uploaded_data, filename, n_clicks, dropdown_value):
    df = pd.read_json(user_uploaded_data)
    print(df)
    # Update column categorization
    if n_clicks > 0:
        df = categorize_column(df)

    # Fill missing value in dataframe
    numeric = ['ECG', 'Apple Watch', 'Empatica',
               'Garmin', 'Fitbit', 'Miband', 'Biovotion']

    option_map = {'Forward Fill': 'ffill', 'Backward Fill':
                  'bfill', 'Interpolate': 'interpolate'}

    if dropdown_value:
        df = fill_missing_values(
            df, 'ID', how=option_map[dropdown_value], columns=numeric
        )

    table = generate_data_table(df, filename['filename'])

    return table
