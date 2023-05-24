import plotly.graph_objects as go
import pandas as pd
import numpy as np
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import base64
import io
from scipy import optimize
import dash_bootstrap_components as dbc

from dash import dash_table



x = np.linspace(0, 10, 50)
y = np.exp(-x)

df_init = pd.DataFrame(np.array([x,y]).T, columns = ["time", "fluorescence"])
df_init=df_init.to_dict()

def exp_decay(parameters, xdata):
    '''
    Calculate an exponential decay of the form:
    S= a * exp(-xdata/b)
    '''
    A = parameters[0]
    tau = parameters[1]
    y0 = parameters[2]
    return A * np.exp(-xdata/tau) + y0

def residuals(parameters, x_data, y_observed, func):
    '''
    Compute residuals of y_predicted - y_observed
    where:
    y_predicted = func(parameters,x_data)
    '''
    return func(parameters,x_data) - y_observed

def simple_tau(time_array, fluo, init):
    """perform monoexponential fit"""
    fluo_transition = fluo
    time_transition = time_array
    OptimizeResult  = optimize.least_squares(residuals,  init, bounds = (-1e9,1e9),
                                        args = (time_transition, fluo_transition, exp_decay))
    parameters_estimated = OptimizeResult.x
    return parameters_estimated

# Define the chemical options
chemical_options = [
    {'label': 'Dronpa 2', 'value': 'd2'},
    {'label': 'Nitrone', 'value': 'Nit'},
    {'label': 'DASA', 'value': 'DASA'},
    {'label': 'Cinamate + Rhodamine', 'value': 'Cin'},
    {'label': 'Photosynthetic apparatus', 'value': 'PA'}
]

# Define a function to calculate the value based on the selected component
def calculate_value(chemical, sigma, params):
    # Replace this with your own calculation logic based on the chemical and wavelength
    return 1e6/(sigma*params[1])

# Create the Dash app instance
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define the layout of the app

controls = dbc.Card(
    [
        html.Div(
            [

        html.Div(id='select-chemical', 
                                children=[html.Div('Select the actinometer used:', style={'font-weight': 'bold', 'margin-right': '24px',
                                'font-size': '24px'})]),
        dcc.Dropdown(
                        id='chemical-dropdown',
                        options=chemical_options,
                        value=chemical_options[0]['value'],
                        style = {'width':"80%"}
                        ),
        
        html.Div(id='select-wavelength', 
                                children=[html.Div('Select the excitation wavelength used:', style={'font-weight': 'bold', 'margin-right': '24px',
                                'font-size': '24px'})]),
        dcc.Dropdown(
                    id='wavelength-dropdown',
                    value=None,
                    style =  {'width':"80%"}
                    ),

        html.Div(id='output-container', 
                                children=[html.Div('Sigma (m²/mol):', style={'font-weight': 'bold', 'margin-right': '10px', "color":"darkred"})]),
        html.Div(id='sigma-value', 
                 style={'display': 'inline-block', 'font-size': '24px', 'vertical-align': 'middle', "color":"darkred"},
                 ),
            ]),
         html.Div(id='direct-table', 
                                children=[html.Div(html.Div([
                                            html.P([
                                                html.Strong('Upload your table:')
                                            ], style={'font-size':'24px'}),
                                            html.Ul([
                                                html.Li('.csv file'),
                                                html.Li('column separator: comma ","'),
                                                html.Li('decimal separator: dot "."')],
                                             style={'display': 'inline-block', 'font-size': '18px', 'vertical-align': 'middle'}),
                                            ]),
                                            
                                            
                                
                                )]), 
        
        dcc.Upload(         id='upload-data',
                            children=html.Div([
                                     'Drag and Drop or ',
                            html.A('Select Files')
                        ]),
                            style={
                                'width': '80%',
                                'height': '60px',
                                'lineHeight': '60px',
                                'borderWidth': '1px',
                                'borderStyle': 'dashed',
                                'borderRadius': '5px',
                                'textAlign': 'center',
                                'margin': '10px',
                            },
                            multiple=False,    
                        ),
    
    ]   
)
            
upload_table = dbc.Card(
    [   
        html.Div(id='output-table')

            ]
        )


