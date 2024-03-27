import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm, ticker, colors
from mpl_toolkits.axes_grid1 import make_axes_locatable
from naptools import BaseData, BasePlot


class ContourData(BaseData):
    """Class for holding and performing operations on contour plot data"""

    def __init__(self, data_file_dict):
        super().__init__(data_file_dict)
        self.contour_df_dict = self.data_df_dict


class ContourPlot(BasePlot):
    """Class for creating error plots based on the underlying error data"""

    def __init__(self, contour_data):
        super().__init__(contour_data)
        self.contour_data = self.data
        self.set_plotting_parameters()

    def set_plotting_parameters(self):
        """Set the default contour plot parameters"""
        self.parameters["separate_colour_bar"] = False
        self.parameters["individual_colour_bar"] = True
        self.parameters["colour_map"] = cm.plasma
        self.parameters["num_thin_lines"] = 5
        self.parameters["x_label"] = "$x$"
        self.parameters["y_label"] = "$y$"
        self.parameters["linear_width"] = 0.01
        self.parameters["suppress_legend"] = True

        # SOME OF THESE SHOULD BE GENERIC PLOTTING PARAMETERS

        self.parameters["font_size"] = 32
        self.parameters["figure_height"] = 6.0
        self.parameters["figure_width"] = 6.0

    def compute_levels(self, num_levels, logarithmic=False):
        """Return an array of values scaled evenly (or logarithmically)"""

        if logarithmic:
            lev_exp = np.linspace(
                np.log(self.colour_bar_min), np.log(self.colour_bar_max), num_levels
            )
            return np.power(np.exp(1), lev_exp)
        else:
            return np.linspace(self.colour_bar_min, self.colour_bar_max, num_levels)

    def plot_series(self, variable, output_filename, parameters={}):
        """Create a series of contour plots associated to the given timestamps"""
        self.parameters.update(parameters)

        for timestamp, data_df in self.contour_data.items():
            self.output_filename = output_filename + "_" + timestamp

    def plot(self, variable, timestamp, output_filename, parameters={}):
        """Create a single contour plot"""
        self.parameters.update(parameters)
        self.output_filename = output_filename
        self.fig, self.axs = plt.subplots()
        data_df = self.contour_data.data_df_dict[timestamp]

        if self.parameters["individual_colour_bar"]:
            self.colour_bar_max = data_df[variable].max()
            self.colour_bar_min = data_df[variable].min()
            self.linear_width = self.parameters["linear_width"] * (
                self.colour_bar_max - self.colour_bar_min
            )

        # Discrete colour values
        self.colour_levels = self.compute_levels(200)

        # Values defining the contour lines
        self.contour_levels = self.compute_levels(50)
        self.thick_contour_levels = self.contour_levels[
            :: self.parameters["num_thin_lines"]
        ]

        # Check in the csv file that paraview labels your x and y coordinates with
        # the following
        Xi = data_df["Points:0"]
        Yi = data_df["Points:1"]
        values = data_df[variable]

        # May have to hard code these to get them to look good, or at least format
        # them properly.
        xx_ticks = [float(values.min()), float(values.max())]
        xx_labels = [str(values.min()), str(values.max())]

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
        contour = self.axs.tricontourf(
            Xi,
            Yi,
            values,
            self.colour_levels,
            # norm=colors.LogNorm(),
            norm=colors.SymLogNorm(linthresh=self.linear_width, linscale=1),
            cmap=self.parameters["colour_map"],
        )

        # Remove the lines between filled regions (we want to add our own):
        for c in self.axs.collections:
            c.set_edgecolor("face")

        # Add in the contour lines (play with the alpha and colour values to get
        # it to look good)
        self.axs.tricontour(
            Xi,
            Yi,
            values,
            self.thick_contour_levels,
            alpha=0.5,
            colors=["1."],
            linewidths=[0.5],
        )
        self.axs.tricontour(
            Xi,
            Yi,
            values,
            self.contour_levels,
            alpha=0.15,
            colors=["1."],
            linewidths=[0.05],
        )

        # # Format plot axes
        # self.axs.set_xlabel(self.parameters["x_label"])
        # self.axs.set_ylabel(self.parameters["y_label"])
        # self.axs.tick_params(labelsize=self.parameters["font_size"])
        # # self.axs.axes.set_aspect("equal")

        self.output()

    def output(self):
        """Format and output plot to file"""
        plt.xlabel(self.parameters["x_label"])
        plt.ylabel(self.parameters["y_label"])

        # Remove axis ticks
        plt.tick_params(
            left=False, right=False, bottom=False, labelleft=False, labelbottom=False
        )

        # if not self.separate_colour_bar:
        #     # Add and format colorbar
        #     divider = make_axes_locatable(axs)
        #     cax = divider.append_axes("right", size="5%", pad=0.05)
        #     cbar = fig.colorbar(contour, cax=cax)
        #     cbar.set_ticks(ticks=xx_ticks, labels=xx_labels)
        #     cbar.ax.tick_params(labelsize=0.75*self.parameters["font_size"])

        super().output()
