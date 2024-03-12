import numpy as np

class LineStyles:
    """Class for controlling the style of lines in plots. The line styles are
    stored as numpy arrays with each line style consisting in the format
    [marker, colour, line style]."""
    def __init__(self, data, degree_id=None, variable=None, custom_style_dict={}):
        self.data = data
        self.degree_id = degree_id
        self.variable = variable
        self.markers = ["o", "x", "^", "v", "d", "+", "<", ">", "s", "*", "|", "_"]
        self.colours = ["#3C9359", "#FF8800", "#5CA7D9", "#B87D4B", "#336699", "#7D5BA6",
                   "blue", "orange", "green", "red", "purple", "pink"]
        self.lines = ["-", "--", ":", "-.", (0, (5, 5)), (0, (3, 5, 1, 5, 1, 5)), (0, (1, 10))]

        # CUSTOM STYLE DICT STUFF NEEDS SORTING

        if self.degree_id is not None:
            if self.variable is not None:
                self.context = "degree_variable"
            else:
                self.context = "degree"
        else:
            self.context = "variable"

        df_columns = next(iter(data.error_df_dict.values())).columns
        
        variable_list = []
        self.norm_list = []
        self.relevant_columns = []
        self.relevant_norm_list = []

        for column in df_columns:
            if column != "h" and column != "Time taken":
                # Assuming the ID is of the form "variable norm"
                variable = column.split(" ")[0]
                norm = column.split(" ")[1]

                variable_list.append(variable)
                self.norm_list.append(norm)

                if "variable" in self.context:
                    if self.variable + " " in column:
                        self.relevant_columns.append(column)
                        self.relevant_norm_list.append(norm)

        if self.context == "degree_variable":
            self.num_styles = len(df_columns) - 2  # NOT CORRECT ATM
        elif self.context == "degree":
            self.num_styles = len(df_columns) - 2  # Ignoring h and Time taken
        elif self.context == "variable":
            self.num_styles = len(self.data.error_df_dict)
            
        self.style_array = self.get_style_array()
        self.line_styles = self.get_line_styles(self.style_array)
        print(self.line_styles)

    def get_style_array(self):
        """Returns a numpy array containing the indexes [marker, colour, line style]"""
        # Initialise style array
        style_array = np.zeros((self.num_styles, len(self.relevant_columns), 3), dtype=int)
        
        # Fix line style for norms
        norm_dict = {}
        norm_counter = 0
        degree_index = 0
        style_index = 0
        
        for norm in self.relevant_norm_list:
            if norm not in norm_dict:
                style_array[:, style_index, 2] = norm_counter

                norm_counter += 1
            else:
                style_array[:, style_index, 2] = norm_dict[norm]
                
            style_index += 1

        # Loop over variables if the context is degree
        if self.context == "degree":
            variable_dict = {}
            style_index = 0
            marker_counter = 0
            colour_counter = 0
            
            for variable in variable_list:
                if variable not in variable_dict:
                    style_array[style_index, 0] = marker_counter
                    style_array[style_index, 1] = colour_counter
                    variable_dict[variable] = [marker_counter, colour_counter]
                    
                    marker_counter += 1
                    colour_counter += 1
                    
                else:
                    style_array[style_index, 0] = variable_dict[variable][0]
                    style_array[style_index, 1] = variable_dict[variable][1]
                    
                style_index += 1
                
            print(style_array)

        # Loop over polynomial degree if the context is variable
        if self.context == "variable":
            degree_id_dict = {}
            degree_index = 0
            self.styles_per_degree = len(self.relevant_columns)
            marker_counter = 0
            colour_counter = 0

            for degree_id in self.data.error_df_dict.keys():
                for style_index in range(self.styles_per_degree):
                    if degree_id not in degree_id_dict:
                        style_array[degree_index, style_index, 0] = marker_counter
                        style_array[degree_index, style_index, 1] = colour_counter
                        degree_id_dict[degree_id] = [marker_counter, colour_counter]
                        
                        marker_counter += 1
                        colour_counter += 1
                        
                    else:
                        style_array[degree_index, style_index, 0] = degree_id_dict[degree_id][0]
                        style_array[degree_index, style_index, 1] = degree_id_dict[degree_id][1]
                        
                    style_index += 1
                degree_index += 1
                 
        return style_array

    def colours_by_degree(self):
        colour_index_array = self.style_array[:, :, 1].flatten()
        colours_array = []

        for colour_index in colour_index_array:
            colours_array.append(self.colours[colour_index])

        colours_array = np.reshape(colours_array, (self.num_styles, self.styles_per_degree))
    
        return colours_array
    
    def line_styles_by_degree(self):
        marker_index_array = self.style_array[:, :, 0].flatten()
        style_index_array = self.style_array[:, :, 2].flatten()
        line_styles_array = []

        for i in range(len(marker_index_array)):
            line_styles_array.append(self.markers[marker_index_array[i]]
                                                  + self.lines[style_index_array[i]])

        line_styles_array = np.reshape(line_styles_array, (self.num_styles, self.styles_per_degree))
    
        return line_styles_array
    
    def get_line_styles(self, style_array):
        """Returns list of line styles"""
        line_styles = [[], [], [], []]
        for degree_index in range(self.num_styles):
            for style_index in range(self.styles_per_degree):
                line_styles[degree_index].append([self.markers[style_array[degree_index, style_index, 0]]
                                                  + self.lines[style_array[degree_index, style_index, 2]],
                                                  self.colours[style_array[degree_index, style_index, 1]]])

        return line_styles
        
