import dash_bootstrap_components as dbc
import dash
from dash.dependencies import Input, Output
import dash_table
import dash_html_components as html
from datetime import datetime
import pandas as pd
import dash_core_components as dcc
import plotly.express as px

import plotly.graph_objects as go

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

layout = html.Div([
    html.Div([
        html.H4('Current Status'),
        dbc.Row([
            dbc.Col([
                html.Div([
                    dbc.Label('Select Region:'),
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
            ], className='graph-grid', width="auto"),
            dbc.Col([
                html.Div([
                    dbc.Label('Select Date:'),
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
            ], className='graph-grid', width="auto"),
        ]),
        dbc.Row([
            dbc.Col([
                dcc.Loading(id="loading-icon", children=[html.Div(dcc.Graph(id='home_chart1'))], type="default")
            ], className='graph-grid', width=9),
            dbc.Col([
                dcc.Loading(id="loading-icon", children=[html.Div([], id='home_table_statistics')], type="default")
            ], className='graph-grid', width='auto')
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
            dbc.Col([
                html.Div([
                    dbc.Label('Graph Type:'),
                    dcc.Dropdown(
                        id='home_graphtype',
                        options=[
                            {'label': 'Default', 'value': 'default'},
                            {'label': 'HeatMap', 'value': 'heatmap'},
                        ],
                        value='default',
                        clearable=False,
                        placeholder='Select Filter...'
                    ),
                ]),
            ]),
        ], className='graph-grid'),
        dbc.Row([
            dbc.Col([
                html.Br(),
                dcc.Loading(id="loading-icon", children=[html.Div(dcc.Graph(id='home_mapchart'))], type="default")
            ])
        ], className='graph-grid')
    ]),
    html.Br()
])

@app.callback(
    [Output('home_chart1', 'figure'),
     Output('home_table_statistics', 'children')],
    [Input('home_region_filter', 'value'),
     Input('home_date_single', 'date')]
)
def update_chart1(region_filter,date_filter):
    df2 = df.copy()
    date_f = pd.to_datetime(date_filter)
    date_mask = (df2.index.date == date_f)
    df2 = df2.loc[date_mask]

    # Group By Hours (sum TotalParkings)
    df2['TotalParkings'] = 1
    pd.to_datetime(df2.index, errors='ignore')
    df2 = df2.resample('H').sum()

    # Make isRain boolean again
    df2['isRain'] = df2.apply((lambda x: 1 if x['isRain'] > 0 else 0), axis=1)
    df2['isRain'] = df2['isRain'].astype('bool')

    # Bar Chart
    home_chart1 = px.bar(df2, x=df2.index, y='TotalParkings', color='isRain')
    home_chart1.update_layout(
        title="["+date_f.strftime("%d/%m/%Y")+"] " + region_filter + " - Parking Lots by Hour"
    )

    statistics = pd.DataFrame(
        {
            "Statistic": ['Total Hours Registered', 'Parking Lots Average (by Hour)'],
            "Value": [str(len(df2)), str(round(df2['TotalParkings'].mean(), 2))]
        }
    )
    home_table_statistics = dbc.Table.from_dataframe(statistics, bordered=True, dark=True, hover=True, responsive=True, striped=True)

    return home_chart1,home_table_statistics


@app.callback(
    Output('home_mapchart', 'figure'),
    [Input('home_openclose_filter', 'value'),
     Input('home_identify_filter', 'value'),
     Input('home_graphtype', 'value')]
)
def update_output(openclose_filter, identify_filter, graphtype):
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

    if graphtype == 'default':
        mapchart = px.scatter_mapbox(df2, lat="lat", lon="lon", custom_data=['name', 'parkings', 'open', 'close', 'status'],
                                     size="size", color=identify_filter, zoom=14, height=600, color_discrete_sequence=px.colors.qualitative.Dark24)
        mapchart.update_layout(mapbox_style="open-street-map")
        mapchart.update_layout(margin={"r":5,"t":35,"l":5,"b":5})
        mapchart.update_traces(
            hovertemplate='<b>%{customdata[0]}</b><br><br>'
                          + 'Open: <b>%{customdata[2]}</b><br>'
                          + 'Close: <b>%{customdata[3]}</b><br>'
                          + 'Total Parkings: <b>%{customdata[1]}</b><br><br>'
                          + 'Status: <b>%{customdata[4]}</b><br>'
                          + '<extra></extra>')
    else:
        df2['occupation'] = [80,20,50]
        mapchart = go.Figure(go.Densitymapbox(lat=df2.lat, lon=df2.lon, z=df2.occupation, colorbar=dict(
                title="Parking Occupation",
                tickvals=[0, 25, 50, 75, 100],
                ticktext=["100%", "75%", "50%", "25%", "0%"],
                ),
                customdata=[df2.name,df2.parkings],
                hovertemplate='<b>( %{lat} , %{lon} )</b><br><br>'
                            + 'Occupation: <b>%{z}%</b><br>'
                            + '<extra></extra>'
            ))
        mapchart.update_layout(
            mapbox_style="open-street-map",
        )
        mapchart.update_traces(
            zmin=0, zmax=100, zauto=False,
        )
    return (mapchart)
