import matplotlib.pyplot as plt
import pandas as pd
import re
import numpy as np
from scipy import stats
from prettyplots import BaseData, BasePlot


class ErrorData(BaseData):
    """Class for holding and performing calculations on error data"""
    def __init__(self, data_file_dict):
        super().__init__(data_file_dict)
        self.error_df_dict = self.data_df_dict
        self.error_norms_dict = {}

    def update_norms(self, error_norms_dict, custom_style_dict={}):
        """Update LaTeX norm notation"""
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

    def plot_degree(self, degree_id, output_filename, parameters={}):
        """Plot all errors for a single polynomial degree"""
        self.parameters.update(parameters)
        self.output_filename = output_filename
        self.fig, self.axs = plt.subplots()
        error_df = self.error_data.error_df_dict[degree_id]
        line_styles = self.get_line_styles(degree_id=degree_id)
        line_colours = [line_styles_degree[1] for line_styles_degree in line_styles][0]
        line_styles = [line_styles_degree[0] for line_styles_degree in line_styles][0]
        
        # Remove unnecessary columns from DataFrame
        plotting_df = error_df.set_index("h")

        plotting_df.drop(
            axis=1,
            labels=["Time taken"],
            inplace=True,
        )
    
        renaming_columns = {}
        
        for error, error_norm in self.error_data.error_norms_dict.items():
            # Calculate line slope for showing convergence rates on plot
            slope = stats.linregress(np.log2(error_df["h"]), np.log2(error_df[error]))[0]

            # Relabel the columns to the correct LaTeX norm notation
            renaming_columns[error] = fr"{error_norm}" + f", Slope (EOC): {slope:.3f}"
        
        # Rename columns for correct plot labels
        plotting_df.rename(
            columns=renaming_columns,
            inplace=True,
        )

        # Create plot
        plotting_df.plot(ax=self.axs, style=line_styles, color=line_colours)
        self.output()
    
    def plot_variable(self, variable, output_filename, parameters={}):
        """Plot errors of all polynomial degree for the given variable"""
        self.parameters.update(parameters)
        self.output_filename = output_filename
        self.fig, self.axs = plt.subplots()
        
        line_styles = self.get_line_styles(variable=variable)
        line_colours = [line_styles_degree[1] for line_styles_degree in line_styles]
        line_styles = [line_styles_degree[0] for line_styles_degree in line_styles]

        for error_df_id, error_df in self.error_data.error_df_dict.items():
            # Remove unnecessary columns from DataFrame
            plotting_df = error_df.set_index("h")
            columns_to_drop = []

            for col in plotting_df.columns:
                if variable + " " not in col:
                    columns_to_drop.append(col)
            
            plotting_df.drop(
                axis=1,
                labels=["Time taken"] + columns_to_drop,
                inplace=True,
            )

            renaming_columns = {}
            
            for error, error_norm in self.error_data.error_norms_dict.items():
                # Calculate line slope for showing convergence rates on plot
                slope = stats.linregress(np.log2(error_df["h"]), np.log2(error_df[error]))[0]
                
                # Relabel the columns to the correct LaTeX norm notation
                renaming_columns[error] = f"{error_df_id}, " + fr"{error_norm}, " + f"EOC: {slope:.3f}"
                
            # Rename columns for correct plot labels
            plotting_df.rename(
                columns=renaming_columns,
                inplace=True,
            )

            # Create plot
            style_degree_index = int(re.findall(r"\d+", error_df_id)[0]) - 1
            plotting_df.plot(ax=self.axs, style=line_styles[style_degree_index], color=line_colours[style_degree_index])

        self.output()

    def output(self):
        """Format and output plot to file"""
        plt.xlabel("$h$")
        plt.ylabel("Error")
        self.parameters["log-log"] = True
        self.parameters["grid"] = True

        super().output()

    def get_line_styles(self, degree_id=None, variable=None, custom_style_dict={}):
        """Returns line styles for plotting"""
        line_styles_dict = {}
        markers = ["o", "x", "^", "v", "d", "+"]
        colours = ["blue", "orange", "green", "red", "purple", "pink"]
        lines = ["-", "--", ":", "-."]
        marker_counter = 0
        colour_counter = 0

        if degree_id is not None:
            variable_style_dict = {}
            line_styles_dict[degree_id] = [[], []]
            
            for column in self.error_data.error_df_dict[degree_id].columns:
                if column != "h" and column != "Time taken":
                    # Assuming the ID is of the form "variable norm"
                    variable = column.split(" ")[0]
                    norm = column.split(" ")[1]

                    # Each variable has a fixed marker and colour
                    if variable not in variable_style_dict:
                        variable_style_dict.update({variable: [markers[marker_counter], colours[colour_counter]]})
                        marker_counter += 1
                        colour_counter += 1
                        
                    line_style = variable_style_dict[variable][0]
                    
                    # Each norm has a fixed line style
                    if norm == "L2":
                        line_style += lines[0]
                        
                    elif norm == "H1":
                        line_style += lines[1]
                        
                    # Add combined degree and norm line styles to line styles dictionary
                    line_styles_dict[degree_id][0].append(line_style)
                    line_styles_dict[degree_id][1].append(variable_style_dict[variable][1])

        if variable is not None and degree_id is None:
            degree_style_dict = {}
            
            for degree_id, error_df in self.error_data.error_df_dict.items():
                line_styles_dict[degree_id] = [[], None]
                for column in error_df.columns:
                    if column != "h" and column != "Time taken":
                        # Assuming the ID is of the form "var norm"
                        var = column.split(" ")[0]
                        norm = column.split(" ")[1]

                        if var == variable:
                            # Each degree has a fixed marker and colour
                            if degree_id not in degree_style_dict:
                                degree_style_dict.update({degree_id: [markers[marker_counter], colours[colour_counter]]})
                                marker_counter += 1
                                colour_counter += 1
                                
                            line_style = degree_style_dict[degree_id][0]
                            
                            # Each norm has a fixed line style
                            if norm == "L2":
                                line_style += lines[0]
                                
                            elif norm == "H1":
                                line_style += lines[1]

                            # Add combined degree and norm line styles to line styles dictionary
                            line_styles_dict[degree_id][0].append(line_style)
                            line_styles_dict[degree_id][1] = degree_style_dict[degree_id][1]

        line_styles_dict.update(custom_style_dict)
        line_styles = list(line_styles_dict.values())

        return line_styles
        
