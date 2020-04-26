# PICAchooser

A simple gui tool for scanning through MELODIC probabalistic ICA runs and quickly making decisions about which components to retain.  This tool does one thing, but it does it quickly and easily using only keyboard input.

Basically, PICAchooser loads the results of a MELODIC ICA run and lets you step through the components, look at them, and decide if you want to keep them or discard them.  After you load the dataset, you get a window showing the active IC component (both the timecourse and the spatial map), the power spectrum of the active IC component, and the motion timecourses for comparison.  By default, components are flagged to be kept (and the timecourses are in green*).


## Usage

``` bash
usage: PICAchooser runmode [options]

A program to review (and alter) melodic component selections.

positional arguments:
  runmode               Analysis mode. Valid choices are "melodic", "aroma", and "fix". In melodic mode,
                        the default output file is named "badcomponents.txt" and will be written to
                        MELODICDIR as comma separated integers. In aroma mode, the file
                        "classified_motion_ICs.txt" must exist in the parent of MELODICDIR; by default
                        the output will be written to "classified_motion_ICs_revised.txt" in the same
                        directory. In fix mode, the default output file is named "hand_labels_noise.txt"
                        and will be written to MELODICDIR as comma separated integers with square
                        brackets surrounding the line.

optional arguments:
  -h, --help            show this help message and exit

Standard input file location specification:
  --featdir FEATDIR     The FEAT directory associated with this MELODIC run.
  --melodicdir MELODICDIR
                        The .ica directory for this MELODIC run.

Nonstandard input file location specification:
  --backgroundfile BGFILE
                        The anatomic file on which to display the ICs (usually found in
                        FEATDIR/reg/example_func.nii.gz),
  --funcfile FUNCFILE   The functional file to be filtered (usually found in
                        FEATDIR/filtered_func_data.nii.gz),
  --motionfile MOTIONFILE
                        The anatomic file on which to display the ICs (usually found in
                        FEATDIR/mc/prefiltered_func_data_mcf.par
  --ICfile ICFILE       The independent component file produced by MELODIC (usually found in
                        MELODICDIR/melodic_IC.nii.gz).
  --ICmask ICMASK       The independent component mask file produced by MELODIC (usually found in
                        MELODICDIR/mask.nii.gz).
  --timecoursefile MIXFILE
                        The timecourses of the independant components (usually found in
                        MELODICDIR/melodic_mix),

Other arguments:
  --initfile INITFILE   The name of an initial bad component file (in aroma mode, this overrides the
                        default input file for AROMA).
  --outputfile OUTPUTFILE
                        Where to write the bad component file (this overrides the default output file
                        name).
  --filteredfile FILTEREDFILE
                        The name of the filtered NIFTI file. If this is set, then when the bad component
                        file is written, the command to generate the filtered file will be printed to
                        the terminal window.
  --displaythresh DISPLAYTHRESH
                        z threshold for the displayed ICA components. Default is 2.3.
```

You'll then get a window that looks like this:

