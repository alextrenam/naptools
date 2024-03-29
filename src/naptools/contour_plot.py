import matplotlib.pyplot as plt
from matplotlib import cm, ticker
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np
import pandas as pd
import sys
import os
import re

# POTENTIAL EXTENSIONS:
# -- PLOT SIDE BY SIDE CONTOUR PLOTS (FOR SHOWING MULTIPLE VARIABLES IN VIDEOS)


class PrettyPlots:
    """Methods of this class create nice looking plots of various nature."""
    def __init__(self, input_data, plotting_variable):
        self.input_data = input_data
        self.plotting_variable = plotting_variable
        self.num_timesteps = len(self.input_data)
        self.data = []
        self.timestamps = []
        self.separate_colour_bar = False

        # Output files names are sanitised input file names
        self.filename_start = re.split(r"\d+", self.input_data[0])[0]
        self.filename_start = self.filename_start.split("data")[0]
        
        # Read in the data and timestamps
        self.create_data()
        
        self.plotting_params = {
            "x_label": "$x$",
            "y_label": "$v$",
            "font_size": 32,
            "colour_map": cm.plasma,
            "num_thin_lines": 5,
            "figure_height": 6,
            "figure_width": 6,
        }
        plt.rcParams["font.family"] = "serif"
        plt.rcParams["mathtext.fontset"] = "cm"
        plt.rcParams["axes.formatter.use_mathtext"] = True
        plt.rcParams["savefig.bbox"] = "tight"
        plt.rcParams["axes.labelsize"] = self.plotting_params["font_size"]

        # Discrete colour values
        self.colour_levels = self.compute_contour_levels(200)
        
        # Values defining the contour lines
        self.contour_levels = self.compute_contour_levels(50)
        self.thick_contour_levels = self.contour_levels[::self.plotting_params["num_thin_lines"]]
                
    def create_data(self):
        """Store the input data (from potentially multiple files)."""

        max_vals = []
        min_vals = []
        
        for input_data_file in self.input_data:
            df = pd.read_csv(input_data_file)

            df_max_val = df[self.plotting_variable].max()
            df_min_val = df[self.plotting_variable].min()

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

    def compute_contour_levels(self, num_levels, logarithmic=False):
        """Return an array of values scaled evenly (or logarithmically) used for
            contour plots."""
        
        if logarithmic:
            lev_exp = np.linspace(np.log(self.colour_bar_min),
                                  np.log(self.colour_bar_max),
                                  num_levels)
            return np.power(np.exp(1), lev_exp)
        else:
            return np.linspace(self.colour_bar_min, self.colour_bar_max, num_levels)

    def plot_contour_series(self):
        """Create a contour plot for each of the input files."""

        for i in range(self.num_timesteps):
            print(f"Plotting figure {i+1}...")
            self.plot_contour(self.data[i], self.timestamps[i])

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
            plt.savefig(self.filename_start + "contour_colour_bar.pdf")
        
    def plot_contour(self, data_df, timestamp):
        """In paraview, select the file and time step that you want to plot a nice
            contour of, and select file->Save Data. Make sure you select csv as the file
            type to save as. Pandas is really useful for reading and using data from csv
            files. Paraview should give each data variable a name based upon what you
            called each variable when you saved it in dealii, and it contains the
            spatial coordinates of all data points."""

        # Check in the csv file that paraview labels your x and y coordinates with
        # the following 
        Xi = data_df["Points:0"]
        Yi = data_df["Points:1"]
        values = data_df[self.plotting_variable]

        # May have to hard code these to get them to look good, or at least format
        # them properly.
        xx_ticks = [values.min(), values.max()]
        xx_labels = [str(values.min()), str(values.max())]
        
        fig, axs = plt.subplots()
        fig.set_figheight(self.plotting_params["figure_height"])
        fig.set_figwidth(self.plotting_params["figure_width"])
        
        # Note: depending on your data, you may want to choose a different norm and
        # set logarithmic = False in the above. There are norms that work for
        # diverging colour schemes which have a central value (i.e. positive and
        # negative data) and if you don't want a logarithmic scale you don't need to
        # supply a norm here (I think).
        #
        # The tricontour works well for point datasets of the form (x, y, z), so
        # this should be a good choice for unstructured meshes where meshgrid and
        # the usual contour functions in python can't be applied. It works by
        # defining a triangulation from (x, y) then interpolating z.
        contour = axs.tricontourf(Xi, Yi, values,
                                self.colour_levels,
                                # norm=colors.LogNorm(),
                                cmap=self.plotting_params["colour_map"])
        
        # Remove the lines between filled regions (we want to add our own):
        for c in axs.collections:
            c.set_edgecolor("face")

        # Add in the contour lines (play with the alpha and colour values to get
        # it to look good)
        axs.tricontour(Xi, Yi, values, self.thick_contour_levels, alpha=0.5, colors=['1.'], linewidths=[0.5])
        axs.tricontour(Xi, Yi, values, self.contour_levels, alpha=0.15, colors=['1.'], linewidths=[0.05])

        # Format plot axes
        axs.set_xlabel(self.plotting_params["x_label"])
        axs.set_ylabel(self.plotting_params["y_label"])
        axs.tick_params(labelsize=self.plotting_params["font_size"])
        # axs.axes.set_aspect("equal")

        # Remove axis ticks
        plt.tick_params(left=False,
                        right=False,
                        bottom=False,
                        labelleft=False,
                        labelbottom=False)

        if not self.separate_colour_bar:
            # Add and format colorbar
            divider = make_axes_locatable(axs)
            cax = divider.append_axes("right", size="5%", pad=0.05)
            cbar = fig.colorbar(contour, cax=cax)
            cbar.set_ticks(ticks=xx_ticks, labels=xx_labels)
            cbar.ax.tick_params(labelsize=0.75*self.plotting_params["font_size"])

        # Output figure
        output_filename = self.filename_start + "contour_" + str(timestamp) + ".pdf"
        os.makedirs(os.path.dirname(output_filename), exist_ok=True)
        plt.savefig(output_filename)
        
        plt.close()
        
if __name__ == "__main__":
    # Command line arguments
    input_data = [sys.argv[i] for i in range(1, len(sys.argv) - 1)]
    plotting_variable = sys.argv[-1]

    pretty_contour = PrettyPlots(input_data, plotting_variable)

    pretty_contour.plot_contour_series()
    
    # pretty_contour.plot_contour()
