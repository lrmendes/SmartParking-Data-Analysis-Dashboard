import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd

from app import app

graph2 = dcc.Graph(
    figure = {
        'data': [
            {
                'x':[1,4,5,6,8],
                'y':[2,5,4,9,12],
                'type': 'line',
                'name': 'IPB Cars'
            },
            {
                'x':[1,2,4,6,8],
                'y':[4,2,8,12,14],
                'type': 'line',
                'name': 'IPB Bikes'
            }
        ],
        'layout': {
            'title': "Simple Line Chart",
            'font': {
                'color': '#000000'
            },
            'dragmode': 'pan'
        }
    }
)

layout = dbc.Row([
    dbc.Col([
        html.H3('App 1'),
        dcc.Dropdown(
            id='app-1-dropdown',
            options=[
                {'label': 'App 1 - {}'.format(i), 'value': i} for i in [
                    'NYC', 'MTL', 'LA'
                ]
            ]
        ),
        html.Div(id='app-1-display-value'),
        dcc.Link('Go to App 2', href='/apps/app2'),
        graph2
    ]),
    dbc.Col([
        html.H3('App 2'),
        dcc.Dropdown(
            id='app-1-dropdown',
            options=[
                {'label': 'App 1 - {}'.format(i), 'value': i} for i in [
                    'NYC', 'MTL', 'LA'
                ]
            ]
        ),
        html.Div(id='app-1-display-value'),
        dcc.Link('Go to App 2', href='/apps/app2'),
        graph2
    ]),
    dbc.Col([
        graph2
    ]),
])