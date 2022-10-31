import base64
import io

import dash
from dash import html, dcc, dash_table, Input, Output, callback
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import pandas as pd

dash.register_page(__name__, name='Upload Data', path='/', order=0)

layout = html.Div(
    [

        dbc.Row([
            dbc.Col([
                html.H3('Upload Data')
            ], width='auto')
        ], justify='start'),

        # Allow user to upload data
        dbc.Row([
            dbc.Col([
                html.Div([
                    dcc.Upload(
                         id='upload-data',
                         children=html.Div([
                             html.Img(src='assets/file_upload_icon.png',
                                      alt='file_upload',
                                      style={'height': '20%',
                                             'width': '20%',
                                             'margin': '50px 10px'}
                                      ),
                             html.Br(),
                             'Drag and Drop or ',
                             html.A('Select Files',
                                    className='link-primary')
                         ]),
                         style={
                             'width': '800px',
                             'height': '400px',
                             'lineHeight': '60px',
                             'borderWidth': '3px',
                             'backgroundColor': '#f4f6fe',
                             'borderColor': '#c6c6c6',
                             'borderStyle': 'dashed',
                             'borderRadius': '10px',
                             'textAlign': 'center',
                             'margin': '100px 50px'
                         },
                         )
                ], id='upload-container')

            ], width='auto')

        ], justify='center'),

        # Display the uploaded data as table
        html.Div(id='output-data-upload', style={'padding': '0 50px'}),

        # Navigate to processing
        html.Div([
            dbc.Row([
                dbc.Col([
                    html.H5('Looks good? Move on to', style={
                        'display': 'inline-block', 'margin-right': '20px'},),
                    dcc.Link(dbc.Button("Data Cleaning"),
                             href='/data-cleaning'),
                ]),
            ], style={'float': 'right', 'margin': '50px 50px'})
        ], hidden=True, id='proceed',)


    ]
)

# Store the uploaded dataframe to central storage after processing, also store the filename.


def generate_df(contents):
    '''
    Generates dataframe from user uploaded raw data files.
    '''

    # Read content of the file and decode
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

    return df


@callback(
    Output('data-store', 'data'),
    Input('upload-data', 'contents')
)
def store_data(contents):
    if contents is None:
        raise PreventUpdate

    df = generate_df(contents)

    return df.to_json()


@callback(
    Output('filename', 'data'),
    Input('upload-data', 'filename')
)
def store_filename(filename):
    if filename is None:
        raise PreventUpdate

    return {'filename': filename}


# Use the stored user data to display data table and figure

def generate_data_table(df, filename):
    return html.Div([
        html.H5(filename),

        dash_table.DataTable(
            df.to_dict('records'),
            [{'name': i, 'id': i} for i in df.columns],
            page_size=8,
        )
    ], style={'margin-top': 50})


@callback(
    Output('output-data-upload', 'children'),
    Output('proceed', 'hidden'),
    Output('upload-container', 'hidden'),
    Input('data-store', 'data'),
    Input('filename', 'data')
)
def update_overview(user_uploaded_data, filename):

    df = pd.read_json(user_uploaded_data)

    # Generate the datatable
    table = generate_data_table(df, filename['filename'])

    return table, False, True
