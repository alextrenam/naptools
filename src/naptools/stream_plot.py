import numpy as np
import matplotlib.pyplot as plt
import matplotlib.tri as tri
from matplotlib import cm, ticker, colors
from mpl_toolkits.axes_grid1 import make_axes_locatable
from naptools import BaseData, BasePlot
import os


# THIS IS NOT IN WORKING ORDER YET


class StreamData(BaseData):
    """Class for holding and performing operations on stream plot data"""
    def __init__(self, data_file_dict):
        super().__init__(data_file_dict)
        self.stream_df_dict = self.data_df_dict

    def get_data_limits(self, variable):
        """Returns an array containing the min and max of each data file"""
        data_limits = np.zeros((len(self.stream_df_dict), 2))
        i = 0

        if "magnitude" in variable:
            for df in self.stream_df_dict.values():
                df_magnitudes = np.sqrt(df.iloc[:, 0]**2 + df.iloc[:, 1]**2 + df.iloc[:, 2]**2)
                data_limits[i] = [df_magnitudes.min(), df_magnitudes.max()]
                i += 1

        else:
            for df in self.stream_df_dict.values():
                data_limits[i] = [df[variable].min(), df[variable].max()]
                i += 1

        return data_limits


class StreamPlot(BasePlot):
    """Class for creating error plots based on the underlying error data"""
    def __init__(self, stream_data):
        super().__init__(stream_data)
        self.stream_data = self.data
        self.set_plotting_parameters()

    def set_plotting_parameters(self):
        """Set the default stream plot parameters"""
        # Default parameters (alphabetical order)
        self.parameters["colour_bar_font_size"] = 0.75 * 32  # Should be 0.75 * font_size
        self.parameters["colour_bar_format"] = ".5f"
        self.parameters["colour_bar_location"] = "right"
        self.parameters["colour_map"] = cm.plasma
        self.parameters["individual_colour_bar"] = True
        self.parameters["mask_conditions"] = None
        self.parameters["separate_colour_bar"] = False
        self.parameters["suppress_legend"] = True
        self.parameters["x_label"] = "$x$"
        self.parameters["y_label"] = "$y$"

        # SOME OF THESE SHOULD BE GENERIC PLOTTING PARAMETERS

        self.parameters["font_size"] = 32
        self.parameters["figure_height"] = 6.0
        self.parameters["figure_width"] = 6.0

    def generate_mask(self, plotting_data, mask_conditions):
        """Generate a mask for plotting data from non-convex domains"""
        # Create triangulation from data
        triangulation = tri.Triangulation(plotting_data[0], plotting_data[1])

        # The mask includes triangles or not based on their barycentre
        # The x and y variables defined here are the coordinates that should
        # be refered to in the mask conditions
        x = plotting_data[0].to_numpy()[triangulation.triangles].mean(axis=1)
        y = plotting_data[1].to_numpy()[triangulation.triangles].mean(axis=1)

        # Create and apply mask
        if mask_conditions is not None:
            mask = np.where(eval(mask_conditions), 0, 1)
            triangulation.set_mask(mask)

        return triangulation
        
    def compute_levels(self, num_levels, logarithmic=False):
        """Return an array of values scaled evenly (or logarithmically)"""

        if logarithmic:
            lev_exp = np.linspace(
                np.log(self.colour_bar_min), np.log(self.colour_bar_max), num_levels
            )
            return np.power(np.exp(1), lev_exp)
        else:
            return np.linspace(self.colour_bar_min, self.colour_bar_max, num_levels)

    def plot(self, variable, timestamps, output_filename, parameters={}):
        """Create a single or series of contour plot(s)"""
        self.parameters.update(parameters)
        self.base_output_filename, self.file_extension = os.path.splitext(output_filename)

        self.data_limits = self.contour_data.get_data_limits(variable)

        self.total_data_min = self.data_limits[:, 0].min()
        self.total_data_max = self.data_limits[:, 1].max()

        # Default behaviour is to use the entire set of data for the colouring
        # The multiplication makes sure the limits show correctly
        if not self.parameters["individual_colour_bar"]:
            self.colour_bar_min = self.total_data_min * (1.0 + 1.0e-10)
            self.colour_bar_max = self.total_data_max * (1.0 - 1.0e-10)

        if self.parameters["separate_colour_bar"]:
            self.dummy_data_df = self.contour_data.data_df_dict[timestamps[0]]
            
        series_counter = 0
        
        for timestamp in timestamps:
            self.output_filename = self.base_output_filename + "_" + timestamp + self.file_extension
            
            self.fig, self.axs = plt.subplots()
            data_df = self.contour_data.data_df_dict[timestamp]
            
            if self.parameters["individual_colour_bar"]:
                self.colour_bar_min = self.data_limits[series_counter, 0]
                self.colour_bar_max = self.data_limits[series_counter, 1]
                
            self.linear_width = self.parameters["symlognorm_linear_width"] * (
                self.colour_bar_max - self.colour_bar_min
            )

            # Discrete colour values
            self.colour_levels = self.compute_levels(200)
            
            # Check in the csv file that paraview labels your x and y
            # coordinates with the following
            Xi = data_df["Points:0"]
            Yi = data_df["Points:1"]

            triangulation = self.generate_mask([Xi, Yi], self.parameters["mask_conditions"])

            if "magnitude" in variable:
                values = np.sqrt(data_df.iloc[:, 0]**2 + data_df.iloc[:, 1]**2 + data_df.iloc[:, 2]**2)

            else:
                values = data_df[variable]
            
            # May have to hard code these to get them to look good, or at
            # least format them properly.
            xx_ticks = [float(values.min()), float(values.max())]
            c_bar_format = self.parameters["colour_bar_format"]
            xx_labels = [f"{float(values.min()):{c_bar_format}}",
                         f"{float(values.max()):{c_bar_format}}"]
            
            # Note: depending on your data, you may want to choose a different
            # norm and set logarithmic = False in the above. There are norms
            # that work for diverging colour schemes which have a central
            # value (i.e. positive and negative data) and if you don't want a
            # logarithmic scale you don't need to supply a norm here (I think).
            #
            # The tricontour works well for point datasets of the form
            # (x, y, z), so this should be a good choice for unstructured
            # meshes where meshgrid and the usual contour functions in python
            # can't be applied. It works by defining a triangulation from
            # (x, y) then interpolating z.
            contour = self.axs.tricontourf(
                # Xi,
                # Yi,
                triangulation,
                values,
                self.colour_levels,
                # norm=colors.LogNorm(),
                norm=colors.SymLogNorm(linthresh=self.linear_width, linscale=1),
                cmap=self.parameters["colour_map"],
            )
            
            # Remove axis ticks
            self.axs.tick_params(left=False,
                                 right=False,
                                 bottom=False,
                                 labelleft=False,
                                 labelbottom=False
                                 )
            
            self.make_colour_bar(self.fig, self.axs, variable, contour, xx_ticks, xx_labels)
            self.output()

            if self.parameters["separate_colour_bar"]:
                self.make_separate_colour_bar(variable)

            series_counter += 1

    def make_colour_bar(self, fig, axs, variable, contour, ticks, labels):
        """Add and format colour bar"""
        divider = make_axes_locatable(axs)
        cax = divider.append_axes(self.parameters["colour_bar_location"],
                                  size="5%",
                                  pad=0.05)
        
        if self.parameters["colour_bar_location"] in ["top", "bottom"]:
            colour_bar_orientation = "horizontal"
        else:
            colour_bar_orientation = "vertical"

        cbar = fig.colorbar(contour,
                            cax=cax,
                            label=rf"${variable}$",
                            orientation=colour_bar_orientation,
                            # spacing="proportional",
                            )
        cbar.set_ticks(ticks=ticks, labels=labels)  # labels=labels prevents pretty scientific notation
        # cbar.formatter.set_powerlimits((-2, 2))
        # cbar.formatter.set_useMathText(True)
        cbar.ax.tick_params(labelsize=self.parameters["colour_bar_font_size"])
                
        if self.parameters["colour_bar_location"] in ["top", "bottom"]:
            cbar.ax.xaxis.set_ticks_position(self.parameters["colour_bar_location"])
            cbar.ax.get_xticklabels()[0].set_horizontalalignment("left")
            cbar.ax.get_xticklabels()[1].set_horizontalalignment("right")
        else:
            cbar.ax.yaxis.set_ticks_position(self.parameters["colour_bar_location"])
            
    def make_separate_colour_bar(self, variable):
        
        dummy_fig, dummy_axs = plt.subplots()  # To avoid deleting other axes
        dummy_Xi = self.dummy_data_df["Points:0"]
        dummy_Yi = self.dummy_data_df["Points:1"]
        dummy_values = self.dummy_data_df[variable]
        dummy_contour = dummy_axs.tricontourf(dummy_Xi,
                                              dummy_Yi,
                                              dummy_values,
                                              self.colour_levels,
                                              # norm=colors.LogNorm(),
                                              cmap=self.parameters["colour_map"])
        
        cbar = plt.colorbar(dummy_contour,
                            ax=dummy_axs,
                            label=rf"${variable}$",
                            aspect=50,
                            location=self.parameters["colour_bar_location"])
        cbar.ax.tick_params(labelsize=self.parameters["colour_bar_font_size"])
        tick_locator = ticker.MaxNLocator(nbins=5)
        cbar.locator = tick_locator
        cbar.update_ticks()
        dummy_axs.remove()
        plt.savefig(self.base_output_filename + "_colour_bar" + self.file_extension)
        
    def output(self):
        """Format and output plot to file"""
        # plt.tick_params(labelsize=self.parameters["font_size"])
        self.fig.set_figheight(self.parameters["figure_height"])
        self.fig.set_figwidth(self.parameters["figure_width"])
        self.axs.axes.set_aspect("equal")

        super().output()
