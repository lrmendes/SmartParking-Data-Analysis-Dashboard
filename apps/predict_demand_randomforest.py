import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from datetime import date, datetime
from dash import callback_context
import plotly.graph_objects as go
from dash.dash import no_update

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

from app import app

pd.options.plotting.backend = "plotly"

df = pd.read_csv('generated_dataset_article_grouped_hour.csv')
df['timeFrom'] = pd.to_datetime(df['timeFrom'], errors='ignore')
df['timeFrom'] = pd.to_datetime(df["timeFrom"].dt.strftime('%d-%m-%Y %H:%M'))

df['isRain'] = df['isRain'].astype('bool')
df['isHoliday'] = df['isHoliday'].astype('bool')
df['isWeekday'] = df['isWeekday'].astype('bool')
df['regpark'] = df['parking'] + ' - ' + df['region']

#df['weekday'] = df['timeFrom'].dt.dayofweek
df['hour'] = df['timeFrom'].dt.hour
df['month'] = df['timeFrom'].dt.month
df = df.set_index('timeFrom')
df = df[df['TotalParkings'] > 0]

def statistics_table(predict_df):
    # Statistics
    p1 = len(predict_df[predict_df['PredictProximity'] >= 95])
    p2 = len(predict_df[(predict_df['PredictProximity'] >= 90) & (predict_df['PredictProximity'] < 95)])
    p3 = len(predict_df[(predict_df['PredictProximity'] >= 80) & (predict_df['PredictProximity'] < 90)])
    p4 = len(predict_df[(predict_df['PredictProximity'] >= 70) & (predict_df['PredictProximity'] < 80)])
    p5 = len(predict_df[(predict_df['PredictProximity'] >= 60) & (predict_df['PredictProximity'] < 70)])
    p6 = len(predict_df[(predict_df['PredictProximity'] >= 50) & (predict_df['PredictProximity'] < 60)])
    p7 = len(predict_df[predict_df['PredictProximity'] < 50])
    p_total = len(predict_df)

    statistics = pd.DataFrame(
        {
            "Predict Proximity": [
                '95% ~ 100%',
                '90% ~ 95%',
                '80% ~ 90%',
                '70% ~ 80%',
                '60% ~ 70%',
                '50% ~ 60%',
                'less than 50%',
                '',
                'Total Records',
            ],
            "Total": [
                str(p1) + ' records',
                str(p2) + ' records',
                str(p3) + ' records',
                str(p4) + ' records',
                str(p5) + ' records',
                str(p6) + ' records',
                str(p7) + ' records',
                '',
                str(p_total) + ' records',
            ],
            "Percentage": [
                str(round(p1 * 100 / p_total, 2)) + "%",
                str(round(p2 * 100 / p_total, 2)) + "%",
                str(round(p3 * 100 / p_total, 2)) + "%",
                str(round(p4 * 100 / p_total, 2)) + "%",
                str(round(p5 * 100 / p_total, 2)) + "%",
                str(round(p6 * 100 / p_total, 2)) + "%",
                str(round(p7 * 100 / p_total, 2)) + "%",
                '',
                "100%",
            ]
        }
    )
    return statistics


layout = html.Div([
    dbc.Row([html.H3("Parking Demand Prediction - Random Forest")], justify="center", align="center"),
    html.Br(),
    html.H4('Parameters:'),
    dbc.Row([
        dbc.Col([
            html.Div([
                dbc.Label('Train/Test Size:'),
                html.Br(),
                dcc.Slider(
                    id='pd2_date_slider',
                    min=50,
                    max=95,
                    value=90,
                    step=None,
                    marks={i: {'label': str(i) + '% / ' + str(100 - i) + '%', 'style': {'color': '#000000'}} for i in
                           range(50, 96, 5)},
                ),
            ]),
        ], className='graph-grid'),
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Label('Select Parking & Region:'),
            dcc.Dropdown(
                id='pd2_region_filter',
                options=[
                    {'label': i, 'value': i} for i in df.regpark.unique()
                ],
                value=df.regpark.unique()[0],
                clearable=False,
                placeholder='Select Filter...'
            ),
        ], className='graph-grid', width="auto"),
        dbc.Col([
            dbc.Label('Submit:'),
            html.Br(),
            dbc.Button("Start Forecast", id="pd2_btn_forecast", color="success")
        ], className='graph-grid', width="auto")
    ]),
    html.Br(),
    html.H4('Data Visualization:'),
    dbc.Row([
        dbc.Col([
            dcc.Loading(id="pd2_loading-icon", children=[html.Div(dcc.Graph(id='pd2_mainchart'))], type="default")
        ]),
    ], className='graph-grid'),
    dbc.Row([
        dbc.Col([
            dcc.Loading(id="pd2_loading-icon", children=[html.Div(dcc.Graph(id='pd2_dailychart'))], type="default")
        ]),
    ], className='graph-grid'),
    html.Br(),
    dbc.Row([
        dbc.Col([], width=3),
        dbc.Col([
            html.Div([], id='pd2_table_statistics'),
        ], width=6),
        dbc.Col([], width=3),
    ])
])


