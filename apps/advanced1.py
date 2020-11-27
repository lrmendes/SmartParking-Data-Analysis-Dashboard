import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from datetime import date, datetime
import plotly.graph_objects as go

from app import app

pd.options.plotting.backend = "plotly"

df = pd.read_csv('generated_dataset_article_grouped_hour.csv', dayfirst=True, parse_dates=['timeFrom'], index_col='timeFrom')
df['hour'] = df.index.hour
#df['day_of_month'] = df.index.day
#df['day_of_week'] = df.index.dayofweek
#df['month'] = df.index.month

df['isRain'] = df['isRain'].astype('bool')
df['isHoliday'] = df['isHoliday'].astype('bool')
df['isWeekday'] = df['isWeekday'].astype('bool')

min_date = df.index.min()
max_date = df.index.max()
start_min_date = min_date

#if len(df['timeFrom']) > 5000:
#    start_min_date = df.iloc[len(df)-5000]['timeFrom']


layout = html.Div([
    dbc.Row([
        dbc.Col([
            html.Div([
                dbc.Label('Date Range:'),
                html.Br(),
                dcc.DatePickerRange(
                    id='adv1_date_range',
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
                id='adv1_legend',
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
            dbc.Row([
                dbc.Col([
                    dcc.Loading(id="loading-icon", children=[html.Div(dcc.Graph(id='adv1_mainchart'))], type="default")
                ])
            ]),
            dbc.Row([
                dbc.Col([
                    dcc.Loading(id="loading-icon", children=[html.Div(dcc.Graph(id='adv2_mainchart'))], type="default")
                ])
            ], className='line-graphs'),
            dbc.Row([
                dbc.Col([
                    dcc.Loading(id="loading-icon", children=[html.Div(dcc.Graph(id='adv3_mainchart'))], type="default")
                ])
            ], className='line-graphs'),
            dbc.Row([
                dbc.Col([
                    dcc.Loading(id="loading-icon", children=[html.Div(dcc.Graph(id='adv4_mainchart'))], type="default")
                ])
            ], className='line-graphs')
        ], width=9),
        dbc.Col([
            html.Div([], id='adv1_table_statistics'),
        ])
    ]),
], id='graph-grid')


@app.callback(
    [Output('adv1_mainchart','figure'),
     Output('adv2_mainchart','figure'),
     Output('adv3_mainchart','figure'),
     Output('adv4_mainchart','figure'),
     Output('adv1_table_statistics', 'children')],
    [Input('adv1_legend','value'),
     Input('adv1_date_range','start_date'),
     Input('adv1_date_range','end_date')]
)
def update_data(legenddropval, start_date, end_date):
    df2 = df.copy()

    start_date_converted = pd.to_datetime(start_date).date()
    end_date_converted = pd.to_datetime(end_date).date()

    # Apply Date Range
    date_mask = (df2.index.date >= start_date_converted) & (df2.index.date <= end_date_converted)
    df2 = df2.loc[date_mask]

    # GroupBy Hour
    df3 = df2.copy()
    #df2 = df2.drop(df2.columns.difference(), axis=1)
    df3 = df3.groupby(by=['hour']).mean()
    # Apply Legend
    adv1_mainchart = px.line(df3, x=df3.index, y="TotalParkings", height=250)
    adv1_mainchart.update_layout(
        title="Total Parkings grouped by Hour of Day",
        xaxis_title="Hour",
        yaxis_title="Total Parkings",
        legend_title=legenddropval,
    )
    adv1_mainchart.update_traces(
        mode='lines+markers',
    )

    # Only Rain
    df4 = df2.copy()
    df_rain0 = df4[df4['isRain'] == 0].groupby(by=['hour']).mean()
    df_rain1 = df4[df4['isRain'] == 1].groupby(by=['hour']).mean()

    adv2_mainchart = go.Figure()
    adv2_mainchart.add_trace(go.Scatter(x=df_rain0.index, y=df_rain0["TotalParkings"], mode='lines+markers',
                                        name='False'))
    adv2_mainchart.add_trace(go.Scatter(x=df_rain1.index, y=df_rain1["TotalParkings"], mode='lines+markers',
                                        name='True'))
    adv2_mainchart.update_layout(
        title="Total Parkings grouped by Hour of Day (Rain)",
        xaxis_title="Hour",
        yaxis_title="Total Parkings",
        legend_title='isRain',
    )
    adv2_mainchart.layout.update(
        height=250,
        hovermode='x unified',
        margin=dict(l=20, r=20, t=40, b=5),
    )

    # Only Holiday
    df5 = df2.copy()
    df_holy0 = df5[df5['isHoliday'] == 0].groupby(by=['hour']).mean()
    df_holy1 = df5[df5['isHoliday'] == 1].groupby(by=['hour']).mean()
    adv3_mainchart = go.Figure()
    adv3_mainchart.add_trace(go.Scatter(x=df_holy0.index, y=df_holy0["TotalParkings"], mode='lines+markers',
                                        name='False'))
    adv3_mainchart.add_trace(go.Scatter(x=df_holy1.index, y=df_holy1["TotalParkings"], mode='lines+markers',
                                        name='True'))
    adv3_mainchart.update_layout(
        title="Total Parkings grouped by Hour of Day (Holiday)",
        xaxis_title="Hour",
        yaxis_title="Total Parkings",
        legend_title="isHoliday",
    )
    adv3_mainchart.layout.update(
        height=250,
        hovermode='x unified',
        margin=dict(l=20, r=20, t=40, b=5),
    )

    # Only WeekDays
    df5 = df2.copy()
    df_week0 = df5[df5['isWeekday'] == 0].groupby(by=['hour']).mean()
    df_week1 = df5[df5['isWeekday'] == 1].groupby(by=['hour']).mean()
    adv4_mainchart = go.Figure()
    adv4_mainchart.add_trace(go.Scatter(x=df_week0.index, y=df_week0["TotalParkings"], mode='lines+markers',
                                        name='False'))
    adv4_mainchart.add_trace(go.Scatter(x=df_week1.index, y=df_week1["TotalParkings"], mode='lines+markers',
                                        name='True'))
    adv4_mainchart.update_layout(
        title="Total Parkings grouped by Hour of Day (Week Days)",
        xaxis_title="Hour",
        yaxis_title="Total Parkings",
        legend_title="isWeekday",
    )
    adv4_mainchart.layout.update(
        height=250,
        hovermode='x unified',
        margin=dict(l=20, r=20, t=40, b=5),
    )

    # Total Records
    total_records = len(df2)

    # Daily Mean Records
    #delta = pd.to_datetime(end_date).date() - pd.to_datetime(start_date).date()
    #adv1_daily_mean = html.Div('Daily Mean Records: ' + str(round((total_records / delta.days), 2)) + ' parkings/day')

    # Statistics
    statistics = pd.DataFrame(
        {
            "Statistic": [
                'Total Records (H)',
                'Total Records (D)',
                '',
                'Rainy Weather Records',
                'Sunny Weather Records',
                '',
                'Holiday Records',
                'Non-Holiday Records',
                'Total Holidays',
                'Total Non-Holidays'
            ],
            "Value": [
                str(total_records) + ' hours',
                str(round(total_records / len(df3), 0)) + ' days',
                '',
                str(len(df2[df2['isRain'] == 0])) + ' hours',
                str(len(df2[df2['isRain'] == 1])) + ' hours',
                '',
                str(len(df2[df2['isHoliday'] == 1])) + ' hours',
                str(len(df2[df2['isHoliday'] == 0])) + ' hours',
                str(round(len(df2[df2['isHoliday'] == 1]) / len(df3), -1)) + ' day(s)',
                str(round(len(df2[df2['isHoliday'] == 0]) / len(df3), 0)) + ' day(s)',
            ]
        }
    )

    # Identificar principais horarios de fluxo do estacionamento
    # Identificar como o estacionamento é afetado pelo clima ( mais ou menos em chuva )
    # Identificar como o estacionamento é afetado por finais de semana ( mais ou menos em fds )
    # Identificar como o estacionamento é afetado por feriados ( mais ou menos em feriados )

    adv1_table_statistics = dbc.Table.from_dataframe(statistics, bordered=True, dark=True, hover=True, responsive=True, striped=True)

    return (adv1_mainchart, adv2_mainchart, adv3_mainchart, adv4_mainchart, adv1_table_statistics)