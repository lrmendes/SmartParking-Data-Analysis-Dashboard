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

df = pd.read_csv('generated_dataset_article_grouped_hour.csv')
df['timeFrom'] = pd.to_datetime(df['timeFrom'], errors='ignore')
df['timeFrom'] = pd.to_datetime(df["timeFrom"].dt.strftime('%d-%m-%Y %H:%M'))

df['isRain'] = df['isRain'].astype('bool')
df['isHoliday'] = df['isHoliday'].astype('bool')
df['isWeekday'] = df['isWeekday'].astype('bool')
df['regpark'] = df['parking'] + ' - ' + df['region']

df['weekday'] = df['timeFrom'].dt.dayofweek
df['hour'] = df['timeFrom'].dt.hour
df['month'] = df['timeFrom'].dt.month
df = df.set_index('timeFrom')
df = df[df['TotalParkings'] > 0]

def predict_by_average(base_df, predict_df):
    predict_parkings = []
    for row, index in predict_df.iterrows():
        lens = []
        # Group Parking by same Hour & Weekday
        average_df = base_df.copy()
        average_df = average_df[(average_df['hour'] == index['hour']) & (average_df['weekday'] == index['weekday'])]
        lens.append(len(average_df))
        valid_df = average_df.copy()

        # Group Parking by same isRain condition
        average_df = average_df[(average_df['isRain'] == index['isRain'])]
        lens.append(len(average_df))
        if len(average_df) > 0:
            valid_df = average_df.copy()

        # Group Parking by same isHoliday condition
        average_df = average_df[(average_df['isHoliday'] == index['isHoliday'])]
        lens.append(len(average_df))
        if len(average_df) > 0:
            valid_df = average_df.copy()

        # Group Parking by same Month
        average_df = average_df[(average_df['month'] == index['month'])]
        lens.append(len(average_df))
        if (len(average_df) > 0):
            valid_df = average_df.copy()

        predict_parkings.append(valid_df['TotalParkings'].mean())

    predict_df['TotalParkingsPredict'] = predict_parkings
    return predict_df

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
                    value=90,
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
        ]),
    ], id='graph-grid'),
    dbc.Row([
        dbc.Col([
            dcc.Loading(id="loading-icon", children=[html.Div(dcc.Graph(id='pd1_dailychart'))], type="default")
        ]),
    ], id='graph-grid'),
    dbc.Row([
        dbc.Col([
            html.Div([], id='pd1_table_statistics'),
        ])
    ])
])


@app.callback(
    [Output('pd1_mainchart','figure'),
     Output('pd1_dailychart','figure'),
     Output('pd1_table_statistics', 'children')],
    [Input('pd1_region_filter','value'),
     Input('pd1_date_slider','value'),
     Input('pd1_checklist','value'),
     Input("pd1_btn_forecast", "n_clicks")]
)

def update_data(region_filter, train_size, checklist, btn_forecast):
    pd1_mainchart = go.Figure()
    pd1_mainchart.update_layout(height=250)

    pd1_dailychart = go.Figure()
    pd1_dailychart.update_layout(height=250)

    pd1_table_statistics = html.Div()
    
    # Check if Download Button has fired
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if 'pd1_btn_forecast' in changed_id:
        # Apply Date Range
        df2 = df.copy()

        df2 = df2[df2['regpark'] == region_filter]
        df2 = df2[df2['TotalParkings'] != 0]

        test = int(len(df2) * ((100-train_size)/100))

        df_train = df2.iloc[:-test]
        df_test = df2.iloc[-test:]

        predict_df = predict_by_average(df_train, df_test)
        pd1_mainchart.add_trace(go.Scatter(x=predict_df.index, y=predict_df.TotalParkings,
                                           mode='lines+markers',
                                           name='Real Data'))
        pd1_mainchart.add_trace(go.Scatter(x=predict_df.index, y=predict_df.TotalParkingsPredict,
                                           mode='lines+markers',
                                           name='Predict Data'))
        pd1_mainchart.update_layout(
            height=500,
            title="["+str(region_filter)+"] Forecast - Total Parkings Grouped by Hour",
            xaxis_title="Hour",
            yaxis_title="Total Parkings",
        )
        pd1_mainchart.layout.update(
            hovermode='x unified',
            margin=dict(l=20, r=20, t=40, b=5),
        )

        # Export Data Grouped By Day - 365 Rows by Year
        df3 = predict_df.copy()
        pd.to_datetime(df3.index, errors='ignore')
        df3 = df3.resample('D').sum()

        pd1_dailychart.add_trace(go.Scatter(x=df3.index, y=df3.TotalParkings,
                                            mode='lines+markers',
                                            name='Real Data'))
        pd1_dailychart.add_trace(go.Scatter(x=df3.index, y=df3.TotalParkingsPredict,
                                            mode='lines+markers',
                                            name='Predict Data'))
        pd1_dailychart.update_layout(
            height=500,
            title="["+str(region_filter)+"] Forecast - Total Parkings Grouped by Day",
            xaxis_title="Hour",
            yaxis_title="Total Parkings",
        )

        pd1_dailychart.layout.update(
            hovermode='x unified',
            margin=dict(l=20, r=20, t=40, b=5),
        )


    return (pd1_mainchart, pd1_dailychart, pd1_table_statistics)