values_out = dbc.Card( 
    [   

    html.Div(id='output-container3', 
                    children=[html.Div('Time constant (s):', style={'font-weight': 'bold', 'margin-right': '10px'})]),

    html.Div(id='tau-value', 
                
                style={'display': 'inline-block', 'font-size': '24px', 'vertical-align': 'middle'}),

        html.Div(id='output-container2', 
                    children=[html.Div('Light intensity (µE/m²/s):', style={'font-weight': 'bold', 'margin-right': '10px'})]),

    html.Div(id='intensity-value-eins', 
                style={'display': 'inline-block', 'font-size': '24px', 'vertical-align': 'middle'},
                ),
    html.Div(id='output-container5', 
                    children=[html.Div('Light intensity (mW/mm²):', style={'font-weight': 'bold', 'margin-right': '10px'})]),

    html.Div(id='intensity-value-watt', 
                style={'display': 'inline-block', 'font-size': '24px', 'vertical-align': 'middle'},
                )  
        ]
        )


graph =  html.Div([

            html.Div(id='select-axis', 
                                children=[html.Div('Select the X and Y column names:', style={'font-weight': 'bold', 'margin-right': '10px',
                                "font-size":"24px"})]),
       

            dcc.Store(id='data-store', data = df_init),
            dcc.Store(id='fit-store', data = "None"),
            dcc.Dropdown(
                id='x-axis-dropdown',
                options=[],
                value=None,
                placeholder="Select X-axis Column",
                style={'margin': '10px'}
                    ),
            dcc.Dropdown(
                id='y-axis-dropdown',
                options=[],
                value=None,
                placeholder="Select Y-axis Column",
                style={'margin': '10px'}
            ),
            dcc.Graph(id='data-plot',
                style={
                #'height': '500px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
                 },
              
                 ),

            ])   

app.layout = dbc.Container(
    [
        html.H1("Light calibration"),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(controls, md=4),
                dbc.Col(graph, md=4),

            ]),
        dbc.Row(
            [
                dbc.Col(upload_table, md=4),
                dbc.Col(values_out, md=4),

            ]
        )
               
      ],
            fluid=True,

)

# Define the callback function that updates the wavelength dropdown based on the selected chemical
@app.callback(
    Output('wavelength-dropdown', 'options'),
    Input('chemical-dropdown', 'value')
)
def update_wavelength_dropdown_options(chemical):
    if chemical == 'd2':
        wavelengths = [{'label': '445', 'value': 140},
                        {'label': '480', 'value': 198}, 
                        {'label': '500', 'value': 128}]
    elif chemical == 'Nit':
        wavelengths = [{'label': '365', 'value': 960},
                        {'label': '380', 'value': 1200},
                        {'label': '405', 'value': 1100},
                        {'label': '420', 'value': 850},
                        ]
    elif chemical == 'Cin':
        wavelengths = [{'label': '350', 'value': 940},
                       {'label': '365', 'value': 1200},
                       {'label': '380', 'value': 1000},
                       {'label': '405', 'value': 184},
                       {'label': '420', 'value': 49},
                       ]
    elif chemical == 'DASA':
        wavelengths = [{'label': '530', 'value': 255},
                       {'label': '560', 'value': 530},
                       {'label': '600', 'value': 885},
                       {'label': '632', 'value': 1135},
                       {'label': '650', 'value': 575}]
    elif chemical == 'PA':
        wavelengths = [{'label': '405', 'value': 2000000},
                       {'label': '470', 'value': 2000000},
                        {'label': '650', 'value': 1100000}]
    else:
        wavelengths = []
    return wavelengths


"""SCALAR VALUES"""
# Define the callback function that updates the output value based on the selected chemical and wavelength
@app.callback(
    Output('sigma-value', 'children'),
    Input('wavelength-dropdown', 'value')
)
def update_output_value(sigma):
    if sigma is None:
        return ""
    else:
        return sigma
    
# Define the callback function that updates the output value based on the selected chemical and wavelength
@app.callback(
    Output('tau-value', 'children'),
    Input('fit-store', 'data')
)
def update_tau_value(params):
    if params is None:
        return ""
    else:
        return '{:.1e}'.format(params[1])
        
@app.callback(
    Output('intensity-value-watt', 'children'),
    Input('fit-store', 'data'),
    Input('chemical-dropdown', 'value'),
    Input('wavelength-dropdown', 'value'),
    State('wavelength-dropdown', 'options')

)
def update_output_value(params, chemical, sigma, options):
    if sigma is None  or params is None:
        return ""
    else:
        wavelength = [option['label'] for option in options if option['value'] == sigma][0]
        value = calculate_value(chemical, sigma, params)
        return '{:.1e}'.format(value/1000*120/int(wavelength))
    
