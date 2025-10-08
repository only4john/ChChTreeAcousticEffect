import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ==============================================================================
# --- 1. SETUP: Configure your file and indices here ---
# ==============================================================================

# MODIFIED: Set the path to your GeoPackage file and the specific layer name.
input_gpkg_path = 'soundIndices_all_final_values.gpkg'
layer_name = 'soundindices_final'

# The 5 core acoustic indices you want to plot
indices_to_plot = [
    'SPL',
    'FEQ',
    'ADI',
    'NDSI',
    'BIO'
]

# A professional, nature-inspired color palette
# (SPL-Blue, NDSI-Orange, FEQ-Green, BIO-Red, ADI-Purple)
palette = sns.color_palette("colorblind", 5)
color_map = dict(zip(indices_to_plot, palette))

# ==============================================================================
# --- 2. Data Loading and Preparation ---
# ==============================================================================

try:
    # MODIFIED: Reading data from the specified layer in the GeoPackage file.
    df = gpd.read_file(input_gpkg_path, layer=layer_name)
    print(f"Data successfully loaded from layer '{layer_name}' in '{input_gpkg_path}'.")
except FileNotFoundError:
    print(f"Error: File not found at '{input_gpkg_path}'. Please check the path and filename.")
    exit()
except Exception as e:
    print(f"An error occurred while reading the file: {e}")
    exit()

# Ensure only the desired columns exist and are numeric
# A GeoDataFrame can be used just like a pandas DataFrame for this part.
df_plot = df[indices_to_plot].apply(pd.to_numeric, errors='coerce').dropna()

print(f"Plotting histograms for {len(df_plot)} valid data points.")

# ==============================================================================
# --- 3. Create the Multi-Panel Plot ---
# ==============================================================================

# Create a 2x3 grid for the subplots
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
# Flatten the 2x3 axes array into a 1D array for easy iteration
axes = axes.flatten()

# Loop through each index and create a histogram on a subplot
for i, index_name in enumerate(indices_to_plot):
    ax = axes[i]
    data_series = df_plot[index_name]
    
    # Plot the histogram using seaborn for a nice aesthetic
    sns.histplot(
        data_series, 
        ax=ax, 
        kde=True, # Adds a smooth density line over the bars
        color=color_map[index_name],
        bins=30 # You can adjust the number of bins for more/less detail
    )
    
    # Add a vertical line for the mean value
    mean_val = data_series.mean()
    ax.axvline(mean_val, color='black', linestyle='--', linewidth=1.5, label=f'Mean: {mean_val:.2f}')
    
    # Set titles and labels for each subplot
    ax.set_title(f'Distribution of {index_name}', fontsize=14, weight='bold')
    ax.set_xlabel(f'{index_name} Value', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.legend()
    ax.grid(axis='y', linestyle=':', alpha=0.6)

# --- 4. Final Touches and Saving ---
# ==============================================================================

# Turn off the last, unused subplot
axes[-1].set_visible(False)

# Add a main title for the entire figure
# fig.suptitle('Distribution of Key Acoustic Indices Across the Study Area', fontsize=20, weight='bold')

# Adjust the layout to prevent titles/labels from overlapping
plt.tight_layout(rect=[0, 0, 1, 0.96]) # Adjust top margin for suptitle

# Save the figure to a high-resolution PNG file
output_filename = 'acoustic_indices_histograms.png'
plt.savefig(output_filename, dpi=300) # dpi=300 for publication quality
print(f"\nPublication-quality histogram plot saved as '{output_filename}'")

# Display the plot
plt.show()
