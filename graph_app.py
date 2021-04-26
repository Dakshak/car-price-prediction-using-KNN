import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_ui as dui
import plotly.graph_objs as go
import pandas as pd
from plotly.subplots import make_subplots
import numpy as np
import pyodbc
import sys

# Read in the data
df_original = pd.read_csv('static/633006662.csv')
t_df = df_original.sort_values(by='Calc_CycleCount',ascending=True)

# Get a list of drop down menu items
kit_num = sorted(t_df.Kit_No.unique())
part_num = sorted(t_df.WP_Customer_Part_No.unique())
serial_num = sorted(t_df.Corrected_Serial_No.unique().astype(str))
parameter = sorted(t_df.Parameter.unique())

# Create the app
app = dash.Dash()
server = app.server

# Populate the layout with HTML and graph components
app.layout = html.Div([
    
    html.H2(children="Linear Chart",
           style={'textAlign': 'center',
#                  'color': layout_colors['text'],
#                  'backgroundColor': layout_colors['background']
                 }),
    html.Div(
        [
            html.H4('Kit Number', style={'font-weight': 'bold', "text-align": "center"}),
            dcc.Dropdown(
                id="KitNum",
                options=[{
                    'label': i,
                    'value': i
                } for i in kit_num],
                value=''),
            
        ],
        style={'width': '15%',
               'display': 'inline-block'}),

    html.Div(
        [
            
        ],
        style={'width': '3%',
               'display': 'inline-block'}),

    html.Div(
        [
            html.H4('Part Number', style={'font-weight': 'bold', "text-align": "center"}),
            dcc.Dropdown(
                id="PartNum",
                options=[{
                    'label': i,
                    'value': i
                } for i in part_num],
                value=''),
            
        ],
        style={'width': '15%',
               'display': 'inline-block'}),

    html.Div(
        [
            
        ],
        style={'width': '3%',
               'display': 'inline-block'}),


    html.Div(
        [
            html.H4('Serial Number', style={'font-weight': 'bold', "text-align": "center"}),
            dcc.Dropdown(
                id="SerialNum",
                options=[{
                    'label': i,
                    'value': i
                } for i in serial_num],
                value=''),
            
        ],
        style={'width': '15%',
               'display': 'inline-block'}),

    html.Div(
        [
            
        ],
        style={'width': '3%',
               'display': 'inline-block'}),

    html.Div(
        [
            html.H4('Parameter', style={'font-weight': 'bold', "text-align": "center"}),
            dcc.Dropdown(
                id="param",
                options=[{
                    'label': i,
                    'value': i
                } for i in parameter],
                value=''),
            
        ],
        style={'width': '15%',
               'display': 'inline-block'}),




    dcc.Graph(id='graph', style={'height':'100%', 'width':'100%'})
])

@app.callback(
    dash.dependencies.Output('graph', 'figure'),
    [dash.dependencies.Input('KitNum', 'value'),
   dash.dependencies.Input('PartNum', 'value'),
   dash.dependencies.Input('SerialNum', 'value'),
   dash.dependencies.Input('param', 'value')
    ])



def update_graph(kit_n, part_n, serial_n, para):

    if kit_n == '' or part_n == '' or serial_n == '' or para == '':

        fig = go.Figure()
        fig.add_trace(go.Bar(x=[0], y=[0]))
        fig.update_layout(barmode='relative', title_text='Select Args to Display Chart', title_x = 0.5, title_y = 0.8)
        return fig

    else:

        df = t_df[(t_df.Kit_No == kit_n) & (t_df.WP_Customer_Part_No == part_n) & (t_df.Corrected_Serial_No == serial_n) & (t_df.Parameter == para)]


        # assigning variables
        x = df['Calc_CycleCount']
        y = df.Calc_Overall_MeasurementAvg


        #plotting linear regresson line
        m, b = np.polyfit(x, y, 1)
        z =  m*x + b

        #setting up parameters
        two_std_positive = z+(2*np.std(z))
        two_std_negative = z-(2*np.std(z))


        #setting lsl and usl based on first value
        # not correct as lsl and usl value is varying
        #this is done just to show a proper plot
        usl = df.Upper_Limit.values
        lsl = df.Lower_Limit.values

        usl = [usl[0]]*len(usl)
        lsl = [lsl[0]]*len(lsl)

        fig = go.Figure()
        std_dev_param = [two_std_positive, two_std_negative,]
        color_std = ['black', 'black']
        legend_std = ["+2 std", "-2 std"]


        parameters = [df.Calc_Overall_MeasurementAvg, df.MeasurementAVG, z]
        legend_name = ["Overall Measurement AVG", "Selected SN", "linear fit"]
        color = ['green', 'blue', 'yellow']

        param_usl_lsl = [usl, lsl]
        leg_usl_lsl = ["usl", "lsl"]
        color_usl_lsl = ['black', 'black']




        for p, c, ln in zip(std_dev_param, color_std, legend_std):
            fig.add_trace(
                go.Scatter(
                    name=ln,
                    x=df.Calc_CycleCount,
                    y=p,
                    mode="lines",
                    line=go.scatter.Line(color=c),
                    showlegend=True)
            )

        fig.update_traces(
            line=dict(dash="dashdot", width=1),
            selector=dict(type="scatter", mode="lines")
            )


        for p, c, ln in zip(param_usl_lsl, color_usl_lsl, leg_usl_lsl):
            fig.add_trace(
                go.Scatter(
                    name=ln,
                    x=df.Calc_CycleCount,
                    y=p,
                    mode="lines",
                    line=go.scatter.Line(color=c),
                    showlegend=True,
                    visible = 'legendonly')
            )


        for p, c, ln in zip(parameters, color, legend_name):
            fig.add_trace(
                go.Scatter(
                    name=ln,
                    x=df.Calc_CycleCount,
                    y=p,
                    mode="lines",
                    line=go.scatter.Line(color=c),
                    showlegend=True)
            )

        fig.add_trace(go.Scatter(
            x=x, y=y,
            mode='markers',
            name='error bar',
            error_y=dict(
                type='data',
                array=df.Calc_Overall_Std_MeasurementAvg,
                color='red',
                thickness=1.5,
                width=3,
            ),
            marker=dict(color='red', size=8)
        ))


        fig.update_layout(
            title="Degradation Pattern",
            xaxis_title="Selected SN & Calc Overall Measurement AVG",
            yaxis_title="Calc Cycle Count",
            legend_title="Parameters",
            font=dict(
                family="Courier New, monospace",
                size=12,
                color="RebeccaPurple"
            )
        )

                            
        return fig



if __name__ == '__main__':
    app.run_server(debug=True)#port=8050, host='127.0.0.1')