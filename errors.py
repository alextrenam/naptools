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
    def __init__(self, project_name, degree_list):
        self.project_name = project_name
        self.degree_list = degree_list
        self.error_df_dict = {}

        # Populate dictionary of error data (for various polynomial degree)
        for degree in degree_list:
            error_df = pd.read_csv("results/" + self.project_name + "/errors_p" + str(degree) + ".csv")
            self.error_df_dict[str(degree)] = error_df

    def get_convergence(self, degree):
        error_df = self.error_df_dict[str(degree)]
        convergence_df = error_df.copy(deep=True)
        for i in range(error_df.shape[0] - 1):
            convergence_df.loc[i] = np.log2((error_df.loc[i]) / (error_df.loc[i + 1]))
        
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
        
        # Calculate line slopes for showing convergence rates on plot
        L2_slope = stats.linregress(np.log2(error_df["h"]), np.log2(error_df["u L2"]))[0]
        H1_slope = stats.linregress(np.log2(error_df["h"]), np.log2(error_df["u H1"]))[0]
        
        # Rename columns for correct plot labels
        plotting_df.rename(
            columns={
                "u L2": r"$|\!|u - u_h|\!|$" + f", Slope (EOC): {L2_slope:.3f}",
                "u H1": r"$|\!|\nabla\left(u - u_h\right)|\!|$" + f", Slope (EOC): {H1_slope:.3f}",
            },
            inplace=True,
        )
        
        # Create combined plot
        fig, axs = plt.subplots()
        plotting_df.plot(ax=axs, style=["x-", "o--"])
        
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

    def plot_all(self):
        # Create combined plot
        fig, axs = plt.subplots()
        
        for degree, error_df in self.error_df_dict.items():
            # Remove unnecessary columns from DataFrame
            plotting_df = error_df.set_index("h")
            
            plotting_df.drop(
                axis=1,
                labels=["Time taken"],
                inplace=True,
            )
            
            # Calculate line slopes for showing convergence rates on plot
            L2_slope = stats.linregress(np.log2(error_df["h"]), np.log2(error_df["u L2"]))[0]
            H1_slope = stats.linregress(np.log2(error_df["h"]), np.log2(error_df["u H1"]))[0]
            
            # Rename columns for correct plot labels
            plotting_df.rename(
                columns={
                    "u L2": r"$p=$" + f"{degree}, " + r"$L2$, " + f"EOC: {L2_slope:.3f}",
                    "u H1": r"$p=$" + f"{degree}, " + r"$H1$, " + f"EOC: {H1_slope:.3f}",
                },
                inplace=True,
            )
            
            plotting_df.plot(ax=axs, style=["x-", "o--"])
        
        plt.xlabel("$h$")
        plt.ylabel("Error")
        plt.xscale("log")
        plt.yscale("log")
        plt.legend()
        plt.grid(which="both", color="#cfcfcf")
        
        filename = "results/" + project_name + "/benchmark_all.pdf"
        plt.savefig(filename)
        plt.close()
        
        print(f"Combined plot saved as: {filename}")
