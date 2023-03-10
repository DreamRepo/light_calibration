<base target="_blank">

# Fluorescence to measure light intensity

This repository contains supplementary files and codes to complete the manuscript XXX:
- Simplified **online implementation of the code used to produce Figure 2** [here](https://github.com/DreamRepo/light_calibration/blob/main/notebooks/Dronpa2_video.ipynb)
- Simulations of the illumination used in Figure 2k,l [here](https://github.com/DreamRepo/light_calibration/tree/main/Macroscope)
- Simulation of 3D illumination pattern and comparison with 2D imaging [here](https://github.com/DreamRepo/light_calibration/tree/main/LED%20Array)
- Absorption and emission spectra of the actinometers [here](https://github.com/DreamRepo/light_calibration/tree/main/spectra_plotly)
- Implementation of the fitting algorithm for the fluorescence induction of microalgae [here](https://github.com/DreamRepo/light_calibration/blob/main/notebooks/PA_OJIP_rise_fit.ipynb)
- Metadata for the video acquisitions used to produce the main text figures [here](https://github.com/DreamRepo/light_calibration/tree/main/imaging_metadata)

The following section explains how to use the **online implementation**. 
## Summary
The manuscript XXX(to complete) describes methods to calibrate the intensity of a light source using various actinometers, and describe how to implement the protocols.


<p align="center">
<a> <img src="images/readme/image_mouette.png" width="700"></a>
</p>


 This repository contains an example code that can be run online to **analyze a light calibration video using Dronpa-2**. The code inputs the video and performs a pixel-per-pixel fit of a monoexponential. It maps a time constant associated to the time evolution of the fluorescence to each pixel in the image. The kinetic parameter $\sigma_{\lambda}$ allows to convert the time-constant map into an intensity map. As described in the supplementary information, we use the equation taking into account the thermal relaxation which intervenes when the light intensity is low: $I(x,y) = \frac{1-k^\Delta \tau}{\sigma_{\lambda} \tau(x,y)}$.  

<p align="center">
<a> <img src="images/readme/scheme.png" width="700"></a>
</p>


The repository also contains an app to visualize the time-evolution pixel-per-pixel by hovering the mouse over the image. 



**Input**: tiff video or folder with tiff images. (can be adapted to image set Python can handle)  
**Output**: 2D map of the light intensity (.csv/.pdf)
**Method**: pixel-per-pixel mono-exponential fit  






## Start

You can clone the repository to use the codes locally or launch it online with Binder. 

To launch Binder: click [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/DreamRepo/light_calibration/HEAD?labpath=notebooks%2FDronpa2_video.ipynb) (**Note**: the launching takes a few minutes and the session expires if unused)

To install locally: 
The requirement.txt file specifying the required packages and their versions is in the Binder folder. Python version 3.8.3, Conda version 22.11.1. The code has been tested on two Windows 10 installations. 

## Usage

Open the jupyter notebook **Notebooks/Dronpa2_video.ipynb**

*To execute a cell:* select the cell by clicking on it and press Shift+Enter to execute it.  

*Query bar:* enter the value and press Enter **or** press Enter to use the default value.

<p align="center">
<a> <img src="images/readme/2023-02-10-14-14-11.png" width="700"></a>
</p>


Start by testing the video provided in the repository to discover the code. Execute the cells using **Shift+Enter** and press **Enter** for all the queries, the default values will be used and are optimal for the video provided.  
**Note:** If you have difficulties executing the code, you can press the double arrow and press "yes" which will execute all the cells automatically and you will just need to press **Enter** for the queries so that the default values are used:

<p align="center">
<a> <img src="images/readme/2023-03-10-10-13-23.png" width="400"></a>
</p>
The demo should run in 2 minutes. 

To test the code with your own video, drag-and-drop it in the interface and type the file name in the query. Uploading the video online may take a few minutes. 

<p align="center">
<a> <img src="images/readme/2023-02-10-14-18-09.png" width="700"></a>
</p>

Follow the instructions in the notebook for the next queries. The $\sigma$ value corresponds to $\lambda_{exc} = 470$ nm.

## Results

The outputs are saved in the folder "images" and you can download them. The units are in $µE/m²/s$. 

<p align="center">
<a> <img src="images/readme/2023-02-10-14-25-55.png" width="700"></a>
</p>



## Explore

Open the code **Notebooks/display_curves.ipynb** accessible in the side bar. 
To visualize the time evolution and fits for each pixel, execute **cell-by-cell** the code. A new window will open and you can hover your mouse over the pixel to display the corresponding raw data and fits. The image can be cropped between a minimum and a maximum value to remove the fit outliers. 

If you are using a local implementation, you should use the **Notebooks/local_display_curves.py** instead of the Jupyter Notebook.


<p align="center">
<a> <img src="images/readme/2023-02-10-14-24-19.png" width="700"></a>
</p>


##### License

Alienor134/light_calibration is licensed under the GNU General Public License v3.0
