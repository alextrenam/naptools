import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm, ticker
from mpl_toolkits.axes_grid1 import make_axes_locatable
from naptools import BaseData, BasePlot, ContourPlot
import os


class Data2D(BaseData):
    """Class for holding and performing operations on two-dimensional data"""
    def __init__(self, data_file_dict):
        super().__init__(data_file_dict)

    def get_data_limits(self, variable):
        """Returns an array containing the min and max of each data file"""
        data_limits = np.zeros((len(self.data_df_dict), 2))
        i = 0

        if "magnitude" in variable:
            for df in self.data_df_dict.values():
                df_magnitudes = np.sqrt(df.iloc[:, 0]**2 + df.iloc[:, 1]**2 + df.iloc[:, 2]**2)
                data_limits[i] = [df_magnitudes.min(), df_magnitudes.max()]
                i += 1

        else:
            for df in self.data_df_dict.values():
                data_limits[i] = [df[variable].min(), df[variable].max()]
                i += 1

        return data_limits


class Plot2D(BasePlot):
    """Class for creating two-dimensional plots"""
    def __init__(self, data):
        super().__init__(data)
        self.set_plotting_parameters()

    def set_plotting_parameters(self):
        """Set the default stream plot parameters"""
        # Default parameters (alphabetical order)
        self.parameters["colour_bar_font_size"] = 0.75 * 32  # Should be 0.75 * font_size
        self.parameters["colour_bar_format"] = ".5f"
        self.parameters["colour_bar_location"] = "right"
        self.parameters["colour_map"] = cm.plasma
        self.parameters["colour_range"] = 1.0
        self.parameters["individual_colour_bar"] = True
        self.parameters["separate_colour_bar"] = False
        self.parameters["suppress_legend"] = True
        self.parameters["x_label"] = "$x$"
        self.parameters["y_label"] = "$y$"

        # SOME OF THESE SHOULD BE GENERIC PLOTTING PARAMETERS

        self.parameters["font_size"] = 32
        self.parameters["figure_height"] = 6.0
        self.parameters["figure_width"] = 6.0
        
    # SINGLE PLOT FUNCTION AND THEN DO DIFFERENT THINGS DEPENDING ON CLASS INSTANCE?
        
    def plot(self, variable, timestamps, output_filename, parameters={}):
        """Create a single or series of plot(s)"""
        self.parameters.update(parameters)
        self.base_output_filename, self.file_extension = os.path.splitext(output_filename)
        
        self.data_limits = self.data.get_data_limits(variable)

        self.total_data_min = self.data_limits[:, 0].min()
        self.total_data_max = self.data_limits[:, 1].max()
        
        # Default behaviour is to use the entire set of data for the colouring
        # The multiplication makes sure the limits show correctly
        if not self.parameters["individual_colour_bar"]:
            self.colour_bar_min = self.total_data_min * (1.0 + 1.0e-10)
            self.colour_bar_max = self.total_data_max * (1.0 - 1.0e-10)
            self.colour_bar_centre = 0.5 * (np.mean(self.data_limits[:, 0]) + np.mean(self.data_limits[:, 1]))
            self.vmin = self.colour_bar_centre - self.parameters["colour_range"] * (self.colour_bar_centre - self.colour_bar_min)
            self.vmax = self.colour_bar_centre + self.parameters["colour_range"] * (self.colour_bar_centre - self.colour_bar_min)

        if self.parameters["separate_colour_bar"]:
            self.dummy_data_df = self.data.data_df_dict[timestamps[0]]
            
        series_counter = 0
        
        for timestamp in timestamps:
            self.output_filename = self.base_output_filename + "_" + timestamp + self.file_extension
            
            self.fig, self.axs = plt.subplots()
            data_df = self.data.data_df_dict[timestamp]
            
            if self.parameters["individual_colour_bar"]:
                self.colour_bar_min = self.data_limits[series_counter, 0]
                self.colour_bar_max = self.data_limits[series_counter, 1]
                self.colour_bar_centre = np.mean(data_df[variable])

            if isinstance(self, ContourPlot):
                plot = self.plot_contour(data_df, variable)
                
            # Remove axis ticks
            self.axs.tick_params(left=False,
                                 right=False,
                                 bottom=False,
                                 labelleft=False,
                                 labelbottom=False
                                 )
            
            # May have to hard code these to get them to look good, or at
            # least format them properly.
            # xx_ticks = [float(values.min()), float(values.max())]
            xx_ticks = [float(self.colour_bar_min), float(self.colour_bar_max)]
            
            c_bar_format = self.parameters["colour_bar_format"]
            # xx_labels = [f"{float(values.min()):{c_bar_format}}",
            #              f"{float(values.max()):{c_bar_format}}"]
            xx_labels = [f"{float(self.colour_bar_min):{c_bar_format}}",
                         f"{float(self.colour_bar_max):{c_bar_format}}"]
            
            self.make_colour_bar(self.fig, self.axs, variable, plot, xx_ticks, xx_labels)
            self.output()

            if self.parameters["separate_colour_bar"]:
                self.make_separate_colour_bar(variable)

            series_counter += 1
        
    def make_colour_bar(self, fig, axs, variable, plot, ticks, labels):
        """Add and format colour bar"""
        divider = make_axes_locatable(axs)
        cax = divider.append_axes(self.parameters["colour_bar_location"],
                                  size="5%",
                                  pad=0.05)
        
        if self.parameters["colour_bar_location"] in ["top", "bottom"]:
            colour_bar_orientation = "horizontal"
        else:
            colour_bar_orientation = "vertical"

        cbar = fig.colorbar(plot,
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
        """Create colour bar as a separate figure"""
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
