import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

from app import app

pd.options.plotting.backend = "plotly"

df = pd.read_csv('generated_dataset_article.csv', dayfirst=True, parse_dates=['timeFrom','timeTo'])
df['isRain'] = df['isRain'].astype('bool')
df['isHoliday'] = df['isHoliday'].astype('bool')
df['isWeekday'] = df['isWeekday'].astype('bool')
#df['Legend'] = 1*df['isWeekday'] + 2*df['isRain'] + 4*df['isHoliday']

#df['timeTo'] = pd.DatetimeIndex(df['timeTo']).time
#fig1.update_layout(yaxis=dict(tickformat='%H:%M'))
#fig1 = px.scatter(df, x="timeFrom", y="timeTo", height=700, hover_data=['isRain','isHoliday','isWeekday'], color='isRain')
#fig1.update_layout(
#    title="All Parkings by Entrance & Exit Date/Times",
#    xaxis_title="Entrance",
#    yaxis_title="Exit",
#    legend_title="Rain",
#    font=dict(
#        size=14,
#    )
#)


layout = dbc.Row([
    dbc.Col([
        dbc.Label('Choose Legend Filter'),
        dcc.Dropdown(
            id='legend-filter',
            options=[
                {'label': 'Rain Days', 'value': 'isRain'},
                {'label': 'Holidays', 'value': 'isHoliday'},
                {'label': 'WeekDays', 'value': 'isWeekday'},
            ],
            value='isRain',
            clearable=False,
            placeholder='Select Filter...'
        ),
        html.Br(),
        dcc.Graph(id='mainchart')
    ]),
],id='graph-grid')

@app.callback(
    Output('mainchart','figure'),
    Input('legend-filter','value')
)

def update_data(legenddropval):
    mainchart = px.scatter(df, x="timeFrom", y="timeTo", height=700, hover_data=['isRain', 'isHoliday', 'isWeekday'], color=legenddropval)
    mainchart.update_layout(
        title="All Parkings by Entrance & Exit Date/Times",
        xaxis_title="Entrance",
        yaxis_title="Exit",
        legend_title=legenddropval,
        font=dict(
            size=14,
        )
    )
    return (mainchart)