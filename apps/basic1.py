import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from datetime import date, datetime

from app import app

pd.options.plotting.backend = "plotly"

df = pd.read_csv('generated_dataset_article.csv', dayfirst=True, parse_dates=['timeFrom','timeTo'])
df['isRain'] = df['isRain'].astype('bool')
df['isHoliday'] = df['isHoliday'].astype('bool')
df['isWeekday'] = df['isWeekday'].astype('bool')

min_date = df['timeFrom'].min()
max_date = df['timeFrom'].max()
start_min_date = min_date
if len(df['timeFrom']) > 5000:
    start_min_date = df.iloc[len(df)-5000]['timeFrom']

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


layout = html.Div([
    dbc.Row([
        dbc.Col([
            html.Div([
                dbc.Label('Date Range:'),
                html.Br(),
                dcc.DatePickerRange(
                    id='b1_date_range',
                    min_date_allowed=min_date,
                    max_date_allowed=max_date,
                    initial_visible_month=max_date,
                    start_date=start_min_date,
                    end_date=max_date,
                ),
            ]),
        ], width="auto"),
        dbc.Col([
            dbc.Label('Choose Legend Filter'),
            dcc.Dropdown(
                id='b1_legend',
                options=[
                    {'label': 'Rain Days', 'value': 'isRain'},
                    {'label': 'Holidays', 'value': 'isHoliday'},
                    {'label': 'WeekDays', 'value': 'isWeekday'},
                ],
                value='isRain',
                clearable=False,
                placeholder='Select Filter...'
            ),
        ]),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dcc.Loading(id="loading-icon", children=[html.Div(dcc.Graph(id='b1_mainchart'))], type="default")
        ], width=9),
        dbc.Col([
            html.Div([], id='b1_table_statistics'),
        ])
    ]),
], id='graph-grid')


@app.callback(
    [Output('b1_mainchart','figure'),
     Output('b1_table_statistics', 'children')],
    [Input('b1_legend','value'),
     Input('b1_date_range','start_date'),
     Input('b1_date_range','end_date')]
)
def update_data(legenddropval, start_date, end_date):
    df2 = df.copy()

    # Apply Date Range
    date_mask = (df2['timeFrom'] >= start_date) & (df2['timeFrom'] <= end_date)
    df2 = df2.loc[date_mask]

    # Apply Legend
    b1_mainchart = px.scatter(df2, x="timeFrom", y="timeTo", height=700, custom_data=['isRain','isHoliday','isWeekday'], color=legenddropval)
    b1_mainchart.update_layout(
        title="All Parkings by Entrance & Exit Date/Times",
        xaxis_title="Entrance",
        yaxis_title="Exit",
        legend_title=legenddropval,
    )
    b1_mainchart.update_traces(
        hoverinfo='skip',
        hovertemplate='Entrance: <b>%{x}</b><br>'
                      + 'Exit: <b>%{y}</b><br><br>'
                      + 'isRain: <b>%{customdata[0]}</b><br>'
                      + 'isHoliday: <b>%{customdata[1]}</b><br>'
                      + 'isWeekday: <b>%{customdata[2]}</b>'
                      + '<extra></extra>')

    # Total Records
    total_records = len(df2)

    # Daily Mean Records
    delta = pd.to_datetime(end_date).date() - pd.to_datetime(start_date).date()
    b1_daily_mean = html.Div('Daily Mean Records: ' + str(round((total_records / delta.days), 2)) + ' parkings/day')

    # Rainy & Sunny Records

    statistics = pd.DataFrame(
        {
            "Statistic": ['Total Records: ','Daily Average Records: ', 'Sunny Weather Records: ','Rainy Weather Records: '],
            "Value": [str(total_records), str(round((total_records / delta.days), 2)) + ' parkings/day', str(len(df2[df2['isRain'] == 0])), str(len(df2[df2['isRain'] == 1]))]
        }
    )

    b1_table_statistics = dbc.Table.from_dataframe(statistics, bordered=True, dark=True, hover=True, responsive=True, striped=True)

    return (b1_mainchart, b1_table_statistics)