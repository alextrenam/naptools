# ==========================================================
#
#  Unit tests
#
# ==========================================================
"""
This file implements unit tests for the NAPTools package.
The tests are as follows:

1. Creating a Plot instance from various data sources
2. Adding, editing, and removing data from a Plot instance
3. 
"""
import naptools as nap
import numpy as np
import pandas as pd

# Here I should run check the functions perform as expected on some test data


test_data_files = {
    "p1": "./data/errors_p1.csv",
    "p2": "./data/errors_p2.csv",
    "p3": "./data/errors_p3.csv",
    "p4": "./data/errors_p4.csv",
    }

error_norms_dict = {
    "p L2": r"$|\!|\rho - \rho_h|\!|$",
    "n L2": r"$|\!|\nu - \nu_h|\!|$",
    "psi L2": r"$|\!|\psi - \psi_h|\!|$",
    "p H1": r"$|\!|\nabla\!\left(\rho - \rho_h\right)|\!|$",
    "n H1": r"$|\!|\nabla\!\left(\nu - \nu_h\right)|\!|$",
    "psi H1": r"$|\!|\nabla\!\left(\psi - \psi_h\right)|\!|$",
}

plotting_params = {
    "custom_style_dict": {"marker": "degree", "colour": "variable", "line": "norm"}
}

# # Base file testing
# test_data = nap.BaseData(test_data_files)
# # test_data.print_data("p4")

# # test_plot = nap.BasePlot(test_data)
# # test_plot.plot("h",
# #                ["p L2", "n L2", "p H1", "n H1"],
# #                "./results/error_plot_p1.pdf",
# #                parameters={"log-log": True, "grid": True})

# # Error data operations
# error_data = nap.ErrorData(test_data_files)
# error_data.update_norms(error_norms_dict)
# error_data.print_degree("p2")

# # Error plots
# error_plots = nap.ErrorPlot(error_data)
# error_plots.plot("h", ["p", "n", "psi"], "p1", "./results/error_plot_p1.pdf")
# error_plots.plot("h", ["p", "n", "psi"], "p2", "./results/error_plot_p2.pdf")
# error_plots.plot("h",
#                  ["n", "psi"],
#                  ["p1", "p2", "p3", "p4"],
#                  "./results/error_plot_n_psi.pdf",
#                  parameters=plotting_params)
# error_plots.plot("h", "n", ["p1", "p2", "p3", "p4"], "./results/error_plot_n.pdf")


# # The following code should work -- the aim is minimal code required to create plots
# p_refinement_plot = nap.ErrorPlot("./data/p_refinement_errors.csv")
# p_refinement_plot.plot("p", "u_L2", "./results/p_refinement_errors.pdf")

data_a = [0, 1, 2, 3, 4]
data_b = [i**2 for i in data_a]

data = [data_a, data_b]

plot = nap.Plot(data)
plot_2 = nap.Plot(test_data_files)

# ==========================================================
#
#  Data handling
#
# ==========================================================
# Initialize the store with a dictionary of CSV files

data_store = nap.Plot({
    "data1": "./data/errors_p1.csv",
    "data2": "./data/errors_p2.csv",
    }, name="from_dict")

# Add a dictionary of datasets: numpy arrays, lists, or DataFrames
data_store.add_data({
    "random_data": np.random.rand(5, 3), 
    "list_data": [[1, 2, 3], [4, 5, 6]],
    "existing_df": pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
}, name="dataset_collection")

# Access stored DataFrames
print(data_store.get_data("random_data"))  # First numpy array dataset
print(data_store.get_data("data2"))  # CSV data if the file exists
print(data_store.get_data("list_data"))  # CSV data if the file exists

# List all stored DataFrames
print(data_store.list_data())

# ==========================================================
#
#  Plotting
#
# ==========================================================
data_store.plot("./results/test_output.pdf", names="list_data")

params = {
    "drop": ["Time taken"],
}

data_store.plot("./results/test_output_2.pdf", names="data2", ind_var="h", dep_vars=["psi L2", "p H1"], parameters=params)


a = np.array([1, 2, 3, 4, 5])
b = a**2
c = a**3

data_dict = {
    "x^2": b,
    "x^3": c,
}

plot = nap.Plot(data_dict)

# plot.update_labels("default_0", "x^2")
# plot.update_labels("default_1", "x^3")
plot.plot("./results/dummy.pdf")

nap.power.plot(a=a, b=b, c=c, output_filename="./results/power_plot.png")
