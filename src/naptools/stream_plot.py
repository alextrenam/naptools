import numpy as np
import matplotlib.pyplot as plt
from naptools import BaseData, BasePlot
import os


# THIS IS NOT IN WORKING ORDER YET


class StreamData(BaseData):
    """Class for holding and performing operations on stream plot data"""
    def __init__(self, data_file_dict):
        super().__init__(data_file_dict)
        self.stream_df_dict = self.data_df_dict


class StreamPlot(BasePlot):
    """Class for creating error plots based on the underlying error data"""
    def __init__(self, stream_data):
        super().__init__(stream_data)
        self.stream_data = self.data
        self.set_plotting_parameters()

    def set_plotting_parameters(self):
        """Set the default stream plot parameters"""
        # Default parameters (alphabetical order)
        self.parameters["arrow_sparsity"] = 1
        self.parameters["arrow_inverse_scale"] = None
        self.parameters["suppress_legend"] = True
        self.parameters["x_label"] = "$x$"
        self.parameters["y_label"] = "$y$"

        # SOME OF THESE SHOULD BE GENERIC PLOTTING PARAMETERS

        self.parameters["font_size"] = 32
        self.parameters["figure_height"] = 6.0
        self.parameters["figure_width"] = 6.0

    def plot(self, variable, timestamps, output_filename, parameters={}):
        """Create a single or series of contour plot(s)"""
        self.parameters.update(parameters)
        self.base_output_filename, self.file_extension = os.path.splitext(output_filename)

        series_counter = 0
        
        for timestamp in timestamps:
            self.output_filename = self.base_output_filename + "_" + timestamp + self.file_extension
            
            self.fig, self.axs = plt.subplots()
            data_df = self.stream_data.data_df_dict[timestamp]
            
            # Check in the csv file that paraview labels your x and y
            # coordinates with the following
            Xi = data_df["Points:0"][::self.parameters["arrow_sparsity"]]
            Yi = data_df["Points:1"][::self.parameters["arrow_sparsity"]]

            Ui = data_df[variable + ":0"][::self.parameters["arrow_sparsity"]]
            Vi = data_df[variable + ":1"][::self.parameters["arrow_sparsity"]]

            colouring = np.hypot(Ui, Vi)
            
            quiver = self.axs.quiver(
                Xi,
                Yi,
                Ui,
                Vi,
                colouring,
                scale=self.parameters["arrow_inverse_scale"],
            )
            
            # Remove axis ticks
            self.axs.tick_params(left=False,
                                 right=False,
                                 bottom=False,
                                 labelleft=False,
                                 labelbottom=False
                                 )
            
            self.output()

            series_counter += 1
        
    def output(self):
        """Format and output plot to file"""
        # plt.tick_params(labelsize=self.parameters["font_size"])
        self.fig.set_figheight(self.parameters["figure_height"])
        self.fig.set_figwidth(self.parameters["figure_width"])
        self.axs.axes.set_aspect("equal")

        super().output()
