# ==========================================================
#
#  Unit tests
#
# ==========================================================
"""
This file implements unit tests for the NAPTools package.
The tests are as follows:


"""
import naptools as nap

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

# Base file testing
test_data = nap.BaseData(test_data_files)
# test_data.print_data("p4")

# test_plot = nap.BasePlot(test_data)
# test_plot.plot("h",
#                ["p L2", "n L2", "p H1", "n H1"],
#                "./results/error_plot_p1.pdf",
#                parameters={"log-log": True, "grid": True})

# Error data operations
error_data = nap.ErrorData(test_data_files)
error_data.update_norms(error_norms_dict)
error_data.print_degree("p2")

# Error plots
error_plots = nap.ErrorPlot(error_data)
error_plots.plot("h", ["p", "n", "psi"], "p1", "./results/error_plot_p1.pdf")
error_plots.plot("h", ["p", "n", "psi"], "p2", "./results/error_plot_p2.pdf")
error_plots.plot("h",
                 ["n", "psi"],
                 ["p1", "p2", "p3", "p4"],
                 "./results/error_plot_n_psi.pdf",
                 parameters=plotting_params)
error_plots.plot("h", "n", ["p1", "p2", "p3", "p4"], "./results/error_plot_n.pdf")


# The following code should work -- the aim is minimal code required to create plots
p_refinement_plot = nap.ErrorPlot("./data/p_refinement_errors.csv")
p_refinement_plot.plot("p", "u_L2", "./results/p_refinement_errors.pdf")

data_a = [0, 1, 2, 3, 4]
data_b = [i**2 for i in data_a]

nap.quick_plot(data_a, data_b, "./results/quick_plot.pdf")
