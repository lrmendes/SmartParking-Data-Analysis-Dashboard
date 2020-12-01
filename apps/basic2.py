import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from dash import callback_context
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff

from app import app

from datetime import datetime

from dash_extensions import Download
from dash_extensions.snippets import send_data_frame

pd.options.plotting.backend = "plotly"

target_cols = ['timeFrom', 'isRain', 'isHoliday', 'isWeekday']
df = pd.read_csv('generated_dataset_article.csv', dayfirst=True, parse_dates=['timeFrom'], index_col='timeFrom',
                 usecols=target_cols)
df['isRain'] = df['isRain'].astype('bool')
df['isHoliday'] = df['isHoliday'].astype('bool')
df['isWeekday'] = df['isWeekday'].astype('bool')

min_date = df.index.min()
max_date = df.index.max()
start_min_date = min_date
if len(df.index) > 5000:
    start_min_date = df.index[len(df)-5000]

layout = html.Div([
    html.H4('Filters:'),
    dbc.Row([
        dbc.Col([
            html.Div([
                dbc.Label('Date Range:'),
                html.Br(),
                dcc.DatePickerRange(
                    id='b2_date_range',
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
            ]),
        ], className='graph-grid', width="auto"),
        dbc.Col([
            html.Div([
                dbc.Label('Graph Type:'),
                dcc.Dropdown(
                    id='b2_graph_type',
                    options=[
                        {'label': 'Default', 'value': 'default'},
                        {'label': 'Distplot', 'value': 'dist'},
                        {'label': 'Normal Distribution', 'value': 'normal'},
                    ],
                    value='default',
                    clearable=False,
                    placeholder='Select Graph Type...'
                ),
            ]),
        ], className='graph-grid'),
    ]),
    html.Br(),
    html.H4('Data Visualization:'),
    dbc.Row([
        dbc.Col([
            html.Br(),
            dcc.Loading(id="loading-icon",children=[html.Div(dcc.Graph(id='b2_mainchart'))], type="default")
        ], width=9, className='graph-grid'),
        dbc.Col([
            html.Div([], id='b2_table_statistics'),
            html.Div([html.Button("Download CSV", id="b2_btn_download_csv"), Download(id="b2_download_csv")])
        ], id='statistics-grid'),
    ])
])

@app.callback(
    [Output('b2_mainchart', 'figure'),
     Output('b2_table_statistics', 'children'),
     Output("b2_download_csv", "data")],
    [Input('b2_legend_filter', 'value'),
     Input('b2_date_range','start_date'),
     Input('b2_date_range','end_date'),
     Input('b2_graph_type','value'),
     Input("b2_btn_download_csv", "n_clicks")]
)

def update_data(legenddropval,start_date,end_date, b2_graph_type,b2_btn_download_csv):
    df2 = df.copy()

    # Apply Date Range
    date_mask = (df2.index >= start_date) & (df2.index <= end_date)
    df2 = df2.loc[date_mask]

    # Apply Legends
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

    if b2_graph_type == 'dist':
        mainchart = ff.create_distplot([df2['TotalParkings']], ['Distplot'])
    elif b2_graph_type == 'normal':
        mainchart = ff.create_distplot([df2['TotalParkings']], ['Distplot'], curve_type='normal')
    else:
        mainchart = px.line(df2, x=df2.index, y='TotalParkings', custom_data=['isWeekday', 'isHoliday'])
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

    total_records = len(df2)

    statistics = pd.DataFrame(
        {
            "Statistic": ['Total Records: ','Average Parkings'],
            "Value": [str(total_records), str(round(df2['TotalParkings'].mean(), 2))]
        }
    )

    b2_table_statistics = dbc.Table.from_dataframe(statistics, bordered=True, dark=True, hover=True, responsive=True, striped=True)

    # Check if Download Button has fired
    download_file = None
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if 'b2_btn_download_csv' in changed_id:
        download_file = send_data_frame(df2.to_csv, filename=datetime.now().strftime("%Y-%m-%d_%H-%M-%S")+".csv")

    return (mainchart, b2_table_statistics, download_file)
