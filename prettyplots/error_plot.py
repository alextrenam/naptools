import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy import stats
from prettyplots import BasePlot


class ErrorData:
    """Class for holding and performing calculations on error data"""
    def __init__(self, project_name, degree_list, error_norms_dict):
        self.project_name = project_name
        self.degree_list = degree_list  # List of polynomial degrees to plot
        self.error_df_dict = {}  # Dictionary to hold all error data
        self.error_norms_dict = error_norms_dict  # Norms being plotted and LaTeX notation for legend
        
        # Populate dictionary of error data (for various polynomial degree)
        for degree in self.degree_list:
            error_df = pd.read_csv("results/" + self.project_name + "/errors_p" + str(degree) + ".csv")
            self.error_df_dict[str(degree)] = error_df

    def get_convergence(self, degree):
        """Returns a DataFrame of the convergence of the provided error data"""
        error_df = self.error_df_dict[str(degree)]
        convergence_df = error_df.copy(deep=True)
        
        for i in range(error_df.shape[0] - 1):
            convergence_df.loc[i] = np.log2((error_df.loc[i]) / (error_df.loc[i + 1]))

        return convergence_df

    def print_degree(self, degree):
        """Prints error and convergence tables in human-readable format"""
        # Print error table
        print("\033[2;31;43m  ERROR VALUES \033[0;0m")
        print(self.error_df_dict[str(degree)])

        # Calculate convergence rate table
        convergence_df = self.get_convergence(degree)
        
        # Drop the final row before printing
        convergence_df.drop(convergence_df.tail(1).index, inplace=True)
        print("\033[2;31;43m  CONVERGENCE RATES \033[0;0m")
        print(convergence_df)
            
    
class ErrorPlot(BasePlot):
    """Class for creating error plots based on the underlying error data"""
    def __init__(self, error_data):
        self.error_data = error_data
        super().__init__()

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
        plotting_df.plot(ax=self.axs) # , style=self.parameters["line_style"])
        self.output()
    
    def plot_variable(self, variable, parameters={}):
        """Plot errors of all polynomial degree for the given variable"""
        self.parameters.update(parameters)
        self.output_filename = "results/" + self.error_data.project_name + "/benchmark_all_" + variable + ".pdf"
        self.fig, self.axs = plt.subplots()

        for degree, error_df in self.error_data.error_df_dict.items():
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
                renaming_columns[error] = r"$p=$" + f"{degree}, " + fr"{error_norm}, " + f"EOC: {slope:.3f}"
                
            # Rename columns for correct plot labels
            plotting_df.rename(
                columns=renaming_columns,
                inplace=True,
            )

            # Create plot
            plotting_df.plot(ax=self.axs, style=["x-", "o--"])

        self.output()

    def output(self):
        # Formatting
        plt.xlabel("$h$")
        plt.ylabel("Error")
        plt.xscale("log")
        plt.yscale("log")
        plt.grid(which="both", color="#cfcfcf")

        super().output()
