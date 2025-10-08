import geopandas as gpd
from libpysal import weights
from esda.moran import Moran
import pandas as pd
import matplotlib.pyplot as plt

# ==============================================================================
# --- 1. SETUP: Please confirm your file path and variables ---
# ==============================================================================

# The full path to your final, joined data file
input_gpkg_path = 'soundIndices_all_final_values.gpkg'
# The name of the layer inside the GeoPackage file
layer_name = 'soundindices_final'

# The final list of 5 acoustic indices you want to analyze
acoustic_indices_to_test = [
    'SPL',
    'NDSI',
    'FEQ',
    'BIO',
    'ADI'
]

# ==============================================================================
# --- 2. DATA PREPARATION (No changes needed below) ---
# ==============================================================================

print(f"Reading layer '{layer_name}' from file '{input_gpkg_path}'...")
try:
    gdf = gpd.read_file(input_gpkg_path, layer=layer_name)
    print(f"Data successfully loaded with {len(gdf)} points.")
except Exception as e:
    print(f"Error reading file: {e}")
    exit()

# --- NEW: Data Cleaning - Convert columns to numeric type ---
print("\nVerifying and converting data types...")
for col in acoustic_indices_to_test:
    if col in gdf.columns:
        # Convert column to numeric, turning any non-numeric values into NaN (Not a Number)
        gdf[col] = pd.to_numeric(gdf[col], errors='coerce')
    else:
        print(f"Warning: Column '{col}' not found in the data.")
        
# Remove any rows that have NaN values in the columns we are testing
original_rows = len(gdf)
gdf.dropna(subset=acoustic_indices_to_test, inplace=True)
cleaned_rows = len(gdf)
if original_rows > cleaned_rows:
    print(f"Removed {original_rows - cleaned_rows} rows containing invalid non-numeric data.")
print("Data types successfully converted.")
# --- END OF NEW SECTION ---


# --- Create Spatial Weights Matrix ---
# For a regular grid like yours, using k=8 (K-Nearest Neighbors) is the standard
# method to define neighborhood, equivalent to "Queen's Contiguity".
print("\nCreating spatial weights matrix based on point locations (this may take a moment)...")
try:
    w = weights.KNN.from_dataframe(gdf, k=8)
    w.transform = 'r' # Row-standardize the weights matrix
    print("Spatial weights matrix created successfully.")
except Exception as e:
    print(f"Error creating spatial weights matrix: {e}")
    exit()

# ==============================================================================
# --- 3. MAIN LOOP: Calculate Moran's I for each index ---
# ==============================================================================

print("\nCalculating Global Moran's I for each acoustic index...")
results_data = []

for var_name in acoustic_indices_to_test:
    short_name = var_name
    
    try:
        y = gdf[var_name]
        # Calculate Moran's I using 999 permutations for a robust p-value
        moran = Moran(y, w, permutations=999)
        
        # Store results for the table
        results_data.append({
            'Acoustic Index': short_name,
            "Moran's I": moran.I,
            'Z-score': moran.z_sim,
            'P-value': moran.p_sim
        })
        
    except KeyError:
        print(f"  ERROR: Column '{var_name}' not found in the data. Skipped.")
    except Exception as e:
        print(f"  ERROR calculating Moran's I for {short_name}: {e}")

# ==============================================================================
# --- 4. Create and Save Results Table ---
# ==============================================================================

if not results_data:
    print("\nNo results were generated. Exiting.")
    exit()

# Create a pandas DataFrame from the results
results_df = pd.DataFrame(results_data)
results_df = results_df.set_index('Acoustic Index')

# Print the results table to the console
print("\n" + "="*55)
print("           Global Moran's I Results Summary")
print("="*55)
print(results_df.round(4))
print("="*55)

# --- Create and save the table as an image ---
fig, ax = plt.subplots(figsize=(8, 3))
ax.axis('tight')
ax.axis('off')

# Format the data for the table, ensuring p-values are displayed correctly
cell_text = []
for index, row in results_df.iterrows():
    p_val_text = f"< 0.001" if row['P-value'] <= 0.001 else f"{row['P-value']:.3f}"
    # --- THIS IS THE FIX ---
    # Get the value into a simple variable first
    moran_i_val = row["Moran's I"] 
    # Now use the simple variable in the f-string
    cell_text.append([f"{moran_i_val:.4f}", f"{row['Z-score']:.2f}", p_val_text])
    # --- END OF THE FIX ---

the_table = ax.table(
    cellText=cell_text,
    colLabels=["Moran's I", "Z-score", "P-value"],
    rowLabels=results_df.index,
    loc='center',
    cellLoc='center'
)

# Style the table
the_table.auto_set_font_size(False)
the_table.set_fontsize(12)
the_table.scale(1.2, 1.8)

for (row, col), cell in the_table.get_celld().items():
    if (row == 0) or (col == -1):
        cell.set_text_props(weight='bold')

# Add Title and Save
plt.title("Table X: Global Spatial Autocorrelation of Acoustic Indices", fontsize=14, weight='bold', pad=20)
output_filename = 'morans_i_final_table.png'
plt.savefig(
    output_filename, 
    dpi=300, 
    bbox_inches='tight',
    pad_inches=0.4
)
print(f"\nPublication-quality table saved as '{output_filename}'")

