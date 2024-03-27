import numpy as np
from naptools import BaseData, BasePlot


class ContourPlot(BasePlot):
    """Class for creating error plots based on the underlying error data"""
    def __init__(self, contour_data):
        super().__init__(contour_data)
        self.contour_data = self.data
        self.set_plotting_parameters()

    def set_plotting_parameters(self):
        """Set the default contour plot parameters"""
        
    # Output files names are sanitised input file names
    self.filename_start = re.split(r"\d+", self.input_data[0])[0]
    self.filename_start = self.filename_start.split("data")[0]
    
    # Discrete colour values
    self.colour_levels = self.compute_contour_levels(200)
    
    # Values defining the contour lines
    self.contour_levels = self.compute_contour_levels(50)
    self.thick_contour_levels = self.contour_levels[::self.plotting_params["num_thin_lines"]]
                
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

if __name__ == "__main__":
    # Command line arguments
    input_data = [sys.argv[i] for i in range(1, len(sys.argv) - 1)]
    plotting_variable = sys.argv[-1]

    pretty_contour = PrettyPlots(input_data, plotting_variable)

    pretty_contour.plot_contour_series()
    
    # pretty_contour.plot_contour()