![PICAchooser screenshot](https://github.com/bbfrederick/picachooser/blob/master/images/picachooser_screenshot.png)

# Controls

To toggle whether the current component should be kept or discarded, press the up or down arrow key.  You can change back and forth as much as you want. Components to be discarded are in red, ones to be kept are in green*.

To go to the next (or previous) component, press the right (or left) arrow.  You'll wrap around if you hit the end.

Press the escape key at any time to save the current version of the component list.  The component list is saved automatically when you quit.


## Input file specification

For most datasets, you only need to specify the FEAT directory where the preprocessing was done, and the MELODIC directory where the ICA analysis was performed, and PICAchooser can find all the files it needs to let you do component selection.  In some cases, however (looking at you, fmriprep), the files you need to find can be scattered all over the place, with different names (and even different formats). In those cases, you can specify the name and location of every one of the files separately (anything you set with these options will override the default locations calculated from the FEATDIR and MELODICDIR).


## Options

`--initfile` lets you read in a bad component file from anywhere to use as a starting point in your classification.  It's the normal behavior in aroma mode (reading from MELODICDIR/../classified_motion_ICs.txt), but you can do it in any mode with this flag, and it will override the aroma classifications.

`--outputfile` lets you write the bad component file anywhere you want, rather than just the default location.

`--filteredfile` specifies where the filtered file would go.  If this is set, PICAchooser prints the fsl_regfilt command to filter the data using the currently tagged bad components whenever the file is saved (when the escape key is pressed, or when you quit).

`--displaythresh` sets the z-threshold for the component maps.

\* You can override the default keepcolor and discardcolor (and the colors for all the motion timecourses) by editing the file ${HOME}/.picachooser.json. This file is created is created with default values if it is not present.  You can use any valid python color specification string, e.g. "r", "ff0000", or "FF0000" could all be used for red.


# fmriprep

fmriprep reformats things to conform to BIDS standard naming conventions and formatting, so file locations, names, and formats are a little weird.  However, you can check components as long as you used an external work directory (you set the "-w" flag during analysis).

A concrete example:  I have an analysis in BIDSDIR, and used the option "-w WORKDIR" when I ran fmriprep (with AROMA processing enabled).  Say I have a functional run, sub-015_ses-001_task-rest_run-1_bold.nii.gz that I want to redo the AROMA processing on.
First off, I need to find my ICfile and IC mask file.  They don't get copied into the derivatives directory, as they are intermediate files, not analysis products.  It turns out the entire melodic directory does exist in the work directory.  In this particular case, if I set:

`--melodicdir ${WORKDIR}/fmriprep_wf/single_subject_015_wf/func_preproc_ses_001_task_rest_run_1_wf/ica_aroma_wf/melodic`

then PICAchooser can find the ICfile and ICmask.

The background file is also in this directory:

`--backgroundfile ${WORKDIR}/fmriprep_wf/single_subject_015_wf/func_preproc_ses_001_task_rest_run_1_wf/ica_aroma_wf/melodic/mean.nii.gz`

Everything else can be found in the functional output file for this:

`FUNCDIR=${BIDSDIR}/derivatives/fmriprep/sub-015/ses-001/func`

By setting the following options:

`--initfile ${FUNCDIR}/sub-015_ses-001_task-rest_run-1_AROMAnoiseICs.csv
--funcfile ${FUNCDIR}/sub-015_ses-001_task-rest_run-1_space-MNI152NLin6Asym_desc-preproc_bold.nii.gz
--motionfile ${FUNCDIR}/sub-015_ses-001_task-rest_run-1_desc-confounds_regressors.tsv`

As a bonus, if you also set:

`--filteredfile ${FUNCDIR}/sub-015_ses-001_task-rest_run-1_space-MNI152NLin6Asym_desc-AROMAnonaggr_bold.nii.gz`

Then when you save your bad component file, you'll see the command necessary to refilter your data printed to the terminal window.  I haven't investigated far enough to know when the smoothing implied in the name of the exisiting filtered file comes from, so there may be some other steps to get to exactly the output you'd get from fmriprep...

# Support

This code base is being developed and supported by a grant from the US
NIH [1R01 NS097512](http://grantome.com/grant/NIH/R01-NS097512-02).

# Additional packages used

PICAchooser would not be possible without many additional open source packages.
These include:

## pyqtgraph:

1) Luke Campagnola. [PyQtGraph: Scientific Graphics and GUI Library for Python](http://www.pyqtgraph.org)

## nibabel:

1) [Nibabel: Python package to access a cacophony of neuro-imaging file formats](https://github.com/nipy/nibabel) \| https://10.5281/zenodo.591597

## numpy:

1) Stéfan van der Walt, S. Chris Colbert and Gaël Varoquaux. The NumPy Array:
   A Structure for Efficient Numerical Computation, Computing in Science
   & Engineering, 13, 22-30 (2011) \| https:10.1109/MCSE.2011.37

## scipy:

1) Pauli Virtanen, Ralf Gommers, Travis E. Oliphant, Matt Haberland, Tyler Reddy,
   David Cournapeau, Evgeni Burovski, Pearu Peterson, Warren Weckesser,
   Jonathan Bright, Stéfan J. van der Walt, Matthew Brett, Joshua Wilson,
   K. Jarrod Millman, Nikolay Mayorov, Andrew R. J. Nelson, Eric Jones,
   Robert Kern, Eric Larson, CJ Carey, İlhan Polat, Yu Feng, Eric W. Moore,
   Jake VanderPlas, Denis Laxalde, Josef Perktold, Robert Cimrman,
   Ian Henriksen, E.A. Quintero, Charles R Harris, Anne M. Archibald,
   Antônio H. Ribeiro, Fabian Pedregosa, Paul van Mulbregt,
   and SciPy 1.0 Contributors. (2020) SciPy 1.0: Fundamental Algorithms for
   Scientific Computing in Python. Nature Methods, 17, 261–272 (2020) \|
   https://doi.org/10.1038/s41592-019-0686-2

## pandas:

1) McKinney, W., pandas: a foundational Python library for data analysis
   and statistics. Python for High Performance and Scientific Computing, 2011. 14.
