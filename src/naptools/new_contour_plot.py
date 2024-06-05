import numpy as np
import matplotlib.tri as tri
from matplotlib import colors
from naptools import Plot2D


class ContourPlot(Plot2D):
    """Class for creating error plots based on the underlying error data"""
    def __init__(self, data):
        super().__init__(data)
        self.set_plotting_parameters()

    def set_plotting_parameters(self):
        """Set the default contour plot parameters"""
        # Default parameters (alphabetical order)
        self.parameters["mask_conditions"] = None
        self.parameters["num_thin_lines"] = 5
        self.parameters["symlognorm_linear_width"] = 0.01
        self.parameters["thick_contour_line_thickness"] = 0.5
        self.parameters["thin_contour_line_thickness"] = 0.05

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

    def plot_contour(self, data_df, variable):
        """Plot contour"""
        if self.parameters["individual_colour_bar"]:
            self.vmin = self.colour_bar_centre - self.parameters["colour_range"] * (self.colour_bar_centre - self.colour_bar_min)
            self.vmax = self.colour_bar_centre + self.parameters["colour_range"] * (self.colour_bar_centre - self.colour_bar_min)
            
        self.linear_width = self.parameters["symlognorm_linear_width"] * (
            self.colour_bar_max - self.colour_bar_min
        )

        # Discrete colour values
        self.colour_levels = self.compute_levels(200)  # , logarithmic=True)
        
        # Values defining the contour lines
        self.contour_levels = self.compute_levels(50)  # , logarithmic=True)
        self.thick_contour_levels = self.contour_levels[
            :: self.parameters["num_thin_lines"]
        ]
        
        # Check in the csv file that the coordinates are labelled as follows
        Xi = data_df["Points:0"]
        Yi = data_df["Points:1"]

        # Make triangulation (taking into account any masking) for contour plot
        triangulation = self.generate_mask([Xi, Yi], self.parameters["mask_conditions"])
        
        if "magnitude" in variable:
            values = np.sqrt(data_df.iloc[:, 0]**2 + data_df.iloc[:, 1]**2 + data_df.iloc[:, 2]**2)
            
        else:
            values = data_df[variable]

        # Make contour plot
        contour = self.axs.tricontourf(
            triangulation,
            values,
            self.colour_levels,
            norm=colors.SymLogNorm(linthresh=self.linear_width, vmin=self.vmin, vmax=self.vmax),
            cmap=self.parameters["colour_map"],
        )
    
        # Remove the lines between filled regions (we add our own next)
        for c in self.axs.collections:
            c.set_edgecolor("face")
            
        # Add in contour lines
        self.axs.tricontour(
            Xi,
            Yi,
            values,
            self.thick_contour_levels,
            alpha=0.5,
            colors=["1."],
            linewidths=[self.parameters["thick_contour_line_thickness"]],
        )
        self.axs.tricontour(
            Xi,
            Yi,
            values,
            self.contour_levels,
            alpha=0.15,
            colors=["1."],
            linewidths=[self.parameters["thin_contour_line_thickness"]],
        )

        return contour
