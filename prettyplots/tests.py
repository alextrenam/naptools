import prettyplots as pp

# Here I should run check the functions perform as expected on some test data

test_data_files = {
    "p1": "./test_data/errors_p1.csv",
    "p2": "./test_data/errors_p2.csv",
    "p3": "./test_data/errors_p3.csv",
    "p4": "./test_data/errors_p4.csv",
    }

error_norms_dict = {
    "p L2": r"$|\!|\rho - \rho_h|\!|$",
    "n L2": r"$|\!|\nu - \nu_h|\!|$",
    "psi L2": r"$|\!|\psi - \psi_h|\!|$",
    "p H1": r"$|\!|\nabla\!\left(\rho - \rho_h\right)|\!|$",
    "n H1": r"$|\!|\nabla\!\left(\nu - \nu_h\right)|\!|$",
    "psi H1": r"$|\!|\nabla\!\left(\psi - \psi_h\right)|\!|$",
}

# Base file testing
test_data = pp.BaseData(test_data_files)
# test_data.print_data("p4")

# test_plot = pp.BasePlot(test_data)
# test_plot.plot("h",
#                ["p L2", "n L2", "p H1", "n H1"],
#                "./test_data/results/error_plot_p1.pdf",
#                parameters={"log-log": True, "grid": True})

# Error file testing
error_data = pp.ErrorData(test_data_files)
error_data.update_norms(error_norms_dict)
error_data.print_degree("p2")
error_plots = pp.ErrorPlot(error_data)
error_plots.plot_variable("n", "./test_data/results/error_plot_n.pdf")
error_plots.plot_degree("p2", "./test_data/results/error_plot_p2.pdf")
