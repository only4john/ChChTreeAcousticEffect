Christchurch Urban Soundscape Analysis (基督城城市声景分析)
This repository contains the Python analysis scripts for the research project investigating the relationship between urban tree canopy structure (cover and volume) and acoustic indices across Christchurch, New Zealand. The analysis employs geospatial techniques, including Geographically Weighted Regression (GWR), to explore spatially varying relationships at multiple scales.

Overview 
This project aims to quantify the link between urban green infrastructure and the acoustic environment. By leveraging high-resolution LiDAR data and a comprehensive set of acoustic indices, we explore:

The spatial distribution and characteristics of key acoustic indices.

The presence of spatial autocorrelation in the acoustic data, justifying the use of local spatial models.

The spatially non-stationary relationships between tree canopy metrics and soundscapes using GWR.

The optimal scales of effect for different acoustic indices.

Data 
The core data for this analysis is expected to be in a GeoPackage file named soundIndices_all_final_values.gpkg with a layer named soundindices_final.

Note: The data file is not included in this repository due to its large size. Users are expected to prepare their own data according to the methodology described in the associated publication. The file should contain the geometry (points) along with fields for all acoustic indices, canopy cover metrics, and canopy volume metrics.

Installation 
This project uses a Conda environment to manage dependencies. To ensure reproducibility, an environment.yml file is provided.

Clone the repository:

git clone [https://github.com/YourUsername/christchurch-soundscape-analysis.git](https://github.com/YourUsername/christchurch-soundscape-analysis.git)
cd christchurch-soundscape-analysis

Create the Conda environment from the file:

conda env create -f environment.yml

Activate the environment before running any scripts:

conda activate sounding_env

Workflow & Usage 
The analysis is broken down into several scripts that should ideally be run in the following order:

1. Generate Descriptive Statistics & Histograms
This script provides an initial overview of the acoustic indices' distributions.

python descriptiveStats.py

2. Test for Spatial Autocorrelation
This script runs the Global Moran's I test to formally justify the need for a local spatial model like GWR.

python MoransI_test.py

3. Run the GWR Analysis
This is the main analysis script. Before running, you must edit the script to choose the analysis mode.

Open GWR_calculation.py.

Set the ANALYSIS_TYPE variable on line 18 to either 'cover' or 'volume'.

Run the script from the terminal:

python GWR_calculation.py

This will generate multiple .gpkg files containing the results for each scale and acoustic index.

4. Visualize Scale Effects
This script likely visualizes the results from the GWR analysis, for example, by plotting R² values across different scales.

python visualizeScaleEffects.py

Scripts Overview 
descriptiveStats.py: Calculates descriptive statistics and generates distribution histograms for the key acoustic indices (SPL, NDSI, etc.).

MoransI_test.py: Calculates the Global Moran's I statistic for each acoustic index to test for spatial autocorrelation.

GWR_calculation.py: The core analysis script. It iterates through multiple spatial scales and acoustic indices, performing GWR for each combination. It handles both canopy cover and canopy volume analyses.

visualizeScaleEffects.py: A script for creating visualizations from the GWR output files to help interpret the results, particularly the effect of spatial scale.

License 
This project is licensed under the MIT License. See the LICENSE file for details.