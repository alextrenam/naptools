import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

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
        
        print(self.data)
        
        # # Populate dictionary of data
        # for data_file_id, data_file in self.data_file_dict.items():
        #     data_df = pd.read_csv(data_file)
        #     self.data_df_dict[data_file_id] = data_df
        
        # Initialise default plotting parameters (alphabetical order)
        self.parameters = {
            "custom_style_dict": {},
            "drop": [],
            "grid": False,
            "loglog": False,
            "semilog-x": False,
            "semilog-y": False,
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
            
        elif isinstance(data, np.ndarray):
            self.data[name] = pd.DataFrame(data)
            columns = ["Indep. Var."] + [f"Dep. Var. {index}" for index in range(1, self.data[name].shape[1])]
            self.data[name].columns = columns
            
        elif isinstance(data, list):
            self.data[name] = pd.DataFrame(data)
            columns = ["Indep. Var."] + [f"Dep. Var. {index}" for index in range(1, self.data[name].shape[1])]
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
        self.data[name].rename(columns=custom_labels_dict, inplace=True)
        
    def plot(self, output_filename, independent_var=None, dependent_vars=None, name=None, parameters={}):
        """Plot the given independent and dependent variables"""
        self.parameters.update(parameters)
        self.output_filename = output_filename
        self.fig, self.axs = plt.subplots()
      
        if name is not None:
            self.data[name].drop(
                axis=1,
                labels=self.parameters["drop"],
                inplace=True,
            )
            self.data[name].plot(independent_var, dependent_vars, ax=self.axs)
            
        else:
            for data_file, data_df in self.data.items():
                data_df.drop(
                    axis=1,
                    labels=self.parameters["drop"],
                    inplace=True,
                )
                data_df.plot(independent_var, dependent_vars, ax=self.axs)

        self.output(independent_var)

    def output(self, independent_var):
        """Format and output plot to file"""
        if self.parameters["x_label"] is not None:
            plt.xlabel(self.parameters["x_label"])

        else:
            plt.xlabel(independent_var)

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

        if self.parameters["loglog"]:
            plt.xscale("log")
            plt.yscale("log")

        if self.parameters["semilog-x"]:
            plt.xscale("log")

        if self.parameters["semilog-y"]:
            plt.yscale("log")

        if not self.parameters["suppress_legend"]:
            plt.legend()
