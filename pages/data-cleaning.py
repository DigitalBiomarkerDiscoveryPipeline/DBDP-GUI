import dash
import pandas as pd
from dash import html, dcc, callback, Input, Output, State, dash_table, ctx
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from sympy import false

dash.register_page(__name__, name='Data Cleaning',
                   path='/data-cleaning', order=1)

layout = html.Div([
    # Headers
    html.H1('Clean your dataset'),
    html.H5('Edit the table directly / use the GUI buttons below.'),

    # Data table
    dash_table.DataTable(
        id='data-table',
        page_size=10,
        editable=True,
        sort_action='native',
        sort_mode='single',
        row_deletable=True,
        column_selectable='multi',
        page_action='native',
        style_table={'overflowX': 'scroll'},
        export_format='csv',
        export_headers='display'),

    # User input for adding column
    html.Div([
        dcc.Input(
            id='add-column-value',
            placeholder='Enter a column name...',
            value='',
            style={'padding': 10}
        ),
        dbc.Button('Add Column', id='add-column-button')
    ], style={'height': 50, 'margin-bottom': 30}),


    # Table modification buttons
    html.Div([
        dbc.Button('Add Row', id='add-row-button'),
        dbc.Button('Fill Missing Values',
                   id='fill-values-button', n_clicks=0),
    ],
        className='d-grid gap-3 d-md-flex justify-content-md-start',
        style={'margin-bottom': 30}
    ),


    # Save updates
    html.Div([
        dbc.Button('Save your updates', id='save', color='success'),
    ]),


    # Success message when save has been successful
    html.Div([
        html.P(
            'Changes successfully saved',
            id='save-success-message',
            style={'display': 'none'}
        )
    ]),

    # Modal Dialog for filling missing values
    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Fill Missing Values")),

            dbc.ModalBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Person ID Column:"),
                        dcc.Dropdown(id="person-id-value",
                                     placeholder="The column that holds user ID."),
                    ]),
                    dbc.Col([
                        dbc.Label("Method"),
                        dcc.Dropdown(
                            id="method-value",
                            options=[
                                {"label": "Backfill", "value": 'backfill'},
                                {"label": "Forward Fill",
                                 "value": 'ffill'},
                                {"label": "Interpolate",
                                 "value": 'interpolate'},
                            ],
                            placeholder="The method of filling empty values.",
                        ),
                    ]),
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Columns to Modify:"),
                        dcc.Dropdown(id="columns-to-modify-value",
                                     multi=True,
                                     placeholder="Which columns to modify.")
                    ]),
                    dbc.Col([
                        dbc.Label("Max Number of NaN values:"),
                        dbc.Input(id="max-nan-values",
                                  type="number",
                                  min=1,
                                  placeholder="If left empty, will fill in all NaN values")
                    ]),
                ])
            ]),

            dbc.ModalFooter(
                dbc.Button(
                    "Submit", id="fill-values-submit-button", className="ms-auto", n_clicks=0, color='primary'
                )
            ),
        ],
        id="missing-values-modal",
        is_open=False,
        size="xl",
    ),
])

## Callbacks and Methods

# Table Callbacks


@callback(
    Output('data-table', 'data'),
    Output('data-table', 'columns'),
    Input('data-store', 'data'),
    Input('cleaned-data-store', 'data'),
    Input('add-row-button', 'n_clicks'),
    Input('add-column-button', 'n_clicks'),
    Input('fill-values-button', 'n_clicks'),
    Input('fill-values-submit-button', 'n_clicks'),
    State('add-column-value', 'value'),
    State('person-id-value', 'value'),
    State('method-value', 'value'),
    State('columns-to-modify-value', 'value'),
    State('max-nan-values', 'value'),
    State('data-table', 'data'),
    State('data-table', 'columns')
)
def display_data_table(data_store_data, cleaned_data_store_data, add_row_button_click, add_column_button_click,
                       fill_value_button_click, fill_value_submit_button_click, add_column_value,
                       person_id_value, method_value, columns_to_modify_value, max_nan_values,
                       table_rows, table_columns):
    '''
        Displays and modifies data table contents based on user input. 

        Documentation for duplicate callback outputs: https://dash.plotly.com/duplicate-callback-outputs
        Look at 'Updating the same output from different inputs' section.
    '''
    # Check what triggered the callback
    triggered_id = ctx.triggered_id

    if triggered_id == None:
        # Case when page has just loaded
        if cleaned_data_store_data != None:
            df = pd.read_json(cleaned_data_store_data)
        else:
            df = pd.read_json(data_store_data)
        data = df.to_dict('records')
        columns = [{'name': i, 'id': i, 'renamable': True,
                    'deletable': True} for i in df.columns]
        return data, columns
    elif triggered_id == 'add-row-button':
        # Case when add row button has been clicked
        table_rows.append({c['id']: '' for c in table_columns})
        return table_rows, table_columns
    elif triggered_id == 'add-column-button':
        # Case when add column button has been clicked
        table_columns.append({
            'id': add_column_value, 'name': add_column_value,
            'renamable': True, 'deletable': True
        })
        return table_rows, table_columns
    elif triggered_id == 'fill-values-submit-button':
        # Case when fill missing values form is being filled out
        df = pd.DataFrame.from_records(table_rows)
        df = column_categorization(df)
        new_df = fill_missing_values(
            df, person_id_value, how=method_value, columns=columns_to_modify_value, limit_n=max_nan_values)
        data = new_df.to_dict('records')
        columns = [{'name': i, 'id': i, 'renamable': True,
                    'deletable': True} for i in new_df.columns]
        return data, columns
    else:
        raise PreventUpdate