@app.callback(
    [Output('pd2_mainchart', 'figure'),
     Output('pd2_dailychart', 'figure'),
     Output('pd2_table_statistics', 'children')],
    [Input('pd2_region_filter', 'value'),
     Input('pd2_date_slider', 'value'),
     Input("pd2_btn_forecast", "n_clicks")]
)
def update_data(region_filter, train_size, btn_forecast):
    pd2_mainchart = go.Figure()
    pd2_mainchart.update_layout(height=250)

    pd2_dailychart = go.Figure()
    pd2_dailychart.update_layout(height=250)

    pd2_table_statistics = html.Div()

    # Check if StartForecast Button has fired
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if not 'pd2_btn_forecast' in changed_id:
        return no_update
    else:
        # Apply Date Range
        df2 = df.copy()

        df2 = df2[df2['regpark'] == region_filter]
        df2 = df2[df2['TotalParkings'] != 0]

        # Remove Unnecessary variables
        df2 = df2.drop(columns=['region', 'parking', 'regpark'])

        # ******************************
        # RandomForest Algorithm
        X = df2.drop('TotalParkings', axis=1)
        y = df2['TotalParkings']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size= train_size / 100, random_state=42)

        rfr = RandomForestRegressor()
        rfr.fit(X_train, y_train)
        rfr_predictions = rfr.predict(X_test)

        predict_df = pd.DataFrame({"TotalParkings": y_test, "TotalParkingsPredict": rfr_predictions})
        predict_df = predict_df.sort_index()
        predict_df = predict_df[int(len(predict_df) * (train_size / 100)):]
        #predict_df = pd.DataFrame({"TotalParkings": df2[-len(rfr_predictions):].TotalParkings, "TotalParkingsPredict": rfr_predictions})

        # *******************************

        pd2_mainchart.add_trace(go.Scatter(x=predict_df.index, y=predict_df.TotalParkings,
                                           mode='lines+markers',
                                           name='Real Data'))
        pd2_mainchart.add_trace(go.Scatter(x=predict_df.index, y=predict_df.TotalParkingsPredict,
                                           mode='lines+markers',
                                           name='Predict Data'))
        pd2_mainchart.update_layout(
            height=500,
            title="[" + str(region_filter) + "] Forecast - Total Parkings Grouped by Hour",
            xaxis_title="Hour",
            yaxis_title="Total Parkings",
        )
        pd2_mainchart.layout.update(
            hovermode='x unified',
            margin=dict(l=20, r=20, t=40, b=5),
        )

        # Export Data Grouped By Day - 365 Rows by Year
        df3 = predict_df.copy()
        pd.to_datetime(df3.index, errors='ignore')
        df3 = df3.resample('D').sum()

        pd2_dailychart.add_trace(go.Scatter(x=df3.index, y=df3.TotalParkings,
                                            mode='lines+markers',
                                            name='Real Data'))
        pd2_dailychart.add_trace(go.Scatter(x=df3.index, y=df3.TotalParkingsPredict,
                                            mode='lines+markers',
                                            name='Predict Data'))
        pd2_dailychart.update_layout(
            height=500,
            title="[" + str(region_filter) + "] Forecast - Total Parkings Grouped by Day",
            xaxis_title="Hour",
            yaxis_title="Total Parkings",
        )

        pd2_dailychart.layout.update(
            hovermode='x unified',
            margin=dict(l=20, r=20, t=40, b=5),
        )

        # Fill Proximity and Difference Columns
        df3_dif = {'difference': [], 'proximity': []}

        for row, index in predict_df.iterrows():
            prox_math = 100 - abs(round((((index['TotalParkingsPredict'] * 100) / index['TotalParkings'])) - 100, 2))
            df3_dif['proximity'].append(prox_math)

            dif_math = round((((index['TotalParkingsPredict'] * 100) / index['TotalParkings'])) - 100, 2)
            df3_dif['difference'].append(dif_math)

        predict_df['PredictProximity'] = df3_dif['proximity']
        predict_df['PredictDifference'] = df3_dif['difference']

        pd2_table_statistics = dbc.Table.from_dataframe(statistics_table(predict_df), bordered=True, dark=True,
                                                        hover=True,
                                                        responsive=True, striped=True)

    return (pd2_mainchart, pd2_dailychart, pd2_table_statistics)
