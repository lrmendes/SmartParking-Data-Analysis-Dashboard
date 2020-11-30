import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from datetime import date, datetime
from dash import callback_context
import plotly.graph_objects as go

from app import app

# http://localhost:8888/notebooks/Documents/GitHub/SmartParking-Data-Simulator/python/MachineLearning/3.%20GroupedByHour%20-%208760%20for%20Year/LSTM-MultiVariable.ipynb
# http://localhost:8888/notebooks/Documents/GitHub/SmartParking-TimeSeries-Forecasting/Scripts/ARIMA-Copy1.ipynb
# http://localhost:8888/notebooks/Documents/GitHub/SmartParking-Data-Simulator/python/DataGenerator_ExportManyCSV.ipynb

pd.options.plotting.backend = "plotly"

df = pd.read_csv('generated_dataset_article_grouped_hour.csv', dayfirst=True, parse_dates=['timeFrom'], index_col='timeFrom')
df['hour'] = df.index.hour
df['isRain'] = df['isRain'].astype('bool')
df['isHoliday'] = df['isHoliday'].astype('bool')
df['isWeekday'] = df['isWeekday'].astype('bool')
df['regpark'] = df['parking'] + ' - ' + df['region']
df['monthyear'] = df.index.strftime('%m-%Y')
df = df[df['TotalParkings'] > 0]

layout = html.Div([
    html.H4('Parameters:'),
    dbc.Row([
        dbc.Col([
            html.Div([
                dbc.Label('Train/Test Size:'),
                html.Br(),
                dcc.Slider(
                    id='pd1_date_slider',
                    min=50,
                    max=95,
                    value=80,
                    step=None,
                    marks={i: {'label': str(i)+'% / '+str(100-i)+'%', 'style': {'color': '#000000'}} for i in range(50, 96, 5)},
                ),
            ]),
        ], id='graph-grid'),
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Label('Select Parking & Region:'),
            dcc.Dropdown(
                id='pd1_region_filter',
                options=[
                    {'label': i, 'value': i} for i in df.regpark.unique()
                ],
                value=df.regpark.unique()[0],
                clearable=False,
                placeholder='Select Filter...'
            ),
        ], id='graph-grid', width="auto"),
        dbc.Col([
            dbc.Label('Consider Variables:'),
            dcc.Checklist(
                id='pd1_checklist',
                options=[
                    {'label': 'isRain', 'value': 'rain'},
                    {'label': 'isHoliday', 'value': 'holiday'},
                    {'label': 'isWeekday', 'value': 'weekday'},
                    {'label': 'SameMonth', 'value': 'month'},
                ],
                value=['rain', 'holiday', 'weekday', 'month'],
                labelStyle={'display': 'inline-block', "margin-right": "20px"}
            ),
        ], id='graph-grid', width="auto"),
        dbc.Col([
            dbc.Label('Submit:'),
            html.Br(),
            dbc.Button("Start Forecast", id="pd1_btn_forecast", color="success")
        ], id='graph-grid', width="auto")
    ]),
    html.Br(),
    html.H4('Data Visualization:'),
    dbc.Row([
        dbc.Col([
            dcc.Loading(id="loading-icon", children=[html.Div(dcc.Graph(id='pd1_mainchart'))], type="default")
        ], width=9),
        dbc.Col([
            html.Div([], id='pd1_table_statistics'),
        ])
    ], id='graph-grid'),
])


@app.callback(
    [Output('pd1_mainchart','figure'),
     Output('pd1_table_statistics', 'children')],
    [Input('pd1_region_filter','value'),
     Input('pd1_date_slider','value'),
     Input('pd1_checklist','value'),
     Input("pd1_btn_forecast", "n_clicks")]
)

def update_data(region_filter, slider_date, checklist, btn_forecast):
    print("Slider: ", slider_date)
    print("Checklist: ", checklist)
    print("Clicks: ", btn_forecast)
    
    pd1_mainchart = go.Figure()
    pd1_table_statistics = html.Div()
    
    # Check if Download Button has fired
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if 'pd1_btn_forecast' in changed_id:
        # Apply Date Range
        df2 = df.copy()

        #df2 = df2[df2['regpark'] == region_filter]
        #df2 = df2[df2['TotalParkings'] != 0]


        print("Clicou")

    """
    # Apply Legend
    pd1_mainchart = px.scatter(df2, x=df2.index, y="timeTo", height=700, custom_data=['isRain','isHoliday','isWeekday'], color=legenddropval)
    pd1_mainchart.update_layout(
        title="All Parkings by Entrance & Exit Date/Times",
        xaxis_title="Entrance",
        yaxis_title="Exit",
        legend_title=legenddropval,
    )
    pd1_mainchart.update_traces(
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
    pd1_daily_mean = html.Div('Daily Mean Records: ' + str(round((total_records / delta.days), 2)) + ' parkings/day')

    # Rainy & Sunny Records

    statistics = pd.DataFrame(
        {
            "Statistic": ['Total Records: ','Daily Average Records: ', 'Sunny Weather Records: ','Rainy Weather Records: '],
            "Value": [str(total_records), str(round((total_records / delta.days), 2)) + ' parkings/day', str(len(df2[df2['isRain'] == 0])), str(len(df2[df2['isRain'] == 1]))]
        }
    )

    pd1_table_statistics = dbc.Table.from_dataframe(statistics, bordered=True, dark=True, hover=True, responsive=True, striped=True)
    """

    return (pd1_mainchart, pd1_table_statistics)