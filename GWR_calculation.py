import geopandas as gpd
import pandas as pd
from mgwr.gwr import GWR
from mgwr.sel_bw import Sel_BW
import numpy as np
import warnings
import threading
import time
import sys
import itertools

# --- Progress Indicator Function ---
def animate():
    """Displays a spinning cursor animation in the terminal."""
    global done
    for c in itertools.cycle(['|', '/', '-', '\\']):
        if done:
            break
        sys.stdout.write('\r' + c + ' Please wait... ')
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write('\rDone!                  \n')

# Suppress RuntimeWarning from numpy that may occur within mgwr
warnings.filterwarnings("ignore", category=RuntimeWarning)

# ==============================================================================
# --- 1. SETUP: Configure Your Analysis Here ---
# ==============================================================================

# --- Core Analysis Selection ---
ANALYSIS_TYPE = 'volume'  # Options: 'cover' or 'volume'

# --- Data File Paths ---
input_gpkg_path = 'soundIndices_all_final_values.gpkg'
layer_name = 'soundindices_final'

# --- Variable Definitions ---
# dependent_vars_list = ['SPL', 'FEQ', 'ACI', 'ADI', 'AEI', 'H', 'BIO', 'NDSI']
dependent_vars_list = ['SPL', 'NDSI', 'FEQ', 'BIO', 'ADI' ]


# ==============================================================================
# --- 2. Dynamic Setup (Script will auto-configure based on your selection) ---
# ==============================================================================

if ANALYSIS_TYPE == 'cover':
    print("--- Selected [Canopy Cover] Analysis Mode ---")
    explanatory_vars = ['Cover50', 'Cover100', 'Cover150', 'Cover200', 'Cover250', 'Cover300']
    output_prefix_base = 'gwr_lidar_cover'
elif ANALYSIS_TYPE == 'volume':
    print("--- Selected [Canopy Volume] Analysis Mode ---")
    explanatory_vars = ['volume50_mean', 'volume100_mean', 'volume150_mean', 'volume200_mean', 'volume250_mean', 'volume300_mean']
    output_prefix_base = 'gwr_lidar_volume'
else:
    print(f"Error: Invalid ANALYSIS_TYPE '{ANALYSIS_TYPE}'. Please choose 'cover' or 'volume'.")
    exit()

# ==============================================================================
# --- 3. Data Preparation ---
# ==============================================================================

print(f"Reading layer '{layer_name}' from file '{input_gpkg_path}'...")
try:
    gdf = gpd.read_file(input_gpkg_path, layer=layer_name)
    print("Data loaded successfully.")
    print(f"Original number of points: {len(gdf)}")
except Exception as e:
    print(f"Error reading file: {e}")
    exit()

# --- Forcefully converting data types to numeric to avoid errors ---
print("\nConverting data types to numeric...")
all_vars_to_convert = dependent_vars_list + explanatory_vars
for col in all_vars_to_convert:
    if col in gdf.columns:
        gdf[col] = pd.to_numeric(gdf[col], errors='coerce')

original_rows = len(gdf)
gdf.dropna(subset=all_vars_to_convert, inplace=True)
cleaned_rows = len(gdf)
if original_rows > cleaned_rows:
    print(f"Warning: Removed {original_rows - cleaned_rows} rows containing invalid data that could not be converted to numeric.")
print("Data type conversion complete.")


# ==============================================================================
# --- 4. Main Loop: Iterate Through Each Scale and Acoustic Index ---
# ==============================================================================

# Outer loop: Iterate through all spatial scales
for current_scale_var in explanatory_vars:
    scale_name = current_scale_var.replace('Cover', '').replace('Volume', '')

    print("\n" + "#"*60)
    print(f"# Processing spatial scale: {scale_name}m")
    print("#"*60)

    # --- 4a. Filter Data ---
    print(f"\nFiltering data for {scale_name}m scale...")
    if ANALYSIS_TYPE == 'cover':
        gdf_filtered = gdf[(gdf[current_scale_var] > 0.0) & (gdf[current_scale_var] < 1.0)].copy()
    else: # For volume
        gdf_filtered = gdf[gdf[current_scale_var] > 0.0].copy()

    if len(gdf_filtered) == 0:
        print(f"Warning: No data found matching the filter criteria for the {scale_name}m scale. Skipping.")
        continue
    
    # (Modified) Using the full filtered dataset
    print(f"Number of points for GWR: {len(gdf_filtered)}")

    coords = np.vstack((gdf_filtered.geometry.x, gdf_filtered.geometry.y)).T
    X = gdf_filtered[[current_scale_var]].values

    # Inner loop: Iterate through each acoustic index
    for dep_var in dependent_vars_list:
        short_name = dep_var
        
        print("\n" + "="*50)
        print(f"Starting analysis for: {short_name} (at {scale_name}m scale)")
        print("="*50)
        
        try:
            y = gdf_filtered[dep_var].values.reshape(-1, 1)
        except KeyError:
            print(f"Error: Column named '{dep_var}' not found in the data. Skipping.")
            continue

        # --- 4b. Find Optimal Bandwidth ---
        print(f"Searching for optimal bandwidth for {short_name}...")
        done = False
        t = threading.Thread(target=animate)
        t.start()
        try:
            selector = Sel_BW(coords, y, X, fixed=False) 
            bandwidth = selector.search()
            done = True
            t.join()
            print(f"--> Optimal bandwidth found: {bandwidth:.3f}")
        except Exception as e:
            done = True
            t.join()
            print(f"\nError during bandwidth search: {e}")
            continue

        # --- 4c. Run GWR Model ---
        print(f"Running GWR model...")
        done = False
        t = threading.Thread(target=animate)
        t.start()
        try:
            model = GWR(coords, y, X, bandwidth, fixed=False)
            results = model.fit()
            done = True
            t.join()
            print(f"--> GWR model fitting complete.")
        except Exception as e:
            done = True
            t.join()
            print(f"\nError during GWR model fitting: {e}")
            continue

        # --- 4d. Display and Save Results ---
        print(f"\n--- GWR Model Summary: {short_name} @ {scale_name}m ---")
        print(results.summary())
        
        # (Modified) Update output filename to reflect the use of the full dataset
        output_gpkg_path = f'{output_prefix_base}_{scale_name}_{short_name}_full.gpkg'
        print(f"\nSaving results to: {output_gpkg_path}")
        
        results_gdf = gdf_filtered.copy()
        results_gdf['local_R2'] = results.localR2
        results_gdf['y_pred'] = results.predy.flatten()
        results_gdf['residual'] = results.resid_response.flatten()
        results_gdf['coeff_intercept'] = results.params[:, 0]
        results_gdf[f'coeff_{current_scale_var}'] = results.params[:, 1]
        
        try:
            results_gdf.to_file(output_gpkg_path, driver='GPKG')
            print(f"--> Success! Results have been saved.")
        except Exception as e:
            print(f"Error saving results file: {e}")

print("\n" + "#"*60)
print("All analyses completed.")
print("#"*60)
