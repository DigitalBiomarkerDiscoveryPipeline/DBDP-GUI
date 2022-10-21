import dash
import pandas as pd
from dash import html, dcc, callback, Input, Output, State, dash_table
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from sympy import false

dash.register_page(__name__, name='Data Cleaning',
                   path='/data-cleaning', order=1)

layout = html.Div([   
        # Data store to hold updated data
        dcc.Store(id='cleaned-data-store', storage_type='local'),

        # Headers
        html.H1('Clean your dataset'),
        html.H5('Edit the table directly / use the GUI buttons below.'),

        # Data table
        html.Div(id='data-table'),

        # Table modification buttons 
        html.Button('Add Column', id='add-column'),
        html.Button('Add Row', id='add-row'),
        html.Button('Fill Missing Values', id='fill-values', n_clicks=0),

        # Save Button
        html.Button('Save your updates', id='save'),

        # Modal Dialog for filling missing values
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
                                        {"label": "Backfill", "value": 'backfill'},
                                        {"label": "Forward Fill", "value": 'ffill'},
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
            id="missing-values-modal",
            is_open=False,
            size="xl",
        ), 
])

## Callbacks

# Table Callbacks
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
            page_size=8,
            export_format='csv',
            export_headers='display',
        )
    ])

@callback(
    Output('data-table', 'children'),
    Input('data-store', 'data'),
    Input('filename', 'data')
)
def update_table(user_uploaded_data, filename):
    '''
        Updates data table with stored data (for use during page transitions).
    '''
    df = pd.read_json(user_uploaded_data)
    table = generate_data_table(df, filename['filename'])

    return table

@callback(
    Output('cleaned-data-store', 'data'),
    Input('save', 'n_clicks'),
    Input('data-table', 'children'),
    State('cleaned-data-store', 'data')
)
def save_data_store(n_clicks, data, new_data_store):
    '''
        Updates data store when save button is clicked
    '''
    print(data['props'])


# Modal Callbacks

@callback(
    Output('missing-values-modal', 'is_open'),
    [Input('fill-values', 'n_clicks'), Input("submit", "n_clicks")],
    State('missing-values-modal', 'is_open'),
)
def toggle_missing_values_modal(n1, n2, is_open):
    '''
        Used to toggle the fill missing values modal dialog on button click.
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