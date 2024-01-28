import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import cm, ticker
import re
from .plot import BasePlot
from .contour_plot import ContourPlot

class Plotter:
    """Data handler with method calls which create instances of various Plots"""
    def __init__(self, input_data_files):
        self.input_data_files = input_data_files
        self.num_timesteps = len(self.input_data)
        self.data = []
        self.timestamps = []
        self.parameters = {
            "x_label": "$x$",
            "y_label": "$v$",
            "font_size": 32,
            "colour_map": cm.plasma,
            "num_thin_lines": 5,
            "figure_height": 6,
            "figure_width": 6,
            "separate_colour_bar": False,
        }
        plt.rcParams["font.family"] = "serif"
        plt.rcParams["mathtext.fontset"] = "cm"
        plt.rcParams["axes.formatter.use_mathtext"] = True
        plt.rcParams["savefig.bbox"] = "tight"
        plt.rcParams["axes.labelsize"] = self.plotting_params["font_size"]

        # Read in the data and timestamps
        self.get_data()

    def get_data(self):
        """Store the input data (from potentially multiple files)"""
        
        max_vals = []
        min_vals = []
        
        for input_data_file in self.input_data_files:
            df = pd.read_csv(input_data_file)

            df_max_val = df[self.plotting_variable].max()
            df_min_val = df[self.plotting_variable].min()

            if self.plot_type == "contour":
                # We require a "timestamp" (doesn't need to represent time in reality)
                # for creating the Dataset
                try:
                    timestamp = re.search(r"\d+", input_data_file).group()
                    
                    # For ease in later post-processing, make sure the timestamps
                    # all have the same length
                    while len(timestamp) < 4:
                        timestamp = "0" + timestamp
                        self.timestamps.append(timestamp)
                
                except Exception:
                    timestamp = None
                    print("\n\tException: Invalid input file name -- timestamp required.")
                    print(f"\tFile responsible: {input_data_file}\n")
                    break

            self.data.append(df)
            max_vals.append(df_max_val)
            min_vals.append(df_min_val)

        self.data_max = max(max_vals)
        self.data_min = min(min_vals)
        
        # Default behaviour is to use the entire set of data for the colouring
        self.colour_bar_max = self.data_max
        self.colour_bar_min = self.data_min

    def plot(self, output_filename, plot_type, plotting_variable, *independent_vars):
        """Plot (a subset of) the data in the desired format"""
        if plot_type == "line":
            BasePlot(output_filename, plotting_variable, independent_vars[0])
        elif plot_type == "contour":
            ContourPlot(output_filename,
                           plotting_variable,
                           independent_vars[0],
                           independent_vars[1])
                    
    def plot_series(self, output_filename, plot_type, plotting_variable, *independent_vars):
        """Create a plot for each of the input files"""
        for i in range(self.num_timesteps):
            print(f"Plotting figure {i+1}...")
            self.plot(self.data[i], self.timestamps[i])

        if plot_type == "contour":
            if self.separate_colour_bar:
                fig, axs = plt.subplots(figsize=(15, 15))
                dummy_Xi = self.data[0]["Points:0"]
                dummy_Yi = self.data[0]["Points:1"]
                dummy_values = self.data[0][self.plotting_variable]
                dummy_contour = axs.tricontourf(dummy_Xi,
                                                dummy_Yi,
                                                dummy_values,
                                                self.colour_levels,
                                                # norm=colors.LogNorm(),
                                                cmap=self.plotting_params["colour_map"])
                
                cbar = plt.colorbar(dummy_contour,
                                    ax=axs,
                                    label=rf"${self.plotting_variable}$",
                                    aspect=50,
                                    location="top")
                cbar.ax.tick_params(labelsize=0.75*self.plotting_params["font_size"])
                tick_locator = ticker.MaxNLocator(nbins=5)
                cbar.locator = tick_locator
                cbar.update_ticks()
                axs.remove()
                plt.savefig(output_filename + "contour_colour_bar.pdf")
