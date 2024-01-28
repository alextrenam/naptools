import prettyplots as pp

# Here I should run check the functions perform as expected on some test data

test_data_files = [
    "./test_data/errors_p1.csv",
    "./test_data/errors_p2.csv",
    # "./test_data/errors_p3.csv",
    # "./test_data/errors_p4.csv",
    ]

# Base file testing
test_data = pp.BaseData(*test_data_files)
# test_data.print_data("./test_data/errors_p1.csv")

test_plot = pp.BasePlot(test_data)
test_plot.plot("h",
               ["p L2", "n L2", "p H1", "n H1"],
               "./test_data/results/error_plot_p1.pdf",
               parameters={"log-log": True, "grid": True})

# Error file testing
# error_data = pp.ErrorData(*test_data_files)
