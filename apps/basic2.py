import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

from app import app

pd.options.plotting.backend = "plotly"

target_cols = ['timeFrom', 'isRain', 'isHoliday', 'isWeekday']
df = pd.read_csv('generated_dataset_article.csv', dayfirst=True, parse_dates=['timeFrom'], index_col='timeFrom',
                 usecols=target_cols)
df['isRain'] = df['isRain'].astype('bool')
df['isHoliday'] = df['isHoliday'].astype('bool')
df['isWeekday'] = df['isWeekday'].astype('bool')

layout = dbc.Row([
    dbc.Col([
        dbc.Label('Group Parkings By:'),
        dcc.Dropdown(
            id='b2_legend_filter',
            options=[
                {'label': 'Hours', 'value': 'hour'},
                {'label': 'Days', 'value': 'day'},
                {'label': 'Months', 'value': 'month'},
            ],
            value='day',
            clearable=False,
            placeholder='Select Filter...'
        ),
        html.Br(),
        dcc.Graph(id='b2_mainchart')
    ]),
], id='graph-grid')


@app.callback(
    Output('b2_mainchart', 'figure'),
    Input('b2_legend_filter', 'value')
)
def update_data(legenddropval):
    df2 = df.copy()

    if (legenddropval == 'hour'):
        df2['TotalParkings'] = 1
        pd.to_datetime(df2.index, errors='ignore')
        df2 = df2.resample('H').sum()
        df2 = df2[df2['TotalParkings'] > 0]

    if (legenddropval == 'day'):
        df2['TotalParkings'] = 1
        pd.to_datetime(df2.index, errors='ignore')
        df2 = df2.resample('D').sum()

    if (legenddropval == 'month'):
        df2['TotalParkings'] = 1
        pd.to_datetime(df2.index, errors='ignore')
        df2 = df2.resample('M').sum()

    df2['isWeekday'] = df2.apply((lambda x: 1 if x['isWeekday'] > 0 else 0), axis=1)
    df2['isWeekday'] = df2['isWeekday'].astype('bool')

    df2['isHoliday'] = df2.apply((lambda x: 1 if x['isHoliday'] > 0 else 0), axis=1)
    df2['isHoliday'] = df2['isHoliday'].astype('bool')

    mainchart = px.line(df2, x=df2.index, y='TotalParkings', custom_data=['isWeekday',
                                                                          'isHoliday'])  # hover_name=df2.index, hover_data=['isWeekday','isHoliday'])
    mainchart.update_layout(
        title="All Parkings Grouped By " + legenddropval,
        xaxis_title="Date",
        yaxis_title="Total Parkings",
        font=dict(
            size=14,
        )
    )
    mainchart.update_traces(
        mode='lines+markers',
        hovertemplate='<b>%{x}</b><br><br>'
                      + '<b>Total Parkings: %{y}</b><br><br>'
                      + 'isWeekday: <b>%{customdata[0]}</b><br>'
                      + 'isHoliday: <b>%{customdata[1]}</b>')

    return (mainchart)
