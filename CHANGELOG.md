# History of changes

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
