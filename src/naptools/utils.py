def get_loglog_slope(self, independent_var, dependent_var, all_data=False):
    """Returns the expected order of convergence (slope of the graph)
        -- either averaged over the curve, or just the final segment"""
    if all_data:
        # Calculate line slope for showing convergence rates on plot
        slope = stats.linregress(np.log2(independent_var),
                                 np.log2(dependent_var))[0]
        
    else:
        # Slope calculation using only the final two values
        slope = stats.linregress(np.log2(independent_var[-2:]),
                                 np.log2(dependent_var[-2:]))[0]
        
    return slope
