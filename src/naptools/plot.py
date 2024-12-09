import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
# from naptools import LineStyles, utils
from naptools import utils

# Default style parameters
naptools_dir_path = os.path.dirname(os.path.realpath(__file__))
plt.style.use(naptools_dir_path + "/naptools_default.mplstyle")


class Plot:
    """Basic two-dimensional plot with one independent and one dependent variable.
    This class is also the basis for the other kinds of plots, featuring the general
    structure of: __init__(), draw(), output()."""

    def __init__(self, data, name="default"):
        """
        Initialize a dictionary of DataFrames based on the type of the input data.
        
        :param data: Can be a single dataset (string, array, numpy array, pandas DataFrame), 
                     a collection of datasets (list of arrays, list of dataframes), 
                     or a dictionary of datasets (dictionary with values as data and keys as names).
        :param name: The name to store the DataFrame in the internal dictionary. 
                     Defaults to "default". If data is a collection or dictionary, keys or indices will be used.
        """
        self.data = {}
        self.add_data(data, name)
        
        # Initialise default plotting parameters (alphabetical order)
        self.parameters = {
            "custom_labels": {},
            "custom_style_dict": {},
            "drop": [],
            "grid": False,
            "include_slopes": False,
            "scale_axes": None,
            "suppress_legend": False,
            "x_label": None,
            "y_label": None,
        }

    def add_data(self, data, name):
        """Detect the type of data and add it to the dictionary."""
        if isinstance(data, dict):
            # If the input is a dictionary, process each key-value pair
            for key, dataset in data.items():
                self.add_single_dataset(dataset, key)
                
        elif isinstance(data, np.ndarray) or isinstance(data, list):
            # Check if it's a collection of datasets (e.g. list of lists, list of arrays)
            if all(isinstance(d, (list, np.ndarray, pd.DataFrame)) for d in data):
                # It's a collection, iterate through and add each
                for idx, dataset in enumerate(data):
                    self.add_single_dataset(dataset, f"{name}_{idx}")
                    
            else:
                # It's a single dataset (list or array), treat it as such
                self.add_single_dataset(data, name)
                
        else:
            self.add_single_dataset(data, name)

    def add_single_dataset(self, data, name):
        """Helper method to add a single dataset as a DataFrame."""
        if isinstance(data, pd.DataFrame):
            self.data[name] = data

        elif isinstance(data, dict):
            self.data[name] = pd.DataFrame(data)
            
        elif isinstance(data, np.ndarray):
            self.data[name] = pd.DataFrame(data)
            columns = ["Ind. Var."] + [f"Dep. Var. {index}" for index in range(1, self.data[name].shape[1])]
            self.data[name].columns = columns
            
        elif isinstance(data, list):
            self.data[name] = pd.DataFrame(data)
            columns = ["Ind. Var."] + [f"Dep. Var. {index}" for index in range(1, self.data[name].shape[1])]
            self.data[name].columns = columns

        elif isinstance(data, str):
            # If the data is a string, assume it's a CSV file path and load it
            if os.path.isfile(data):
                try:
                    self.data[name] = pd.read_csv(data)
                    
                except Exception as e:
                    raise ValueError(f"Error reading file {data}: {e}")
                
            else:
                raise ValueError(f"Invalid file path: {data}")

        else:
            raise TypeError(f"Unsupported data type in collection: {type(data)}")

    def get_data(self, name):
        """Return the DataFrame stored as name."""
        return self.data.get(name, None)

    def remove_data(self, name):
        """Remove the DataFrame stored as name."""
        if name in self.dataframes:
            del self.data[name]
            
        else:
            raise KeyError(f"No data found with name: {name}")

    def list_data(self):
        """List all stored data names."""
        return list(self.data.keys())
    
    def print_data(self, name):
        """Print name and the DataFrame name."""
        print(f"\n{name}\n{self.data[name]}")

    def update_labels(self, name, custom_labels_dict):
        """Update labels for plotting."""
        
        
    def plot(self, output_filename, ind_var=None, dep_vars=None, names=None, parameters={}):
        """Plot the given independent and dependent variables"""
        self.parameters.update(parameters)
        self.output_filename = output_filename
        self.fig, self.axs = plt.subplots()
      
        if isinstance(dep_vars, str):
            dep_vars = [dep_vars]

        if isinstance(names, str):
            names = [names]

        if names is None:
            names = self.data.keys()

        # line_styles = LineStyles(self.data, dependent_var, names,
        #                          drop=self.parameters["drop"],
        #                          custom_style_dict=self.parameters["custom_style_dict"])
        # styles = line_styles.line_styles_by_degree()
        # colours = line_styles.colours_by_degree()
        # style_degree_index = 0
        
        for name in names:
            plotting_df = self.data[name].copy(deep=True)  # .set_index(ind_var)
            
            # Drop unnecessary columns
            drop_columns = []

            for column in list(plotting_df.columns.values):
                if (ind_var is not None and column not in ind_var) and (
                    (dep_vars is not None and column not in dep_vars)
                    or (column in self.parameters["drop"])):
                    drop_columns.append(column)
            
            try:
                plotting_df.drop(
                    axis=1,
                    labels=drop_columns,
                    inplace=True,
                    )
            except Exception as e:
                print(f"Exception: {e}. Unable to drop columns -- check they have not been relabelled or already removed.")
                
            if name in self.parameters["custom_labels"].keys():
                # Update custom labels
                plotting_df.rename(columns=self.parameters["custom_labels"][name], inplace=True)
                
            if ind_var is None:
                plotting_dep_vars = plotting_df.columns

            else:
                # Get all columns except the independent variable
                ind_var_index = plotting_df.columns.get_loc(ind_var)
                plotting_dep_vars = plotting_df.columns.delete(ind_var_index)
                
                if self.parameters["include_slopes"]:
                    renaming_columns = {}
                    
                    for dep_var in plotting_dep_vars:
                        # Calculate slope and relabel the columns to include
                        slope = utils.calculate_slope(plotting_df[ind_var], plotting_df[dep_var], self.parameters["scale_axes"])
                        renaming_columns[dep_var] = f"{dep_var}, Slope: {slope:.3f}" 
            
                    # Rename columns for correct plot labels
                    plotting_df.rename(columns=renaming_columns, inplace=True)

                # Get updated plotting variables columns
                plotting_dep_vars = plotting_df.columns.delete(ind_var_index)
                
            # Create plot
            plotting_df.plot(ind_var, plotting_dep_vars, ax=self.axs)
            
            # plotting_df.plot(ax=self.axs, style=list(styles[style_degree_index]), color=list(colours[style_degree_index]))
            # style_degree_index += 1

        self.output(ind_var)

    def output(self, ind_var):
        """Format and output plot to file"""
        if self.parameters["x_label"] is not None:
            plt.xlabel(self.parameters["x_label"])

        else:
            plt.xlabel(ind_var)

        if self.parameters["y_label"] is not None:
            plt.ylabel(self.parameters["y_label"])
        
        self.resolve_parameters()
        # self.fig.tight_layout() #INCLUDED IN SAVEFIG BELOW

        os.makedirs(os.path.dirname(self.output_filename), exist_ok=True)
        plt.savefig(self.output_filename, bbox_inches="tight")
        plt.close()
        print(f"Results plotted as: {self.output_filename}")

    def resolve_parameters(self):
        """Act on parameter values to modify plot appearance"""
        
        
        if self.parameters["grid"]:
            plt.grid(which="both", color="#cfcfcf")

        match self.parameters["scale_axes"]:
            case "log-log":
                plt.xscale("log")
                plt.yscale("log")

            case "semilog-x":
                plt.xscale("log")

            case "semilog-y":
                plt.yscale("log")

            case _:
                pass

        if not self.parameters["suppress_legend"]:
            plt.legend()
