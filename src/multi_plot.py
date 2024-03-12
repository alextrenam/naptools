
class MultiPlot:
    """This class is a custom holder for multiple individual plots (useful if
    a single image with multiple plots, e.g. for making a video, is needed)"""
    def __init__(self, num_rows, num_columns):
        self.num_rows = num_rows
        self.num_columns = num_columns
        
    def plot(self, row_index, column_index, plot_type, data):
        """Creates an instance of Plot to populate the given MultiPlot element"""
        pass
