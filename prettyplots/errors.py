import sys
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy import stats

project_name = sys.argv[1]
poly_degree = int(sys.argv[2])

plt.rcParams["font.family"] = "serif"
plt.rcParams["mathtext.fontset"] = "cm"
plt.rcParams["figure.figsize"] = [12, 10]
plt.rc("axes", labelsize=14)
plt.rc("legend", fontsize=12)


class ErrorPlots:
    def __init__(self, project_name, degree_list, error_norms_dict, parameters={}):
        self.project_name = project_name
        self.degree_list = degree_list  # List of polynomial degrees to plot
        self.error_df_dict = {}  # Dictionary to hold all error data
        self.error_norms_dict = error_norms_dict  # Norms being plotted and LaTeX notation for legend
        self.parameters = {}
        self.parameters.update(parameters)

        # Populate dictionary of error data (for various polynomial degree)
        for degree in self.degree_list:
            error_df = pd.read_csv("results/" + self.project_name + "/errors_p" + str(degree) + ".csv")
            self.error_df_dict[str(degree)] = error_df

    def get_convergence(self, degree):
        error_df = self.error_df_dict[str(degree)]
        convergence_df = error_df.copy(deep=True)
        for i in range(error_df.shape[0] - 1):
            convergence_df.loc[i] = np.log2((error_df.loc[i]) / (error_df.loc[i + 1]))

        return convergence_df
        
    def print_degree(self, degree):
        # Print error table
        error_df = self.error_df_dict[str(degree)]
        print("\033[2;31;43m  ERROR VALUES \033[0;0m")
        print(error_df)

        # Calculate convergence rate table
        convergence_df = self.get_convergence(degree)
        
        # Drop the final row before printing
        convergence_df.drop(convergence_df.tail(1).index, inplace=True)
        print("\033[2;31;43m  CONVERGENCE RATES \033[0;0m")
        print(convergence_df)
            
    def plot_degree(self, degree):
        error_df = self.error_df_dict[str(degree)]
        
        # Remove unnecessary columns from DataFrame
        plotting_df = error_df.set_index("h")

        plotting_df.drop(
            axis=1,
            labels=["Time taken"],
            inplace=True,
        )
    
        renaming_columns = {}
        
        for error, error_norm in self.error_norms_dict.items():
            # Calculate line slope for showing convergence rates on plot
            slope = stats.linregress(np.log2(error_df["h"]), np.log2(error_df[error]))[0]

            # Relabel the columns to the correct LaTeX norm notation
            renaming_columns[error] = fr"{error_norm}" + f", Slope (EOC): {slope:.3f}"
        
        # Rename columns for correct plot labels
        plotting_df.rename(
            columns=renaming_columns,
            inplace=True,
        )

        # Create combined plot
        fig, axs = plt.subplots()
        plotting_df.plot(ax=axs, style=self.parameters["line_style"])
        
        plt.xlabel("$h$")
        plt.ylabel("Error")
        plt.xscale("log")
        plt.yscale("log")
        plt.legend()
        plt.grid(which="both", color="#cfcfcf")
        
        filename = "results/" + project_name + "/benchmark_p" + str(poly_degree) + ".pdf"
        plt.savefig(filename)
        plt.close()
        
        print(f"Combined plot saved as: {filename}")

    def plot_all(self, variable):
        # Create combined plot
        fig, axs = plt.subplots()

        for degree, error_df in self.error_df_dict.items():
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
            
            for error, error_norm in self.error_norms_dict.items():
                # Calculate line slope for showing convergence rates on plot
                slope = stats.linregress(np.log2(error_df["h"]), np.log2(error_df[error]))[0]
                
                # Relabel the columns to the correct LaTeX norm notation
                renaming_columns[error] = r"$p=$" + f"{degree}, " + fr"{error_norm}, " + f"EOC: {slope:.3f}"
                
            # Rename columns for correct plot labels
            plotting_df.rename(
                columns=renaming_columns,
                inplace=True,
            )

            plotting_df.plot(ax=axs, style=["x-", "o--"])
        
        plt.xlabel("$h$")
        plt.ylabel("Error")
        plt.xscale("log")
        plt.yscale("log")
        plt.legend()
        plt.grid(which="both", color="#cfcfcf")
        
        filename = "results/" + project_name + "/benchmark_all_" + variable + ".pdf"
        plt.savefig(filename)
        plt.close()
        
        print(f"Combined plot saved as: {filename}")