@app.callback(
    Output('intensity-value-eins', 'children'),
    Input('fit-store', 'data'),
    Input('chemical-dropdown', 'value'),
    Input('wavelength-dropdown', 'value')
)
def update_output_value(params, chemical, sigma):
    if sigma is None or params is None:
        return ""
    else:
        value = calculate_value(chemical, sigma, params)
        return '{:.1e}'.format(value/1e6)

"""DATA STORAGE"""
@app.callback(
    Output('data-store', 'data'),
    Input('upload-data', 'contents'),
    Input('upload-data', 'filename')
)
def update_storage(contents, filename):
    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        print(decoded)
        try:
            if 'csv' in filename:
                # Assume that the user uploaded a CSV file
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

            elif 'xls' in filename:
                # Assume that the user uploaded an Excel file
                df = pd.read_excel(decoded, engine = 'openpyxl', encoding='ISO-8859-1')

            elif 'txt' or 'tsv' in filename:
                # Assume that the user upl, delimiter = '\t'
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), delimiter = '\t')
            
            else:
                return html.Div([
                    'The uploaded file format is not supported. Please upload a CSV, Excel, TXT or TSV file.'
                ])
            


            return df.to_dict()
        
        except Exception as e:
            print(e)
            return html.Div([
                'There was an error processing this file.'
            ])


def read_table(df):
        df = pd.DataFrame(df)
        return html.Div([
            dash_table.DataTable(
                data=df.to_dict('records'),

                columns=[{'name': i, 'id': i} for i in df.columns],
                        
                style_table={'overflowX': 'scroll', 
                             'maxHeight': '200px',
                             'maxWidth': '100%',
                             'overflowY': 'scroll'},

            )])

@app.callback(
    Output('output-table', 'children'),
    Input('data-store', 'data'),
)
def update_table(df):
        if df is not None:
            children = [read_table(df)]
            return children

            
@app.callback(
    dash.dependencies.Output('x-axis-dropdown', 'options'),
    dash.dependencies.Output('y-axis-dropdown', 'options'),
    dash.dependencies.Input('data-store', 'data')
)
def update_dropdowns(df):
    if df is not None:
        df = pd.DataFrame(df)
        x_axis_options = [{'label': col, 'value': col} for col in df.columns]
        y_axis_options = [{'label': col, 'value': col} for col in df.columns]
        return x_axis_options, y_axis_options
    else:
        return [], []

@app.callback(
    Output('fit-store', 'data'),
    Input('data-store',"data"),
    Input('x-axis-dropdown', 'value'),
    Input('y-axis-dropdown', 'value'),

)
def update_fit(df, key_time, key_fluo):
    if key_time is None or df is None:
        return None
    else:
        df = pd.DataFrame(df)
        X = df[key_time].values
        Y = df[key_fluo].values
        amplitude = np.max(Y) - np.min(Y)
        noise = np.min(Y)
        span = (np.max(X) - np.min(X))/5
        init = [amplitude, span, noise]
        params = simple_tau(X, Y, init)
        return params


# Define the callback function that collects the file and reads it
@app.callback(
    Output('data-plot', 'figure'),
    Input('data-store',"data"),
    Input('x-axis-dropdown', 'value'),
    Input('y-axis-dropdown', 'value'),
    Input('fit-store', 'data'),

)
def update_figure(df, key_time, key_fluo, params):
            fig = go.Figure()

            fig.update_layout(
                    plot_bgcolor='white',  # Set the plot background color to white

                    xaxis=dict(showgrid=False),  # Hide the x-axis grid lines
                    yaxis=dict(showgrid=False),  # Hide the y-axis grid lines
)
            if df is None or key_time is None or key_fluo is None:
                return fig
            else:
                df = pd.DataFrame(df)
                
                X = df[key_time].values
                Y = df[key_fluo].values
                fig.add_trace(go.Scatter(
                    
                    x=df[key_time], 
                    y=df[key_fluo], 
                    name = "raw",
                    mode = "markers",
                    marker_color='rgba(152, 0, 0, .8)'
                    )
                )
                x_pred = np.linspace(X.min(), X.max(), 1024)
                y_pred = exp_decay(params, x_pred)
                fig.add_trace(go.Scatter(
                                x = x_pred, 
                                y=y_pred, 
                                name = "fit",
                                mode = "lines",
                                line_color = "rgba(0,0,0,0.6)"
                                )
                )
                fig.update_layout(
                    xaxis_title=key_time,  # Set the x-axis label
                    yaxis_title=key_fluo,  # Set the y-axis label
                )
                
                return fig


# Run the app
if __name__ == '__main__':
    app.run_server(debug=False)
