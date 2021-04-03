# History of changes

## Version 1.1.0 (4/3/20)
* Added groupmelodic runmode, for examining group ICAs.
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
