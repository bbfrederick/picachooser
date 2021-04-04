PICAchooser
===========

A simple gui tool for scanning through MELODIC probabalistic ICA runs
and quickly making decisions about which components to retain. This tool
does one thing, but it does it quickly and easily using only keyboard
input.

Basically, PICAchooser loads the results of a MELODIC ICA run and lets
you step through the components, look at them, and decide if you want to
keep them or discard them. After you load the dataset, you get a window
showing the active IC component (both the timecourse and the spatial
map), the power spectrum of the active IC component, and the motion
timecourses for comparison. By default, components are flagged to be
kept (and the timecourses are in green\*).

Usage
-----

`usage: PICAchooser runmode [options]`

A program to review (and alter) melodic component selections.

positional arguments:

runmode. Valid choices are "melodic", "groupmelodic", "aroma", and
"fix".

In melodic mode, the default output file is named "badcomponents.txt";
components flagged for removal will be written to MELODICDIR as comma
separated integers. Component numbers start at 1 (for compatibility with
fsl\_regfilt).

In groupmelodic mode, the default output file is named
"goodcomponents.txt"; components which are worth keeping will be written
to MELODICDIR as integers, one per line. Component numbers start at 0
(for compatibility with standard NIFTI array indexing).

In aroma mode, the file "classified\_motion\_ICs.txt" must exist in the
parent of MELODICDIR; by default the output will be written to
"classified\_motion\_ICs\_revised.txt" in the same directory. Component
numbers start at 1 (for compatibility with AROMA numbering convention).

In fix mode, the default output file is named "hand\_labels\_noise.txt"
and will be written to MELODICDIR as comma separated integers with
square brackets surrounding the line. Component numbers start at 1 (for
compatibility with FIX numbering convention).

optional arguments: -h, --help show this help message and exit

Standard input file location specification:

`--featdir FEATDIR` The FEAT directory associated with this MELODIC run.

`--melodicdir MELODICDIR` The .ica directory for this MELODIC run.

Nonstandard input file location specification: --backgroundfile BGFILE
The anatomic file on which to display the ICs (usually found in
FEATDIR/reg/example\_func.nii.gz), --funcfile FUNCFILE The functional
file to be filtered (usually found in
FEATDIR/filtered\_func\_data.nii.gz), --motionfile MOTIONFILE The
anatomic file on which to display the ICs (usually found in
FEATDIR/mc/prefiltered\_func\_data\_mcf.par). If the file has a .tsv
extension, assume it is an fmriprep confounds file. --ICfile ICFILE The
independent component file produced by MELODIC (usually found in
MELODICDIR/melodic\_IC.nii.gz). --ICmask ICMASK The independent
component mask file produced by MELODIC (usually found in
MELODICDIR/mask.nii.gz). --timecoursefile MIXFILE The timecourses of the
independant components (usually found in MELODICDIR/melodic\_mix),

Other arguments: --initfile INITFILE The name of an initial bad
component file (in aroma mode, this overrides the default input file for
AROMA). --outputfile OUTPUTFILE Where to write the bad component file
(this overrides the default output file name). --filteredfile
FILTEREDFILE The name of the filtered NIFTI file. If this is set, then
when the bad component file is written, the command to generate the
filtered file will be printed to the terminal window. --displaythresh
DISPLAYTHRESH z threshold for the displayed ICA components. Default is
2.3.