@callback(
    Output('cleaned-data-store', 'data'),
    Output('save-success-message', 'style'),
    Input('data-table', 'data'),
    Input('data-table', 'columns'),
    Input('save', 'n_clicks'),
)
def save_data_table_to_store(data, columns, save_button_click):
    '''
        On save changes button click, saves data to local data store
    '''
    if save_button_click != None and save_button_click > 0:
        # Get columns from columns dict in data-table
        column_list = []
        for c in columns:
            column_list.append(c['name'])
        
        # TODO: a ValueError should be raised here if column names are the same
        # ValueError: DataFrame columns must be unique for orient='columns'.

        # Convert data-table to json
        df = pd.DataFrame.from_records(data, columns=column_list)
        output_json = df.to_json()
        return output_json, {'display': 'block'}
    else:
        raise PreventUpdate

# Modal Callbacks

@callback(
    Output('missing-values-modal', 'is_open'),
    [Input('fill-values-button', 'n_clicks'),
     Input("fill-values-submit-button", "n_clicks")],
    State('missing-values-modal', 'is_open'),
)
def toggle_missing_values_modal(file_values_button, fill_values_submit_button, is_open):
    '''
        Used to toggle the fill missing values modal dialog on button click.
    '''
    if file_values_button or fill_values_submit_button:
        return not is_open
    return is_open


@callback(
    Output('person-id-value', 'options'),
    Output('columns-to-modify-value', 'options'),
    Input('fill-values-button', 'n_clicks'),
    Input('data-table', 'columns'),
    Input('person-id-value', 'options'),
)
def get_column_names(fill_missing_values_button_click, columns, person_id_value):
    '''
        Returns columns of dataframe for use in modal dropdown
    '''

    if fill_missing_values_button_click > 0:
        return_list = [{'label': c['id'], 'value': c['id']} for c in columns]
        return return_list, return_list
    else:
        raise PreventUpdate

# Helper functions


def fill_missing_values(df, person_id_col, how, columns, limit_n):
    '''
        Used to fill missing values in dataframe.

        df: dataframe to modify
        person_id_col: name of the person_id column
        how: users can choose from the following-- bfill, ffill, interpolate
        columns: columns to modify (fill missing values)
        limit_n: maximum number of consecutive NaN values to fill
    '''
    temp = df.copy()

    new_columns = ['filled ' + x for x in columns]

    if how == 'interpolate':
        temp[new_columns] = temp.groupby(person_id_col)[columns].apply(
            lambda x: x.interpolate(limit=limit_n))
    else:
        temp[new_columns] = temp.groupby(person_id_col)[
            columns].fillna(method=how, limit=limit_n)
    return temp


def column_categorization(df):
    '''
        If some columns like person_id or elapsed time are not specified, the code will insert the following:
        person_id -- will assume that the whole dataset is for one participant, put an arbituary id called 00-000
        elapsed time -- will assume that the rows are sorted in chronological order. index number will be used to represent the elapsed time
    '''
    person_id = 'ID'
    time = []

    if len(time) == 0:
        df['Elapsed Time'] = df.index
        df['Elapsed Time'] = df.groupby(
            by=person_id)['Elapsed Time'].apply(lambda x: x - x.iloc[0])

    if len(person_id) == 0:
        df['person_id'] = '00-000'

    return df
