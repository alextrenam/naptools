import numpy as np


class LineStyles:
    """Class for controlling the style of lines in plots. The line styles are
    stored as numpy arrays with each line style consisting in the format
    [marker, colour, line style]."""
    def __init__(self, data, variables, degree_ids, drop=None, custom_style_dict={}):
        self.data = data
        if type(variables) is str:
            self.variables = [variables]
        else:
            self.variables = variables
        if type(degree_ids) is str:
            self.degree_ids = [degree_ids]
        else:
            self.degree_ids = degree_ids
        self.drop = drop
        self.markers = ["o", "x", "^", "v", "d", "+", "<", ">", "s", "*", "|", "_"]
        self.colours = ["#3C9359", "#FF8800", "#5CA7D9", "#B87D4B", "#336699", "#7D5BA6",
                   "blue", "orange", "green", "red", "purple", "pink"]
        self.lines = ["-", "--", ":", "-.", (0, (5, 5)), (0, (3, 5, 1, 5, 1, 5)), (0, (1, 10))]

        # Set default style and update if appropriate
        self.style_dict = {
            "marker": "variable",
            "colour": "degree",
            "line": "norm",
        }
        self.style_dict.update(custom_style_dict)

        self.variable_list = []
        self.norm_list = []
        self.relevant_columns = []
        self.relevant_norm_list = []
        self.relevant_variable_list = []

        df_columns = next(iter(data.error_df_dict.values())).columns

        for column in df_columns:
            if column != "h" and column != "Time taken" and column not in self.drop:
                # Assuming the ID is of the form "variable norm"
                variable = column.split(" ")[0]
                norm = column.split(" ")[1]

                self.variable_list.append(variable)
                self.norm_list.append(norm)

                for var in self.variables:
                    if var + " " in column:
                        self.relevant_columns.append(column)
                        self.relevant_norm_list.append(norm)
                        self.relevant_variable_list.append(variable)
                        
        # Set up dictionary for handling style controls
        self.controls_dict = {}
        
        for control_id, control in self.style_dict.items():
            if control == "degree":
                control_list = self.degree_ids
            elif control == "variable":
                control_list = self.variables
            elif control == "norm":
                control_list = self.norm_list
            
            self.controls_dict[control_id] = control_list

        self.marker_control_list = self.controls_dict["marker"]
        self.colour_control_list = self.controls_dict["colour"]
        self.line_control_list = self.controls_dict["line"]

        self.num_degrees = len(self.degree_ids)
        self.num_styles_per_degree = len(self.relevant_columns)
        
        self.style_array = self.get_style_array()
        self.line_styles = self.get_line_styles(self.style_array)

    def get_style_array(self):
        """Returns a numpy array containing the indexes [marker, colour, line style]"""
        # Initialise style array
        style_array = np.zeros((self.num_degrees, self.num_styles_per_degree, 3), dtype=int)
        
        # Loop over styles to populate style array
        for style in self.style_dict.keys():
            # Initialise some variables
            control_dict = {}
            counter = 0
            iterator = 0

            # Get correct column for given style ([marker, colour, line])
            if style == "marker":
                style_column_index = 0
            elif style == "colour":
                style_column_index = 1
            elif style == "line":
                style_column_index = 2

            # Set up tools for moving through iterations
            if self.style_dict[style] == "degree":
                degree_index = lambda: iterator
                row_index = lambda: slice(None)
                column_index = lambda: style_column_index
                control_list = self.degree_ids
                
            elif self.style_dict[style] == "variable":
                degree_index = lambda: slice(None)
                row_index = lambda: iterator
                column_index = lambda: style_column_index
                control_list = self.relevant_variable_list
                
            elif self.style_dict[style] == "norm":
                degree_index = lambda: slice(None)
                row_index = lambda: iterator
                column_index = lambda: style_column_index
                control_list = self.relevant_norm_list

            # Loop over controls to populate style array
            for control in control_list:
                if control not in control_dict:
                    style_array[degree_index(), row_index(), column_index()] = counter
                    control_dict[control] = counter
                    
                    counter += 1
                    
                else:
                    style_array[degree_index(), row_index(), column_index()] = control_dict[control]
                    
                iterator += 1

        return style_array
            
    def colours_by_degree(self):
        colour_index_array = self.style_array[:, :, 1].flatten()
        colours_array = []

        for colour_index in colour_index_array:
            colours_array.append(self.colours[colour_index])

        colours_array = np.reshape(colours_array, (self.num_degrees, self.num_styles_per_degree))
    
        return colours_array
    
    def line_styles_by_degree(self):
        marker_index_array = self.style_array[:, :, 0].flatten()
        style_index_array = self.style_array[:, :, 2].flatten()
        line_styles_array = []

        for i in range(len(marker_index_array)):
            line_styles_array.append(self.markers[marker_index_array[i]]
                                                  + self.lines[style_index_array[i]])

        line_styles_array = np.reshape(line_styles_array, (self.num_degrees, self.num_styles_per_degree))
    
        return line_styles_array
    
    def get_line_styles(self, style_array):
        """Returns list of line styles"""
        line_styles = [[] for x in range(self.num_degrees)]
        
        for degree_index in range(self.num_degrees):
            for style_index in range(self.num_styles_per_degree):
                line_styles[degree_index].append([self.markers[style_array[degree_index, style_index, 0]]
                                                  + self.lines[style_array[degree_index, style_index, 2]],
                                                  self.colours[style_array[degree_index, style_index, 1]]])

        return line_styles
        
