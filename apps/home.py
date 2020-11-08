import dash_bootstrap_components as dbc
from app import app
import dash
from dash.dependencies import Input, Output
import dash_table
import dash_html_components as html
import datetime
import pandas as pd

df = pd.read_csv('generated_dataset_article.csv', parse_dates=['timeFrom','timeTo'])
layout = html.Div([
    dbc.Row([
        dbc.Col([
        html.Div([
        html.H4("Database as DataFrame", style={'align': 'center'}),
        dash_table.DataTable(
            columns=[
                {'name': 'parking', 'id': 'parking', 'type': 'text'},
                {'name': 'region', 'id': 'region', 'type': 'text'},
                {'name': 'timeFrom', 'id': 'timeFrom', 'type': 'datetime'},
                {'name': 'timeTo', 'id': 'timeTo', 'type': 'datetime'},
                {'name': 'spotWanted', 'id': 'spotWanted', 'type': 'numeric'},
                {'name': 'spotWon', 'id': 'spotWon', 'type': 'numeric'},
                {'name': 'isWeekday', 'id': 'isWeekday', 'type': 'numeric'},
                {'name': 'isRain', 'id': 'isRain', 'type': 'numeric'},
                {'name': 'isHoliday', 'id': 'isHoliday', 'type': 'numeric'},
            ],
            data=df.to_dict('records'),
            filter_action='native',
            sort_action="native",
            sort_mode='multi',
            fixed_rows={'headers': True},
            style_table={'height': '600px', 'overflowY': 'auto',},
            style_data={
                'width': '150px', 'minWidth': '150px', 'maxWidth': '150px','overflow': 'hidden',
                'textOverflow': 'ellipsis',
            })
        ])
    ],
    id='graph-grid'),
    ])
])
