import base64
import io

import dash
from dash import html, dcc, dash_table, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px

from func.preprocess import apple

dash.register_page(__name__, name='Upload Data', path='/')

layout = html.Div(
    [

        dbc.Row([
            dbc.Col([
                html.H3('Welcome! Start by Uploading Data')
            ], width='auto')
        ], justify='center'),

        # Allow user to upload data
        dbc.Row([
            dbc.Col([
                dcc.Upload(
                    id='upload-data',
                    children=html.Div([
                        'Drag and Drop or ',
                        html.A('Select Files', className='link-primary')
                    ]),
                    style={
                        'width': '100%',
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin': '10px'
                    },
                )
            ], width='auto')

        ], justify='center'),

        # Display the uploaded data as table
        html.Div(id='output-data-upload', style={'padding': '0 50px'}),


        # Display Unfiltered ECG data
        html.Div(id='apple-hr-plot')
    ]
)


def generate_df(contents):
    '''
    Generates dataframe from user uploaded raw data files.
    '''

    # Read content of the file and decode
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    df = apple(io.StringIO(decoded.decode('utf-8')))

    return df


def parse_contents(contents, filename):

    df = generate_df(contents)

    return html.Div([
        html.H5(filename),

        dash_table.DataTable(
            df.to_dict('records'),
            [{'name': i, 'id': i} for i in df.columns],
            page_size=8,
        )
    ])


@callback(
    Output('output-data-upload', 'children'),
    Output('apple-hr-plot', 'children'),
    Input('upload-data', 'contents'),
    Input('upload-data', 'filename'),
)
def update_overview(content, filename):
    if content is not None:
        # Generate the datatable
        table = parse_contents(content, filename)

        # Generate the unfiltered ECG plot
        df = generate_df(content)
        fig = px.line(
            x=df["Elapsed_time_(sec)"],
            y=df["HR_Apple"],
            title='Apple Watch Heart Rate Data',
            labels=dict(x="Elapse Time (s)", y="Heart Rate")
        )
        fig = dcc.Graph(figure=fig)

        return table, fig
    raise dash.exceptions.PreventUpdate
