import matplotlib.pyplot as plt
import pandas as pd
import os

# Default style parameters
naptools_dir_path = os.path.dirname(os.path.realpath(__file__))
plt.style.use(naptools_dir_path + "/naptools_default.mplstyle")


# TODO -- Setup some default parameter choices for easily reading one, two, three, four
#         plots next to each other in a LaTeX document.


class BaseData:
    """Base class for holding and performing calculations on data"""

    def __init__(self, data_file_dict):
        self.data_file_dict = data_file_dict
        self.data_df_dict = {}

        # Populate dictionary of data
        for data_file_id, data_file in self.data_file_dict.items():
            data_df = pd.read_csv(data_file)
            self.data_df_dict[data_file_id] = data_df

    def print_data(self, data_df_id):
        print(self.data_df_dict[data_df_id])


class BasePlot:
    """Basic two-dimensional plot with one independent and one dependent variable.
    This class is also the basis for the other kinds of plots, featuring the general
    structure of: __init__(), draw(), output()."""

    def __init__(self, data):
        self.data = data

        # Default plotting parameters (alphabetical order)
        self.parameters = {
            "drop": [],
            "grid": False,
            "log-log": False,
            "semilog-x": False,
            "semilog-y": False,
            "suppress_legend": False,
            "x_label": None,
            "y_label": None,
        }

    def plot(self, independent_vars, dependent_vars, output_filename, parameters={}):
        """Plot the given independent and dependent variables"""
        self.parameters.update(parameters)
        self.output_filename = output_filename
        self.fig, self.axs = plt.subplots()

        for data_file, data_df in self.data.data_df_dict.items():
            data_df.plot(independent_vars, dependent_vars, ax=self.axs)

        self.output()

    def output(self):
        """Format and output plot to file"""
        plt.xlabel(self.parameters["x_label"])
        plt.ylabel(self.parameters["y_label"])
        
        self.resolve_parameters()
        # self.fig.tight_layout() #INCLUDED IN SAVEFIG BELOW

        os.makedirs(os.path.dirname(self.output_filename), exist_ok=True)
        plt.savefig(self.output_filename, bbox_inches="tight")
        plt.close()
        print(f"Results plotted as: {self.output_filename}")

    def resolve_parameters(self):
        """Act on parameter values to modify plot appearance"""
        if self.parameters["grid"]:
            plt.grid(which="both", color="#cfcfcf")

        if self.parameters["log-log"]:
            plt.xscale("log")
            plt.yscale("log")

        if self.parameters["semilog-x"]:
            plt.xscale("log")

        if self.parameters["semilog-y"]:
            plt.yscale("log")

        if not self.parameters["suppress_legend"]:
            plt.legend()
