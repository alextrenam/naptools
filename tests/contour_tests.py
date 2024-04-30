import naptools as nap

# ============================================================================
#
# Get data
#
# ============================================================================
data_files = {
    "0002": "./data/u_0002.csv",
    "0005": "./data/u_0005.csv",
}

contour_data = nap.ContourData(data_files)
contour_data.print_data("0002")
# ============================================================================
#
# Custom plotting parameters
#
# ============================================================================
single_plotting_params = {
    "y_label": "$v$",
}

condition_1 = "(x > 0.0) & (y < 0.0)"
condition_2 = "(x < 0.0) & (y > 0.0)"
condition_3 = "((2.0 * x)**2 + (y)**2 < 0.5)"

mask_conditions = (
    condition_1 + " | "
    + condition_2 + " | "
    + condition_3
)

series_plotting_params = {
    "y_label": "$v$",
    "separate_colour_bar": True,
    "individual_colour_bar": True,
    "symlognorm_linear_width": 0.1,
    "colour_bar_location": "right",
    "mask_conditions": mask_conditions,
}
# ============================================================================
#
# Outputs
#
# ============================================================================
contour_plot = nap.ContourPlot(contour_data)

contour_plot.plot("u",
                  ["0002"],
                  "./results/u_contour.pdf",
                  parameters=single_plotting_params)

contour_plot.plot("u",
                  list(data_files.keys()),
                  "./results/u_contour.pdf",
                  parameters=series_plotting_params,
                  )
