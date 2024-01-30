import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy import stats
from prettyplots import BaseData, BasePlot


class ErrorData(BaseData):
    """Class for holding and performing calculations on error data"""
    def __init__(self, data_file_dict):
        super().__init__(data_file_dict)
        self.error_df_dict = self.data_df_dict

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
        convergence_df = self.get_convergence(degree)
        
        # Drop the final row before printing
        convergence_df.drop(convergence_df.tail(1).index, inplace=True)
        print("\033[2;31;43m  CONVERGENCE RATES \033[0;0m")
        print(convergence_df)
            
    
class ErrorPlot(BasePlot):
    """Class for creating error plots based on the underlying error data"""
    def __init__(self, error_data):
        super().__init__(error_data)
        self.error_data = self.data

    def plot_degree(self, degree, parameters={}):
        """Plot all errors for a single polynomial degree"""
        self.parameters.update(parameters)
        self.output_filename = "results/" + self.error_data.project_name + "/benchmark_p" + str(degree) + ".pdf"
        self.fig, self.axs = plt.subplots()
        error_df = self.error_data.error_df_dict[str(degree)]
        
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
        plotting_df.plot(ax=self.axs, style=self.line_styles)
        self.output()
    
    def plot_variable(self, variable, output_filename, parameters={}):
        """Plot errors of all polynomial degree for the given variable"""
        self.parameters.update(parameters)
        self.output_filename = output_filename
        self.fig, self.axs = plt.subplots()

        for error_df_id, error_df in self.error_data.error_df_dict.items():
            # Remove unnecessary columns from DataFrame
            plotting_df = error_df.set_index("h")
            columns_to_drop = []
            plotting_line_styles_dict = self.line_styles_dict
            line_styles = []

            for col in plotting_df.columns:
                if variable + " " not in col:
                    columns_to_drop.append(col)
            
            plotting_df.drop(
                axis=1,
                labels=["Time taken"] + columns_to_drop,
                inplace=True,
            )

            for line_style_id in columns_to_drop:
                if line_style_id in plotting_line_styles_dict:
                    del plotting_line_styles_dict[line_style_id]
            
 
            renaming_columns = {}
            
            for error, error_norm in self.error_norms_dict.items():
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
            line_styles = list(plotting_line_styles_dict.values())
            plotting_df.plot(ax=self.axs, style=line_styles)

        self.output()

    def output(self):
        """Format and output plot to file"""
        plt.xlabel("$h$")
        plt.ylabel("Error")
        self.parameters["log-log"] = True
        self.parameters["grid"] = True

        super().output()

    def update_legend(self, error_norms_dict, custom_style_dict={}):
        """Update notation in the legend (e.g. LaTeX norm notation)"""
        self.error_norms_dict = error_norms_dict
        self.line_styles_dict = {}
        self.variable_marker_dict = {}
        self.markers = ["o", "x", "^"]
        self.marker_counter = 0
        
        for error_norm in error_norms_dict:
            # Assuming the ID is of the form "variable norm"
            variable = error_norm.split(" ")[0]
            
            if variable not in self.variable_marker_dict:
                self.variable_marker_dict.update({variable: self.markers[self.marker_counter]})
                self.marker_counter += 1

            line_style = self.variable_marker_dict[variable]
            
            if "L2" in error_norm:
                line_style += "-"

            elif "H1" in error_norm:
                line_style += "--"

            self.line_styles_dict[error_norm] = line_style

        self.line_styles_dict.update(custom_style_dict)
        self.line_styles = list(self.line_styles_dict.values())

    def get_line_styles(self, error_norms_dict, context, custom_style_dict={}):
        """Returns line styles for plotting"""
        line_styles_dict = {}
        variable_marker_dict = {}
        markers = ["o", "x", "^", "v", "d", "+"]
        colours = ["blue", "orange", "green", "red", "purple", "pink"]
        lines = ["-", "--", ":", "-."]
        marker_counter = 0

        # I THINK THE IDEA HERE SHOULD BE THAT A DICTIONARY IS CREATED
        # WITH THE KEYS STORING ALL THE RELEVANT INFORMATION TO ASSIGN
        # UNIQUE LINE STYLES -- MAYBE A DICTIONARY OF DICTIONARIES?
        # (SINCE THAT IS HOW THE DATA IS STORED ANYWAY BASICALLY)
        
        for 
        if context == "variable":
            line_style
            self.colour_index += 1
            self.marker_index += 1

        elif context == "degree":
            for error_norm in error_norms_dict:
                # Assuming the ID is of the form "variable norm"
                variable = error_norm.split(" ")[0]
                
                if variable not in self.variable_marker_dict:
                    self.variable_marker_dict.update({variable: self.markers[self.marker_counter]})
                    self.marker_counter += 1
                    
                line_style = self.variable_marker_dict[variable]
                
                if "L2" in error_norm:
                    line_style += "-"
                    
                elif "H1" in error_norm:
                    line_style += "--"

                self.line_styles_dict[error_norm] = line_style


        line_styles_dict.update(custom_style_dict)
        line_styles = list(line_styles_dict.values())

        return line_styles
