import matplotlib.pyplot as plt
import pandas as pd
import re
import numpy as np
from scipy import stats
from naptools import BaseData, BasePlot, LineStyles


class ErrorData(BaseData):
    """Class for holding and performing calculations on error data"""
    def __init__(self, data_file_dict):
        super().__init__(data_file_dict)
        self.error_df_dict = self.data_df_dict
        self.error_norms_dict = {}

    def update_norms(self, error_norms_dict, custom_style_dict={}):
        """Update LaTeX norm notation."""
        self.error_norms_dict = error_norms_dict
        
    def get_convergence(self, degree_id):
        """Returns a DataFrame of the convergence of the provided error data"""
        error_df = self.error_df_dict[degree_id]
        convergence_df = error_df.copy(deep=True)
        
        for i in range(error_df.shape[0] - 1):
            convergence_df.loc[i] = np.log2((error_df.loc[i]) / (error_df.loc[i + 1]))

        return convergence_df

    def print_degree(self, degree_id):
        """Prints error and convergence tables in human-readable format"""
        # Print error table
        print("\033[2;31;43m  ERROR VALUES \033[0;0m")
        print(self.error_df_dict[degree_id])

        # Calculate convergence rate table
        convergence_df = self.get_convergence(degree_id)
        
        # Drop the final row before printing
        convergence_df.drop(convergence_df.tail(1).index, inplace=True)
        print("\033[2;31;43m  CONVERGENCE RATES \033[0;0m")
        print(convergence_df)
            
    
class ErrorPlot(BasePlot):
    """Class for creating error plots based on the underlying error data"""
    def __init__(self, error_data):
        super().__init__(error_data)
        self.error_data = self.data
        self.set_plotting_parameters()

    def set_plotting_parameters(self):
        """Set the default error plot parameters"""
        self.parameters["log-log"] = True
        self.parameters["x_label"] = "$h$"
        self.parameters["y_label"] = "Error"

    def get_loglog_slope(self, independent_var, dependent_var, all_data=False):
        """Returns the expected order of convergence (slope of the graph)
        -- either averaged over the curve, or just the final segment"""
        if all_data:
            # Calculate line slope for showing convergence rates on plot
            slope = stats.linregress(np.log2(independent_var),
                                     np.log2(dependent_var))[0]

        else:
            # Slope calculation using only the final two values
            slope = stats.linregress(np.log2(independent_var[-2:]),
                                     np.log2(dependent_var[-2:]))[0]

        return slope
                
    def plot(self, independent_var, dependent_vars, data_ids, output_filename, parameters={}):
        """Plot the errors for the given variables at the given polynomial degrees"""
        self.parameters.update(parameters)
        self.output_filename = output_filename
        self.fig, self.axs = plt.subplots()
        
        if type(dependent_vars) is str:
            dependent_vars = [dependent_vars]
            
        if type(data_ids) is str:
            data_ids = [data_ids]
            
        relevant_error_dfs = [self.error_data.error_df_dict[data_id] for data_id in data_ids]
        relevant_error_dfs_dict = dict(zip(data_ids, relevant_error_dfs))

        line_styles = LineStyles(self.data, dependent_vars, data_ids,
                                 drop=self.parameters["drop"],
                                 custom_style_dict=self.parameters["custom_style_dict"])
        styles = line_styles.line_styles_by_degree()
        colours = line_styles.colours_by_degree()
        style_degree_index = 0
        
        for error_df_id, error_df in relevant_error_dfs_dict.items():
            # Remove unnecessary columns from DataFrame
            plotting_df = error_df.set_index(independent_var)
            columns_to_drop = []

            for column in plotting_df.columns:
                # Assuming the ID is of the form "variable norm"
                variable = column.split(" ")[0]
                norm = column.split(" ")[1]
                
                if variable not in dependent_vars:
                    columns_to_drop.append(column)
                     
            plotting_df.drop(
                axis=1,
                labels=columns_to_drop + self.parameters["drop"],
                inplace=True,
            )

            renaming_columns = {}
            
            for error, error_norm in self.error_data.error_norms_dict.items():
                slope = self.get_loglog_slope(error_df[independent_var], error_df[error])

                # Relabel the columns to the correct LaTeX norm notation
                renaming_columns[error] = f"{error_df_id}, " + fr"{error_norm}, " + f"EOC: {slope:.3f}"
                
            # Rename columns for correct plot labels
            plotting_df.rename(columns=renaming_columns, inplace=True)

            # Create plot
            plotting_df.plot(ax=self.axs, style=list(styles[style_degree_index]), color=list(colours[style_degree_index]))
            style_degree_index += 1

        self.output()

