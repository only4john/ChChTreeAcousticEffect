import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

# ==============================================================================
# --- 1. Data Setup (Final LiDAR-based results) ---
# ==============================================================================

# GWR R² values for the Tree Cover analysis
data_cover = {
    '50m':  [0.039, 0.082, 0.069, 0.044, 0.064, 0.053, 0.010, 0.064],
    '100m': [0.063, 0.091, 0.086, 0.059, 0.083, 0.073, 0.013, 0.083],
    '150m': [0.064, 0.108, 0.089, 0.054, 0.082, 0.067, 0.009, 0.082],
    '200m': [0.069, 0.118, 0.097, 0.053, 0.088, 0.068, 0.011, 0.088],
    '250m': [0.069, 0.118, 0.105, 0.058, 0.092, 0.077, 0.010, 0.092],
    '300m': [0.065, 0.140, 0.118, 0.055, 0.094, 0.077, 0.009, 0.094]
}

data_volume = {
    '50m':  [0.042, 0.077, 0.069, 0.042, 0.061, 0.053, 0.010, 0.061],
    '100m': [0.062, 0.095, 0.087, 0.055, 0.080, 0.072, 0.012, 0.080],
    '150m': [0.063, 0.102, 0.092, 0.048, 0.078, 0.065, 0.010, 0.080],
    '200m': [0.070, 0.117, 0.098, 0.059, 0.087, 0.067, 0.010, 0.086],
    '250m': [0.069, 0.119, 0.105, 0.058, 0.091, 0.076, 0.009, 0.091],
    '300m': [0.068, 0.137, 0.118, 0.056, 0.093, 0.076, 0.009, 0.093]
}


indices = ['SPL', 'NDSI', 'FEQ', 'BIO', 'ADI', 'H', 'ACI', 'AEI']
# (MODIFIED) Only these 5 indices will be plotted
indices_to_plot = ['SPL', 'NDSI', 'FEQ', 'BIO', 'ADI']

# Create and transpose DataFrames
df_cover = pd.DataFrame(data_cover, index=indices).T
df_cover.index = [50, 100, 150, 200, 250, 300]

df_volume = pd.DataFrame(data_volume, index=indices).T
df_volume.index = [50, 100, 150, 200, 250, 300]

# Define line styles and colors
style_map = {
    'SPL':  {'color': '#1f77b4', 'marker': 'o'}, 'NDSI': {'color': '#ff7f0e', 'marker': 'o'},
    'FEQ':  {'color': '#2ca02c', 'marker': 's'}, 'BIO':  {'color': '#d62728', 'marker': 's'},
    'ADI':  {'color': '#9467bd', 'marker': '^'}
}

# ==============================================================================
# --- 2. Plotting (Two subplots) ---
# ==============================================================================
# (MODIFIED) Reduced figsize width and set wspace to bring plots closer
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8), sharey=True, gridspec_kw={'wspace': 0.05})


# --- Plot 1: Tree Cover ---
for index_name in indices_to_plot:
    style = style_map.get(index_name)
    ax1.plot(df_cover.index, df_cover[index_name], marker=style['marker'], color=style['color'], label=index_name, linewidth=2)

# (MODIFIED) Simplified title
ax1.set_title('Tree Cover', fontsize=18, pad=10)

# --- Plot 2: Tree Volume ---
for index_name in indices_to_plot:
    style = style_map.get(index_name)
    ax2.plot(df_volume.index, df_volume[index_name], marker=style['marker'], color=style['color'], label=index_name, linewidth=2)

# (MODIFIED) Simplified title
ax2.set_title('Tree Volume', fontsize=18, pad=10)

# ==============================================================================
# --- 3. Formatting and Fixed Highlighting ---
# ==============================================================================

# --- MODIFIED: Fixed highlight coloring ---
red_color = '#d62728'
blue_color = '#1f77b4'
orange_color = '#ff7f0e'

for ax in [ax1, ax2]:
    ax.axvspan(80, 120, color=red_color, alpha=0.15, zorder=0)
    ax.axvspan(200, 250, color=blue_color, alpha=0.15, zorder=0)
    ax.axvspan(280, 320, color=orange_color, alpha=0.15, zorder=0)

# Apply common formatting to both subplots
for ax in [ax1, ax2]:
    ax.set_xlabel('Spatial Scale (Buffer Radius in meters)', fontsize=12, labelpad=10)
    ax.set_xticks([50, 100, 150, 200, 250, 300])
    ax.tick_params(axis='both', which='major', labelsize=11)
    ax.grid(True, which='both', linestyle=':', linewidth=0.7)
    ax.set_axisbelow(True)

ax1.set_ylabel('GWR R² (Explanatory Power)', fontsize=12, labelpad=10)

# --- (MODIFIED) Create a single, shared, grouped legend for the 5 indices ---
handles, labels = ax1.get_legend_handles_labels()
handles_labels_dict = dict(zip(labels, handles))

# Dummy handles for titles and zones
title_handle = Line2D([0], [0], color='none', label='')
zone_a = plt.Rectangle((0,0), 1, 1, color=red_color, alpha=0.2)
zone_b = plt.Rectangle((0,0), 1, 1, color=blue_color, alpha=0.2)
zone_c = plt.Rectangle((0,0), 1, 1, color=orange_color, alpha=0.2)

# Define groups
group1_title = "Fundamental \nMetrics"
group1_items = ['SPL', 'NDSI']
group2_title = "Bioacoustic \nCharacteristics"
group2_items = ['FEQ', 'BIO']
group3_title = "Ecological \nHealth" # Renamed group
group3_items = ['ADI']
highlight_title = "Optimal Scale"

# Build legend elements
legend_elements = [title_handle]
legend_labels = [group1_title]
for item in group1_items:
    legend_elements.append(handles_labels_dict[item])
    legend_labels.append(item)

legend_elements.extend([title_handle, title_handle])
legend_labels.extend(["", group2_title])
for item in group2_items:
    legend_elements.append(handles_labels_dict[item])
    legend_labels.append(item)
    
legend_elements.extend([title_handle, title_handle])
legend_labels.extend(["", group3_title])
for item in group3_items:
    legend_elements.append(handles_labels_dict[item])
    legend_labels.append(item)

legend_elements.extend([title_handle, title_handle, zone_a, zone_b, zone_c])
legend_labels.extend(["", highlight_title, "Local", "Neighbour", "Landscape"])

legend = fig.legend(
    handles=legend_elements,
    labels=legend_labels,
    bbox_to_anchor=(0.99, 0.85), 
    loc="upper right",
    fontsize=11,
    title="Legend",
    title_fontsize=13
)
for text in legend.get_texts():
    if text.get_text() in [group1_title, group2_title, group3_title, highlight_title]:
        text.set_weight('bold')
        text.set_size(12)

# ==============================================================================
# --- 4. Save and Show the Plot ---
# ==============================================================================

plt.subplots_adjust(right=0.87)
# (MODIFIED) Adjusted the right margin to bring the legend closer


output_filename = 'gwr_r2_comparison_final.png'
plt.savefig(output_filename, dpi=300) # dpi=300 for high resolution
print(f"Publication-quality chart saved as '{output_filename}'")

plt.show()