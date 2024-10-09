from naptools import Plot
"""
The power module provides functions for rapid plotting without the need to
expliictly create instances of the underlying Plot classes.
"""

def plot(**data):
    if "output_filename" in data.keys():
        output_filename = data["output_filename"]

    else:
        raise ValueError("No output file name provided.")
    
    del data["output_filename"]
    data_dict = {"Input data": data}
    print(data_dict)
    output_plot = Plot(data_dict)

    output_plot.print_data("Input data")
    output_plot.plot(output_filename)

# def plot(*data, output_filename):
#     input_data_dict = {}
#     index = 1
#     for item in data:
#         input_data_dict[f"Data {index}"] = item
#         index += 1
        
#     data_dict = {"Input data": input_data_dict}
#     output_plot = Plot(data_dict)

#     output_plot.print_data("Input data")
#     output_plot.plot(output_filename)
