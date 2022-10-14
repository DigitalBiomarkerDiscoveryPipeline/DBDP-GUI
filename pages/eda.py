import dash
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from dash import dcc, html, callback, Output, Input, dash_table
import plotly.express as px
import pandas as pd
import numpy as np

dash.register_page(
    __name__, name='Exploratory Data Analysis', path='/eda', order=2)

layout = html.Div(
    [
        dbc.Accordion(
            [
                dbc.AccordionItem(
                    [
                        dbc.Row([
                            dbc.Col([
                                dcc.Dropdown(
                                    id='person-id-options',
                                ),
                            ]),
                            dbc.Col([
                                dcc.Dropdown(
                                    ['Apple Watch', 'Empatica',
                                     'Garmin', 'Fitbit', 'Miband', 'Biovotion'],
                                    ['Apple Watch', 'Fitbit'],
                                    multi=True,
                                    id='wearable-options',
                                ),
                            ]),
                        ]),

                        dcc.Graph(id='timeseries'),
                    ],
                    title="Explore Time Series"
                ),
                dbc.AccordionItem(
                    [
                        dbc.Row(
                            [
                                dbc.Col([
                                    dcc.Dropdown(
                                        id='y-options',
                                        placeholder='Select Y-Axis Variable'
                                    ),
                                ]),
                                dbc.Col([
                                    dcc.Dropdown(
                                        id='x-options',
                                        placeholder='Select X-Axis Variable'
                                    ),
                                ]),
                            ]
                        ),
                        dcc.Graph(id='correlation'),
                        dcc.Graph(id='heatmap')
                    ],
                    title="Explore Correlation"
                )
            ]
        )
    ]
)

# Dropdown Options


@callback(
    Output('y-options', 'options'),
    Output('x-options', 'options'),
    Input('data-store', 'data')
)
def update_options(user_uploaded_data):
    df = pd.read_json(user_uploaded_data)

    options = df.columns[1:8]

    return options, options


@callback(
    Output('person-id-options', 'options'),
    Output('person-id-options', 'value'),
    Input('data-store', 'data')
)
def update_options(user_uploaded_data):
    df = pd.read_json(user_uploaded_data)

    options = df['ID'].unique()
    int_value = np.random.choice(options)

    return options, int_value

# Time Series Plots


def draw_timeseries(df, time_col, standard, comp_y, person_to_plot):

    temp = df[df['ID'] == person_to_plot].copy()
    comp_y = ['filled ' + y for y in comp_y]
    temp = temp.sort_values(by=[time_col])

    # ECG data plots
    fig = px.line(temp, x=time_col, y=standard)
    fig.data[0].line.color = 'grey'
    fig.update_traces(opacity=0.3)

    # Add additional plots for selected wearbales
    colors = px.colors.qualitative.Plotly[:len(comp_y)]
    for i, y in enumerate(comp_y):
        add_fig = px.line(temp, x=time_col, y=y)
        add_fig.data[0].line.color = colors[i]
        fig.add_trace(add_fig.data[0])

    return fig


@callback(
    Output('timeseries', 'figure'),
    Input('data-store', 'data'),
    Input('person-id-options', 'value'),
    Input('wearable-options', 'value')
)
def update_timeseries(user_uploaded_data, person_id, wearables):
    df = pd.read_json(user_uploaded_data)

    fig = draw_timeseries(df, 'Elapsed Time', 'ECG', wearables, person_id)

    return fig

# Correlation Plots


def draw_correlation_plot(df, x, y):
    x = 'filled ' + x
    y = 'filled ' + y
    temp = df[[x, y]]

    fig = px.scatter(temp, x=x, y=y, trendline='ols')

    return fig


@callback(
    Output('correlation', 'figure'),
    Input('data-store', 'data'),
    Input('y-options', 'value'),
    Input('x-options', 'value')
)
def update_correlation(user_uploaded_data, y_axis, x_axis):
    if (x_axis is None) or (y_axis is None) or (x_axis == y_axis):
        raise PreventUpdate

    df = pd.read_json(user_uploaded_data)

    corr_plot = draw_correlation_plot(df, x_axis, y_axis)
    corr_plot.update_layout(title_text=f'{y_axis} vs. {x_axis}')

    return corr_plot


@callback(
    Output('heatmap', 'figure'),
    Input('data-store', 'data')
)
def update_corr_table(user_uploaded_data):
    df = pd.read_json(user_uploaded_data)

    comp_x = df.columns[1:8]
    temp = df[comp_x]

    corr = temp.corr()
    fig = px.imshow(corr)

    return fig
