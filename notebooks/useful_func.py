import skimage
import numpy as np
import matplotlib.pyplot as plt

from scipy import optimize
from mpl_toolkits.axes_grid1 import make_axes_locatable
from joblib import delayed
from joblib import wrap_non_picklable_objects


save_folder = "../images/"
extension= ".pdf"

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
    parameters_estimated[1] /= sample_rate

    return parameters_estimated

@delayed
@wrap_non_picklable_objects
def parallel_tau(fluo, time_array, sample_rate):
    """monoexponential for joblib"""
    return  simple_tau(fluo, time_array, sample_rate)[1]
    

def plot_map(I_000, I_000_map, save_name, limits = (0,0)):
    """display the results"""
    
    #crop the outliers for correct scaling of the colormap
    if limits==(0,0):
        Q1 = np.quantile(I_000, 0.01)
        Q3 = np.quantile(I_000, 0.995)
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


def threshold_convert(filter_type):
    if filter_type == "skimage.filters.thresholding.threshold_isodata":
        filt = skimage.filters.thresholding.threshold_isodata
        
    if filter_type == "skimage.filters.thresholding.threshold_li":
        filt = skimage.filters.thresholding.threshold_li

    if filter_type == "skimage.filters.thresholding.threshold_mean":
        filt = skimage.filters.thresholding.threshold_mean
        
    if filter_type == "skimage.filters.thresholding.threshold_minimum":
        filt = skimage.filters.thresholding.threshold_minimum
        
    if filter_type == "skimage.filters.thresholding.threshold_otsu":
        filt = skimage.filters.thresholding.threshold_otsu
    if filter_type == "skimage.filters.thresholding.threshold_triangle":
        filt = skimage.filters.thresholding.threshold_triangle
    if filter_type == "skimage.filters.thresholding.threshold_yen":
        filt = skimage.filters.thresholding.threshold_yen
    if filter_type == "None":
        filt = lambda x:0
        
    return filt