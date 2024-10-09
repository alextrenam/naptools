import matplotlib.pyplot as plt
import pandas as pd
import re
import numpy as np
from naptools import Plot, LineStyles, utils


class ErrorPlot(Plot):
    """Class for creating error plots based on the underlying error data"""
    def __init__(self, data, name="default"):
        super().__init__(data, name)
        self.set_plotting_parameters()

    def set_plotting_parameters(self):
        """Set the default error plot parameters"""
        self.parameters["scale_axes"] = "log-log"
        self.parameters["y_label"] = "Error"
        self.parameters["include_slopes"] = True

    def get_convergence(self, name):
        """Returns a DataFrame of the convergence of the provided error data"""
        error_df = self.data[name]
        convergence_df = error_df.copy(deep=True)
        
        for i in range(error_df.shape[0] - 1):
            convergence_df.loc[i] = np.log2((error_df.loc[i]) / (error_df.loc[i + 1]))

        return convergence_df
    
    def print_convergence(self, name):
        """Print name and the associated convergence DataFrame."""
        # Calculate convergence rate table
        convergence_df = self.get_convergence(name)
        
        # Drop the final row before printing
        convergence_df.drop(convergence_df.tail(1).index, inplace=True)
        print(f"\n{name} convergence rates\n{convergence_df}\n")
    
