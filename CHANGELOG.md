# History of changes

## Version 1.4.4 (6/29/23)
* Fixed image pane resizing.

## Version 1.4.3 (6/9/23)
* Added reference file matching - if you specify a set of reference components, any IC with a spatial correlation with any reference component above a threshold is retained.

## Version 1.4.2 (5/11/23)
* (Docker) Updated to python 3.11 basecontainer.
* (package) Modernized install procedure.

## Version 1.4.1 (2/14/23)
* Upgraded pyqtgraph calls to handle deprecations.  NOTE: this only handles versions of pyqtgraph<0.13.
* Made substantial changes to the Dockerfile to handle changes in basecontainer.

## Version 1.4.0 (2/9/23)
* Added --version and --detailedversion command line flags to PICAchooser, melodicomp, and grader.
* Accepted several PR's from dependabot for build scripts.
* Updated versioneer.
* Renamed master branch to main.
* Adapted to the new basecontainer.

## Version 1.3.1.2 (8/19/22)
* Updated Dockerfile for a newer python distribution.

## Version 1.3.1.1 (8/19/22)
* Updated versioneer.

## Version 1.3.1 (8/19/22)
* Tweaked pyproject.ml file to hopefully fix documentation build.

## Version 1.3.0 (9/8/21)
* Reformatted with black and isort.
* Flipped x axis to display radiological coordinates.
* Harmonized Dockerfile and automated container building methods with rapidtide.
* Fixed some formatting in documentation (thank you DMD!)

## Version 1.2.3 (4/6/20)
* Major documentation improvements.
* Finally fixed picachooser.readthedocs.org.
* Added reset component keystroke to PICAchooser and melodicomp.

## Version 1.2.2 (4/5/20)
* More fiddling to get deplyment working again.

## Version 1.2.1 (4/5/20)
* Fiddled with .gitignore to try to get deplyment working again.
* Added a help line to the bottom of grader GUI window.

## Version 1.2.0 (4/5/20)
* Added a new program - melodicomp - to compare ICs between runs.
* Added a help line to the bottom of GUI windows.

## Version 1.1.4 (4/3/20)
* Now with pypi!  Just ``pip install picachooser``, and off you go!

## Version 1.1.0 (4/3/20)
* Added groupmelodic runmode, for examining group ICAs.
* Added the ability to select an ROI from the dataset.
* General code cleanup, reformatting with black.
* Updated documentation.

## Version 1.0.2 (11/24/20)
* Added line to help QT compatibility with macOS 11 (Big Sur).

## Version 1.0.1 (6/30/20)
* Just bumping the version number to generate an initial Zenodo DOI.

## Version 1.0.0 (6/3/20)
* Motion correlation parameters are now properly output to the terminal when switching components.
* Turned down default verbosity.

## Version 1.0.0rc13 (6/1/20)
* You can now switch to viewing slices in axial, coronal, or sagittal orientation by pressing the a, c, or s key.
* Fixed the aspect ratio and padding of the images in the display window.

## Version 1.0.0rc12 (5/21/20)
* The explained variance and total variance of the component are now displayed in the title bar of the window.

## Version 1.0.0rc11 (5/15/20)
* Properly handle the case of the timecourses being shorter than the motion plots (happens when fMRIprep discards (but doesn't really discard) initial timepoints).
* Window resizing works somewhat better (but it's not perfect yet).

## Version 1.0.0rc10 (5/7/20)
* All plot linewidths are now settable from the command line.
* Added the --scalemotiontodata option to autoscale motion plots (rather than setting the plot limits by the dashed guide lines.)

## Version 1.0.0rc9 (4/27/20)
* keepcolor, discardcolor, transmotlimits and rotmotlimits are now settable via command line arguments.  This means docker users can change configuration values.
* Increased some linewidths to make the display more readable, made the widths settable in the config file.

## Version 1.0.0rc8 (4/27/20)
* Added fixed (but configurable) "normal" limits to motion plots (thank you to Richard Dinga for the suggestion).

## Version 1.0.0rc7 (4/26/20)
* Revamped input file specification to allow for maximum flexibility
* PICAchooser can now read motion out of fmriprep confounds files.
* On bad component file save, print the command needed to refilter the dataset.

## Version 1.0.0rc6 (4/25/20)
* Updated the run options for docker and singularity to reflect the current interface

## Version 1.0.0rc5 (4/25/20)
* All timecourse colors are now changeable by editing the ${HOME}/.picachooser.json file (the file is created with default values if it doesn't exist).
* Numerous documentation fixes and updates

## Version 1.0.0rc4 (4/25/20)
* Changed help lines to match actual runmode names
* Calculate and print correlation coefficients (and p values) between current component and all motion timecourses

## Version 1.0.0rc3 (4/24/20)
* Changed option specification
* Added configuration file to set colors

## Version 1.0.0rc2 (4/24/20)
* Fixed docker build issues
* Timecourse and spectrum window now show the component number
* Resolved remaining rapidtide dependencies
* Still having problems with readthedocs

## Version 1.0.0rc1 (4/23/20)
* Initial release
