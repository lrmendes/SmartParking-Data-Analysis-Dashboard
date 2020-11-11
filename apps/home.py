import dash_bootstrap_components as dbc
import dash
from dash.dependencies import Input, Output
import dash_table
import dash_html_components as html
from datetime import datetime
import pandas as pd
import dash_core_components as dcc
import plotly.express as px

from dash_extensions import Download
from dash_extensions.snippets import send_data_frame

from app import app

px.set_mapbox_access_token(open(".mapbox_token").read())

parkings = pd.read_csv('parkings.csv', parse_dates=['open', 'close'])
parkings['open'] = pd.to_datetime(parkings['open'], format='%H:%M').dt.time
parkings['close'] = pd.to_datetime(parkings['close'], format='%H:%M').dt.time

parkings['size'] = 20

target_cols = ['timeFrom', 'region', 'isRain', 'isHoliday', 'isWeekday']
df = pd.read_csv('generated_dataset_article.csv', dayfirst=True, parse_dates=['timeFrom'], index_col='timeFrom',
                 usecols=target_cols)
df['isRain'] = df['isRain'].astype('bool')
df['isHoliday'] = df['isHoliday'].astype('bool')
df['isWeekday'] = df['isWeekday'].astype('bool')

min_date = df.index.min()
max_date = df.index.max()

fig = px.scatter_mapbox(parkings, lat="lat", lon="lon", custom_data=['name', 'parkings', 'open', 'close'], size="size",
                        color="name", zoom=14, height=600)
fig.update_layout(mapbox_style="open-street-map")
# fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.update_traces(
    hovertemplate='<b>%{customdata[0]}</b><br><br>'
                  + 'Open: <b>%{customdata[2]}</b><br>'
                  + 'Close: <b>%{customdata[3]}</b><br>'
                  + 'Total Parkings: <b>%{customdata[1]}</b><br>'
                  + '<extra></extra>')

# fig = px.scatter_mapbox(parkings, lat="lat", lon="lon", color="name", color_continuous_scale=px.colors.cyclical.IceFire, size="size", zoom=10)
# fig.show()


layout = html.Div([
    html.Div([
        html.H4('Current Status'),
        dbc.Row([
            dbc.Col([
                html.Div([
                    dbc.Label('Group Parkings By:'),
                    dcc.Dropdown(
                        id='home_region_filter',
                        options=[
                            {'label': i, 'value': i} for i in df.region.unique()
                        ],
                        value=df.region.unique()[0],
                        clearable=False,
                        placeholder='Select Filter...'
                    ),
                ]),
            ], id='graph-grid', width="auto"),
            dbc.Col([
                html.Div([
                    dbc.Label('Date:'),
                    html.Br(),
                    dcc.DatePickerSingle(
                        id='home_date_single',
                        min_date_allowed=min_date,
                        max_date_allowed=max_date,
                        initial_visible_month=max_date,
                        date=max_date,
                    ),
                    html.Div(id='home_output')
                ]),
            ], id='graph-grid', width="auto"),
        ]),
        dbc.Row([
        dbc.Col([

        ], id='graph-grid'),
        dbc.Col([

        ], id='graph-grid')
    ]),
    ]),
    html.Br(),
    html.Hr(),
    html.Br(),
    html.Div([
        html.H4('World View'),
        dbc.Row([
            dbc.Col([
                html.Div([
                    dbc.Label('Group Parkings By:'),
                    dcc.Dropdown(
                        id='home_openclose_filter',
                        options=[
                            {'label': 'All Parking Lots', 'value': 'all'},
                            {'label': 'Open Parking Lots', 'value': 'open'},
                            {'label': 'Closed Parking Lots', 'value': 'close'},
                        ],
                        value='all',
                        clearable=False,
                        placeholder='Select Filter...'
                    ),
                ]),
            ]),
            dbc.Col([
                html.Div([
                    dbc.Label('Identify Parking Lots By:'),
                    dcc.Dropdown(
                        id='home_identify_filter',
                        options=[
                            {'label': 'Name', 'value': 'name'},
                            {'label': 'Status (Open/Closed)', 'value': 'status'},
                        ],
                        value='name',
                        clearable=False,
                        placeholder='Select Filter...'
                    ),
                ]),
            ]),
        ], id='graph-grid'),
        dbc.Row([
            dbc.Col([
                html.Br(),
                dcc.Loading(id="loading-icon", children=[html.Div(dcc.Graph(id='home_mapchart'))], type="default")
            ])
        ], id='graph-grid')
    ]),
    html.Br()
])

@app.callback(
    Output('home_mapchart', 'figure'),
    [Input('home_region_filter', 'value'),
     Input('home_date_single', 'date'),
     Input('home_openclose_filter', 'value'),
     Input('home_identify_filter', 'value')]
)
def update_output(date_single, region_filter, openclose_filter, identify_filter):
    df2 = parkings.copy()
    df2['status'] = df2.apply(
        (lambda x: 'closed' if (datetime.now().time() < x['open']) | (datetime.now().time() > x['close']) else 'open'),
        axis=1)

    if (openclose_filter == 'open'):
        # Apply Date Range
        date_mask = (df2['open'] <= datetime.now().time()) & (df2['close'] >= datetime.now().time())
        df2 = df2.loc[date_mask]
    elif (openclose_filter == 'close'):
        date_mask = ((datetime.now().time() < df2['open']) | (datetime.now().time() > df2['close']))
        df2 = df2.loc[date_mask]

    mapchart = px.scatter_mapbox(df2, lat="lat", lon="lon", custom_data=['name', 'parkings', 'open', 'close', 'status'],
                                 size="size", color=identify_filter, zoom=14, height=600)
    mapchart.update_layout(mapbox_style="open-street-map")
    mapchart.update_layout(margin={"r":5,"t":35,"l":5,"b":5})
    mapchart.update_traces(
        hovertemplate='<b>%{customdata[0]}</b><br><br>'
                      + 'Open: <b>%{customdata[2]}</b><br>'
                      + 'Close: <b>%{customdata[3]}</b><br>'
                      + 'Total Parkings: <b>%{customdata[1]}</b><br><br>'
                      + 'Status: <b>%{customdata[4]}</b><br>'
                      + '<extra></extra>')

    return (mapchart)
