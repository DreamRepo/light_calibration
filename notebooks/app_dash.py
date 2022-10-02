from jupyter_dash import JupyterDash
import dash
from dash import dcc
from dash import html
from dash.dependencies import Output, Input
import plotly.express as px
import chart_studio.plotly as py
import plotly.graph_objects as go
from plotly.subplots import make_subplots


import numpy as np
import matplotlib.pyplot as plt
from scipy import optimize
import os
import glob

from statsmodels.regression import linear_model
from statsmodels.api import add_constant

from mpl_toolkits.axes_grid1 import make_axes_locatable

from skimage.transform import rescale, resize, downscale_local_mean
import skimage
from scipy.ndimage import binary_erosion

from joblib import Parallel, delayed
from joblib import wrap_non_picklable_objects

import tifffile as tiff
from tqdm import tqdm



sigma_480 = 198 #m2/mol
sigma_405 = 415 #m2/mol
tau_relax = 0.014


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

initial = np.ones((10,10))
fig_init = px.imshow(initial)


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


def simple_tau(fluo, time_array, sample_rate):
    """perform monoexponential fit"""
    L = len(time_array) 
    fluo_transition = fluo
    time_transition = np.linspace(0, L - 1, L)
    x0 = [1e5, L/8, 1]
    OptimizeResult  = optimize.least_squares(residuals,  x0, bounds = (-1e9,1e9),
                                        args = (time_transition, fluo_transition, exp_decay))
    parameters_estimated = OptimizeResult.x
    tau = parameters_estimated[1]

    #conditions on tau too low or too high for the second, more accurate, fit, because we will fit on a signal that lasts 5*tau
    if tau >  L//10: #if too high
        tau =  L//10
    if tau < 3: #if too low, increase it
        tau = 5
    x0 = parameters_estimated #initial guess: parameters from previous fit
    #second fit
    OptimizeResult  = optimize.least_squares(residuals,  x0, bounds = (-1e9,1e9),
                                        args = (time_transition[0:int(tau*5)], fluo_transition[0: int(tau*5)], exp_decay))
    parameters_estimated = OptimizeResult.x
    
    if False:
        plt.figure()
        plt.plot(time_transition, fluo_transition, 'o')
        plt.plot(time_transition, exp_decay(parameters_estimated, time_transition))
    #parameters_estimated[1] /= sample_rate

    return parameters_estimated

@delayed
@wrap_non_picklable_objects
def parallel_tau(fluo, time_array, sample_rate):
    """monoexponential for joblib"""
    return  simple_tau(fluo, time_array, sample_rate)[1]
    

def plot_map(I_000, I_000_map, save_name, save_folder, limits = (0,0)):
    """display the results"""
    
    #crop the outliers for correct scaling of the colormap
    if limits==(0,0):
        Q1 = np.quantile(I_000, 0.01)
        Q3 = np.quantile(I_000, 0.95)
    else: 
        Q1 = limits[0]
        Q3 = limits[1]
    I_000_map[I_000_map <= Q1 ] = Q1
    I_000_map[I_000_map >= Q3 ] = Q3
    
    
    #map of intensities
    f = plt.figure()
    image = plt.imshow((I_000_map))
    plt.axis("off")
    divider = make_axes_locatable(plt.gca())
    axdef = divider.append_axes("bottom", "5%", pad="3%")
    cbar = plt.colorbar(image, cax=axdef, orientation = "horizontal")
    f.tight_layout()
    plt.savefig(save_folder + "/" +save_name)
    
    
    # histogram of intensities
    I_000_distrib = I_000[(I_000>Q1)*(I_000<Q3)].flatten()

    fig = plt.figure()
    ax = plt.gca()
    
    plt.xlabel(r"Light intensity ($\mu Eins /m^2/s$)")
    plt.ylabel("")
    ax.tick_params(axis='both', which='major', direction = 'in', top = True, right = True)
    _, bins, _ = plt.hist(I_000_distrib, 15, density= False, alpha=1, facecolor = "white", edgecolor = "black")

    plt.savefig(save_folder + "/hist_" + save_name)
    
    np.savetxt(save_folder + "/" + save_name + ".csv", I_000_map, delimiter=",")


    return I_000_map, I_000_distrib

def create_distribution(I_map):
    fig = px.imshow(I_map)
    fig.update_traces(hovertemplate="x: %{x} <br> y: %{y} <br> z: %{z}")
    #fig.update_layout(coloraxis=dict(colorbar=dict(orientation='h')))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig

def create_trace(time, trace, framerate, log = False):
    params = simple_tau(trace, time, sample_rate = framerate)
    y = exp_decay(params, time)
    time = time/framerate
    if log==True: 
        y = np.log(y)
        trace = np.log(trace)
    trace1 = go.Scatter(
        mode = "markers",
        x=time,
        y=trace,
        name="raw",
        marker=dict(
            color='rgb(34,163,192)'
                   )
    )
    trace2 = go.Scatter(
        x=time,
        y=y,
        name='fit',)

    fig_trace = make_subplots()
    fig_trace.add_trace(trace1)
    fig_trace.add_trace(trace2)    
    fig_trace.add_annotation(x=0, y=0.85, xanchor='left', yanchor='bottom',
                       xref='paper', yref='paper', showarrow=False, align='left', text = "",
                       )
    fig_trace.update_layout(plot_bgcolor='rgba(255,255,255,1)')
    return fig_trace




layout = html.Div([
        html.Div([            
            html.Label("Framerate"),
            dcc.Input(value= 3, type='number', id="framerate"),
        ], style={'display': 'flex', "flex-direction":"row", 'width':'5%'}
        ),
        html.Div([

            dcc.Graph(id="distribution", figure = fig_init),
            dcc.Graph(id="trace", figure = fig_init),

        ],
        style={'width': '49%', 'display': 'flex'}),
]
)



    