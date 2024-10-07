import matplotlib.pyplot as plt
import pandas as pd
import re
import numpy as np
from scipy import stats
from naptools import Plot, LineStyles, get_loglog_slope


class ErrorPlot(Plot):
    """Class for creating error plots based on the underlying error data"""
    def __init__(self, data, name="default"):
        super().__init__(data, name)
        self.error_norms_dict = {}
        self.set_plotting_parameters()

    def set_plotting_parameters(self):
        """Set the default error plot parameters"""
        self.parameters["log-log"] = True
        self.parameters["x_label"] = "$h$"
        self.parameters["y_label"] = "Error"

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
            
    def plot(self, output_filename, independent_var=None, dependent_vars=None, names=None, parameters={}):
        """Plot the errors for the given variables at the given polynomial degrees"""
        self.parameters.update(parameters)
        self.output_filename = output_filename
        self.fig, self.axs = plt.subplots()
        
        if type(dependent_vars) is str:
            dependent_vars = [dependent_vars]
            
        if type(data_ids) is str:
            names = [names]
        
        # line_styles = LineStyles(self.data, dependent_var, names,
        #                          drop=self.parameters["drop"],
        #                          custom_style_dict=self.parameters["custom_style_dict"])
        # styles = line_styles.line_styles_by_degree()
        # colours = line_styles.colours_by_degree()
        # style_degree_index = 0
        
        for error_df in [self.data[name] for name in names]:
            plotting_df = error_df.set_index(independent_var)
            plotting_df.drop(
                axis=1,
                labels=self.parameters["drop"],
                inplace=True,
            )

            renaming_columns = {}

            if self.parameters["include_slopes"]:
                for dependent_var in dependent_vars:
                    slope = get_loglog_slope(error_df[independent_var], error_df[dependent_var])
                    
                    # Relabel the columns to the correct LaTeX norm notation
                    columns[dependent_var] = f"{dependent_var}, EOC: {slope:.3f}"
                
            # Rename columns for correct plot labels
            plotting_df.rename(columns=renaming_columns, inplace=True)

            # Create plot
            # plotting_df.plot(ax=self.axs, style=list(styles[style_degree_index]), color=list(colours[style_degree_index]))
            plotting_df.plot(ax=self.axs)
            # style_degree_index += 1

        self.output()

