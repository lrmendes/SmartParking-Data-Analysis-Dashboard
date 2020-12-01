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
df['isRain'] = df['isRain'].astype('bool')
df['isHoliday'] = df['isHoliday'].astype('bool')
df['isWeekday'] = df['isWeekday'].astype('bool')
df['regpark'] = df['parking'] + ' - ' + df['region']

min_date = df.index.min()
max_date = df.index.max()
start_min_date = min_date

layout = html.Div([
    html.H4('Filters:'),
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
        ], className='graph-grid', width="auto"),
        dbc.Col([
            html.Div([
                dbc.Label('Select Parking & Region:'),
                dcc.Dropdown(
                    id='adv1_region_filter',
                    options=[
                        {'label': i, 'value': i} for i in df.regpark.unique()
                    ],
                    value=df.regpark.unique()[0],
                    clearable=False,
                    placeholder='Select Filter...'
                ),
            ]),
        ], className='graph-grid', width="auto"),
    ]),
    html.Br(),
    html.H4('Data Visualization:'),
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
            html.Div([], id='adv1_stats_div'),
        ])
    ], className='graph-grid'),
])


@app.callback(
    [Output('adv1_mainchart', 'figure'),
     Output('adv2_mainchart', 'figure'),
     Output('adv3_mainchart', 'figure'),
     Output('adv4_mainchart', 'figure'),
     Output('adv1_table_statistics', 'children'),
     Output('adv1_stats_div', 'children')],
    [Input('adv1_region_filter', 'value'),
     Input('adv1_date_range', 'start_date'),
     Input('adv1_date_range', 'end_date')]
)
def update_data(region_filter, start_date, end_date):
    df2 = df.copy()
    df2 = df2[df2['regpark'] == region_filter]
    df2 = df2[df2['TotalParkings'] != 0]

    start_date_converted = pd.to_datetime(start_date).date()
    end_date_converted = pd.to_datetime(end_date).date()

    # Apply Date Range
    date_mask = (df2.index.date >= start_date_converted) & (df2.index.date <= end_date_converted)
    df2 = df2.loc[date_mask]

    # GroupBy Hour
    df3 = df2.copy()
    df3 = df3.groupby(by=['hour']).mean()
    df3_dif = []
    is_first = True
    for index in range(0,len(df3)):
        if not is_first:
            dif_math = round((100 - ((df3.iloc[index-1][3] * 100) / df3.iloc[index][3])), 2)
            res = '+'
            if dif_math < 0:
                res = ""
            df3_dif.append(res + str(dif_math) + "%")
        else:
            is_first = False
            df3_dif.append("0%")
    df3['dif'] = df3_dif

    # Apply Legend
    adv1_mainchart = px.line(df3, x=df3.index, y="TotalParkings", custom_data=['dif'], height=250)
    adv1_mainchart.update_layout(
        title="Total Parkings grouped by Hour of Day",
        xaxis_title="Hour",
        yaxis_title="Total Parkings",
    )
    adv1_mainchart.update_traces(
        hoverinfo='skip',
        mode='lines+markers',
        hovertemplate='Hour: <b>%{x}</b><br>'
                      + 'Total Parkings: <b>%{y}</b><br><br>'
                      + 'Difference: <b>%{customdata[0]}</b>'
                      + '<extra></extra>')

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
        title="Total Parkings grouped by Hour of Day (isRain)",
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
                str(round(len(df2[df2['isHoliday'] == 1]) / len(df3), 0)) + ' day(s)',
                str(round(len(df2[df2['isHoliday'] == 0]) / len(df3), 0)) + ' day(s)',
            ]
        }
    )

    adv1_table_statistics = dbc.Table.from_dataframe(statistics, bordered=True, dark=True, hover=True, responsive=True, striped=True)

    print("\n---------------")
    stats_label0 = ['The highest daily flow occurs at ', ' hours', ' and has an average flow ', '% higher', ' than the general average']
    stats_label0_v = round(((df3['TotalParkings'].max() * 100) / df3['TotalParkings'].mean()) - 100, 2)
    stats_label0_h = df3[df3['TotalParkings'] == df3['TotalParkings'].max()].index.values[0]

    stats_label1 = ['The lowest daily flow occurs at ', ' hours', ' and has an average flow ', '% lower', ' than the general average']
    stats_label1_v = round((df3['TotalParkings'].min() * 100) / df3['TotalParkings'].mean(), 2)
    stats_label1_h = df3[df3['TotalParkings'] == df3['TotalParkings'].min()].index.values[0]

    stats_label2 = ['Rainy', 'Sunny', ' hours have an average of ', '% more flow than ', ' hours']
    stats_label2_v = '-'
    if len(df_rain0) > 0 and len(df_rain1) > 0:
        if df_rain0['TotalParkings'].mean() > df_rain1['TotalParkings'].mean():
            stats_label2 = ['Sunny', 'Rainy', ' days have an average of ', '% more flow than ', ' days']
            stats_label2_v = round(df_rain1['TotalParkings'].mean() * 100 / df_rain0['TotalParkings'].mean(), 2)
        else:
            stats_label2_v = round(df_rain0['TotalParkings'].mean() * 100 / df_rain1['TotalParkings'].mean(), 2)

    stats_label3 = ['Holidays', 'Non-Holidays', ' have an average of ', '% more flow than ']
    stats_label3_v = '-'
    if len(df_holy0) > 0 and len(df_holy1) > 0:
        if df_holy0['TotalParkings'].mean() > df_holy1['TotalParkings'].mean():
            stats_label3 = ['Non-Holidays', 'Holidays', ' have an average of ', '% more flow than ']
            stats_label3_v = round(df_holy1['TotalParkings'].mean() * 100 / df_holy0['TotalParkings'].mean(), 2)
        else:
            stats_label3_v = round(df_holy0['TotalParkings'].mean() * 100 / df_holy1['TotalParkings'].mean(), 2)


    stats_label4 = ['Weekdays', 'Weekend days', ' have an average of ', '% more flow than ']
    stats_label4_v = '-'
    if len(df_week0) > 0 and len(df_week1) > 0:
        if df_week0['TotalParkings'].mean() > df_week1['TotalParkings'].mean():
            stats_label4 = ['Weekend days', 'Weekdays', ' have an average of ', '% more flow than ']
            stats_label4_v = round(df_week1['TotalParkings'].mean() * 100 / df_week0['TotalParkings'].mean(), 2)
        else:
            stats_label4_v = round(df_week0['TotalParkings'].mean() * 100 / df_week1['TotalParkings'].mean(), 2)

    adv1_stats_div = html.Div([
        html.Br(),
        html.Br(),
        html.H4('Parking Characteristics:'),
        html.Br(),
        html.Div([stats_label0[0], html.B([stats_label0_h, stats_label0[1]]), stats_label0[2], html.B([stats_label0_v, stats_label0[3]]), stats_label0[4], '.']),
        html.Br(),
        html.Div([stats_label1[0], html.B([stats_label1_h, stats_label1[1]]), stats_label1[2], html.B([stats_label1_v, stats_label1[3]]), stats_label1[4], '.']),
        html.Br(),
        html.Div([html.B([stats_label2[0]]), stats_label2[2], html.B([stats_label2_v]), stats_label2[3], html.B([stats_label2[1]]), stats_label2[4], '.']),
        html.Br(),
        html.Div([html.B([stats_label3[0]]), stats_label3[2], html.B([stats_label3_v]), stats_label3[3], html.B([stats_label3[1]]), '.']),
        html.Br(),
        html.Div([html.B([stats_label4[0]]), stats_label4[2], html.B([stats_label4_v]), stats_label4[3], html.B([stats_label4[1]]), '.']),
        html.Br(),
    ]),

    return (adv1_mainchart, adv2_mainchart, adv3_mainchart, adv4_mainchart, adv1_table_statistics, adv1_stats_div)