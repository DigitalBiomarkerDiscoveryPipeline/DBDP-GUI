import dash
import pandas as pd
from dash import html, callback, Input, Output, State, dash_table, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, name='Data Cleaning',
                   path='/data-cleaning', order=1)

## Layout 
layout = html.Div([
        # Headers
        html.H1('Clean your dataset'),
        html.H5('Edit the table directly / use the GUI buttons below.'),

        # Data table
        html.Div(id='data-table'),

        # Buttons 
        html.Button('Add Column', id='add-column'),
        html.Button('Fill Missing Values', id='fill-values', n_clicks=0),

        # Modal Dialog
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Fill Missing Values")),

                dbc.ModalBody([
                    dbc.Row([
                            dbc.Col([
                                dbc.Label("Person ID Column:"),
                                dcc.Dropdown(id="person-id-dropdown", 
                                placeholder="The column that holds user ID."),
                            ]),
                            dbc.Col([
                                dbc.Label("Method"),
                                dcc.Dropdown(
                                    id="method-dropdown",
                                    options=[
                                        {"label": "Bfill", "value": 'bfill'},
                                        {"label": "Backfill", "value": 'backfill'},
                                        {"label": "Pad", "value": 'pad'},
                                        {"label": "Ffill", "value": 'ffill'},
                                        {"label": "Interpolate", "value": 'interpolate'},
                                    ],
                                    placeholder="The method of filling empty values.",
                                ),
                            ]),
                    ]),
                    dbc.Row([
                            dbc.Col([
                                dbc.Label("Columns to Modify:"),
                                dcc.Dropdown(id="columns-to-modify",
                                                multi=True,
                                                placeholder="Which columns to modify.")                                
                            ]),
                            dbc.Col([
                                dbc.Label("Max Number of NaN values:"),
                                dbc.Input(id="max_nan_values", 
                                            type="number",
                                            min = 1,
                                            placeholder="The maximum number of NaN values to fill.")
                            ]),
                    ])
                ]),

                dbc.ModalFooter(
                    dbc.Button(
                        "Submit", id="submit", className="ms-auto", n_clicks=0
                    )
                ),
            ],
            id="modal",
            is_open=False,
            size="xl",
        ),
])

## Call-backs and Methods
def generate_data_table(df, filename):
    '''
        Generates table of uploaded CSV with editable fields.
    '''
    return html.Div([
        dash_table.DataTable(

            # Data
            df.to_dict('records'),

            # Columns
            [{'name': i, 
                'id': i, 
                'renamable': True,
                'deletable': True } 
                for i in df.columns],

            # Settings
            editable=True,
            sort_action='native',
            sort_mode='single',
            row_deletable=True,
            column_selectable='multi',
            page_action='native',
            page_size=8
        )
    ])

@callback(
    Output('data-table', 'children'),
    Input('data-store', 'data'),
    Input('filename', 'data')
)
def update(user_uploaded_data, filename):
    '''
        Updates data table with stored data.
    '''
    df = pd.read_json(user_uploaded_data)
    table = generate_data_table(df, filename['filename'])

    return table

@callback(
    Output('modal', 'is_open'),
    [Input('fill-values', 'n_clicks'), Input("submit", "n_clicks")],
    State('modal', 'is_open'),
)
def toggle_modal(n1, n2, is_open):
    '''
        Used to toggle the modal dialog on button click.
    '''
    if n1 or n2:
        return not is_open
    return is_open

@callback(
    Output('person-id-dropdown', 'options'),
    Output('columns-to-modify', 'options'),
    Input('data-store', 'data'),
)
def get_column_names(data):
    '''
        Returns columns of dataframe for use in modal dropdown
    '''
    df = pd.read_json(data)
    return_list = [{'label': c, 'value': c} for c in df.columns]
    return return_list, return_list