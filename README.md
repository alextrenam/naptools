# About
The Numerical Analysis Plotting Toolbox (NAPTools) is a package designed to speed up the generation of commonly-used numerical analysis plots (e.g. error convergence, solution snapshots). Built on matplotlib, the motivation is to minimise the amount of code the end-user needs to write but to still allow flexibility in the plots created. The package is a work in progress and is currently at an early stage of development with many features yet to be implemented. Users are encouraged to request desired features and submit pull requests for review. Thanks for being part of the process!

# Setup
To allow for local import from anywhere run the following command from the repository root directory:
`pip install .`

If you wish to edit the source code and test without needing to reinstall each time, run:
`pip install -e .`

# Version Roadmap
Here's what you can expect from the planned upcoming versions of the package:
- 0.5.0: Basic plots and error plots
- 0.6.0: Contour plots (e.g. for plotting solution profiles)
- 0.7.0: Legend manipulation
- 0.8.0: Multi-plots (on both a single and multiple axes)
- 0.9.0: Extended parameter set for easy customisation
- 1.0.0: All initial features implemented
