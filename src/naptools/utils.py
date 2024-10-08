import numpy as np
from scipy import stats


def get_loglog_slope(ind_var, dep_var, all_data=False):
    """Returns the expected order of convergence (slope of the graph)
    for loglog plot."""
    slope = get_slope(np.log(ind_var), np.log(dep_var), all_data)

    return slope


def get_semilogx_slope(ind_var, dep_var, all_data=False):
    """Returns the expected order of convergence (slope of the graph)
    for semilog-x plot."""
    slope = get_slope(np.log(ind_var), dep_var, all_data)
    
    return slope


def get_semilogy_slope(ind_var, dep_var, all_data=False):
    """Returns the expected order of convergence (slope of the graph)
    for semilog-y plot."""
    slope = get_slope(ind_var, np.log(dep_var), all_data)
    
    return slope


def get_slope(scaled_ind_var, scaled_dep_var, all_data=False):
    """Returns the expected order of convergence (slope of the graph)
    -- either averaged over the curve, or just the final segment.
    The scaling is taken into account (e.g. semi-log, log-log, etc)
    in the function which calls this function."""
    if all_data:
        index_string = "slice(None)"

    else:
        index_string = "slice(-2, None)"
        
    # Calculate line slope for showing convergence rates on plot
    slope = stats.linregress(scaled_ind_var[eval(index_string)],
                             scaled_dep_var[eval(index_string)])[0]
        
    return slope


def calculate_slope(ind_var, dep_var, scale_axes):
    match scale_axes:
        case "log-log":
            slope = get_loglog_slope(ind_var, dep_var)
            
        case "semilog-x":
            slope = get_semilogx_slope(ind_var, dep_var)
                            
        case "semilog-y":
            slope = get_semilogy_slope(ind_var, dep_var)
                            
        case _:
            slope = get_slope(ind_var, dep_var)
                    
    return slope
