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

# Time Series Plots


def draw_timeseries(df, comp_y, time_col, person_id, comp_x='', person_to_plot=[], random_choice=5, use_raw=True):
    # df: dataframe to modify
    # comp_y: numerical columns to plot
    # person_id: name of the person_id column
    # comp_x: column that becomes the gold standard (if user specifies)
    # person_to_plot: list of participants to plot, max will be len == 5
    # random_choice: number of random participants user would like to visualize
    # use_raw: user should select whether to plot raw or interpolated data

    if len(person_to_plot) == 0:
        person_to_plot = np.random.choice(
            df[person_id].unique(), random_choice, replace=False)

    temp = df[df[person_id].isin(person_to_plot)].copy()

    for c in person_to_plot:
        temp = df[df[person_id] == c].copy()
        fig = px.line(temp, x=time_col, y=comp_y)

    return fig


@callback(
    Output('timeseries', 'figure'),
    Input('data-store', 'data')
)
def update_timeseries(user_uploaded_data):
    df = pd.read_json(user_uploaded_data)

    fig = draw_timeseries(df, ['Apple Watch', 'Fitbit', 'Miband'],
                          'Elapsed Time', person_id='ID', random_choice=3)

    return fig

# Correlation Plots


def draw_correlation_plot(df, x, y):
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