Configuration arguments: --keepcolor KEEPCOLOR Set the color of
timecourses to be kept (default is "g"). --discardcolor DISCARDCOLOR Set
the color of timecourses to discard (default is "r"). --transmotlimits
LOWERLIM UPPERLIM Override the "normal" limits of translational motion
from the values in the configuration file to LOWERLIM-UPPERLIM mm.
--rotmotlimits LOWERLIM UPPERLIM Override the "normal" limits of
rotations motion from the values in the configuration file to
LOWERLIM-UPPERLIM radians. --scalemotiontodata Scale motion plots to the
motion timecourse values rather than to the limit lines.
--componentlinewidth LINEWIDTH Override the component line width (in
pixels) in the configuration file with LINEWIDTH. --motionlinewidth
LINEWIDTH Override the motion timecourse line widths (in pixels) in the
configuration file with LINEWIDTH. --motionlimitlinewidth LINEWIDTH
Override the line widths of the motion limit lines (in pixels) in the
configuration file with LINEWIDTH. \`\`\`

You'll then get a window that looks like this:

![PICAchooser
screenshot](https://github.com/bbfrederick/picachooser/blob/master/images/picachooser_screenshot2.png)

Controls
========

To toggle whether the current component should be kept or discarded,
press the up or down arrow key. You can change back and forth as much as
you want. Components to be discarded are in red, ones to be kept are in
green\*.

To go to the next (or previous) component, press the right (or left)
arrow. You'll wrap around if you hit the end.

Press the escape key at any time to save the current version of the
component list. The component list is saved automatically when you quit.

Input file specification
------------------------

For most datasets, you only need to specify the FEAT directory where the
preprocessing was done, and the MELODIC directory where the ICA analysis
was performed, and PICAchooser can find all the files it needs to let
you do component selection. In some cases, however (looking at you,
fmriprep), the files you need to find can be scattered all over the
place, with different names (and even different formats). In those
cases, you can specify the name and location of every one of the files
separately (anything you set with these options will override the
default locations calculated from the FEATDIR and MELODICDIR).

Other command line options
--------------------------

`--initfile` lets you read in a bad component file from anywhere to use
as a starting point in your classification. It's the normal behavior in
aroma mode (reading from MELODICDIR/../classified\_motion\_ICs.txt), but
you can do it in any mode with this flag, and it will override the aroma
classifications.

`--outputfile` lets you write the bad component file anywhere you want,
rather than just the default location.

`--filteredfile` specifies where the filtered file would go. If this is
set, PICAchooser prints the fsl\_regfilt command to filter the data
using the currently tagged bad components whenever the file is saved
(when the escape key is pressed, or when you quit).

`--displaythresh` sets the z-threshold for the component maps.

`--spatialroi XMIN XMAX YMIN YMAX ZMIN ZMAX` lets you zoom in on a cubic
ROI within the NIFTI dataset. Useful if you did a constrained ICA on a
particular brain region. Set the MAX value to -1 to go to the maximum
value for a given dimension. These are voxel indices, with 0 being the
first element of each dimension.

\* Configuration changes
------------------------

You can use `--keepcolor`, `--discardcolor`, `--transmotlimits` and
`--rotmotlimits` to alter display behavior for the current run (useful
if you're using the docker container). To change things
semi-permanently, edit the file \${HOME}/.picachooser.json. This file is
created with default values if it is not present. You can use any valid
python color specification string for color values, e.g. "r", "ff0000",
or "FF0000" could all be used for red.

`--componentlinewidth`, `--motionlinewidth`, and
`--motionlimitlinewidth` can all be used to specify various linewidths
(in pixels) for the various plots. Useful if you want to make a
screenshot pretty for a figure.

`--scalemotiontodata` autoscales the motion plots to the motion
timecourse values rather than to fixed limits.

The motion plots have two dotted lines to indicate "normal" motion
limits (by default +/-2.5 mm for translation and +/-0.04 radians for
rotation). The locations of these lines are set by "transmotlimits" and
"rotmotlimits" in the configuration file. Setting "motionplotstyle" to 0
will remove the lines, and fix the y range of the plots to the limit
values. Set the limit line color using "motionlimitcolor".

Reprocessing fmriprep AROMA analyses
====================================

fmriprep reformats things to conform to BIDS standard naming conventions
and formatting, so file locations, names, and formats are a little
weird. However, you can check components as long as you used an external
work directory (you set the "-w" flag during analysis).

A concrete example: I have an analysis in BIDSDIR, and used the option
"-w WORKDIR" when I ran fmriprep (with AROMA processing enabled). Say I
have a functional run, sub-015\_ses-001\_task-rest\_run-1\_bold.nii.gz
that I want to redo the AROMA processing on. First off, I need to find
my ICfile and IC mask file. They don't get copied into the derivatives
directory, as they are intermediate files, not analysis products. It
turns out the entire melodic directory does exist in the work directory.
In this particular case, if I set:

`--melodicdir ${WORKDIR}/fmriprep_wf/single_subject_015_wf/func_preproc_ses_001_task_rest_run_1_wf/ica_aroma_wf/melodic`

then PICAchooser can find the ICfile and ICmask.

The background file is also in this directory:

`--backgroundfile ${WORKDIR}/fmriprep_wf/single_subject_015_wf/func_preproc_ses_001_task_rest_run_1_wf/ica_aroma_wf/melodic/mean.nii.gz`

Everything else can be found in the functional output directory for this
session:

`FUNCDIR=${BIDSDIR}/derivatives/fmriprep/sub-015/ses-001/func`

By setting the following options:

`--initfile ${FUNCDIR}/sub-015_ses-001_task-rest_run-1_AROMAnoiseICs.csv --funcfile ${FUNCDIR}/sub-015_ses-001_task-rest_run-1_space-MNI152NLin6Asym_desc-preproc_bold.nii.gz --motionfile ${FUNCDIR}/sub-015_ses-001_task-rest_run-1_desc-confounds_regressors.tsv`

As a bonus, if you also set:

`--filteredfile ${FUNCDIR}/sub-015_ses-001_task-rest_run-1_space-MNI152NLin6Asym_desc-AROMAnonaggr_bold.nii.gz`

Then when you save your bad component file, you'll see the command
necessary to refilter your data printed to the terminal window. I
haven't investigated far enough to know when the smoothing implied in
the name of the exisiting filtered file comes from, so there may be some
other steps to get to exactly the output you'd get from fmriprep...

Support
=======

This code base is being developed and supported by a grant from the US
NIH [1R01 NS097512](http://grantome.com/grant/NIH/R01-NS097512-02).

Additional packages used
========================

PICAchooser would not be possible without many additional open source
packages. These include:

pyqtgraph:
----------

1)  Luke Campagnola. [PyQtGraph: Scientific Graphics and GUI Library for
    Python](http://www.pyqtgraph.org)

nibabel:
--------

1)  [Nibabel: Python package to access a cacophony of neuro-imaging file
    formats](https://github.com/nipy/nibabel) |
    <https://10.5281/zenodo.591597>

numpy:
------

1)  Stéfan van der Walt, S. Chris Colbert and Gaël Varoquaux. The NumPy
    Array: A Structure for Efficient Numerical Computation, Computing in
    Science & Engineering, 13, 22-30 (2011) |
    <https:10.1109/MCSE.2011.37>

scipy:
------

1)  Pauli Virtanen, Ralf Gommers, Travis E. Oliphant, Matt Haberland,
    Tyler Reddy, David Cournapeau, Evgeni Burovski, Pearu Peterson,
    Warren Weckesser, Jonathan Bright, Stéfan J. van der Walt, Matthew
    Brett, Joshua Wilson, K. Jarrod Millman, Nikolay Mayorov, Andrew R.
    J. Nelson, Eric Jones, Robert Kern, Eric Larson, CJ Carey, İlhan
    Polat, Yu Feng, Eric W. Moore, Jake VanderPlas, Denis Laxalde, Josef
    Perktold, Robert Cimrman, Ian Henriksen, E.A. Quintero, Charles R
    Harris, Anne M. Archibald, Antônio H. Ribeiro, Fabian Pedregosa,
    Paul van Mulbregt, and SciPy 1.0 Contributors. (2020) SciPy 1.0:
    Fundamental Algorithms for Scientific Computing in Python. Nature
    Methods, 17, 261–272 (2020) |
    <https://doi.org/10.1038/s41592-019-0686-2>

pandas:
-------

1)  McKinney, W., pandas: a foundational Python library for data
    analysis and statistics. Python for High Performance and Scientific
    Computing,
    2011. 14.


