# PICAchooser

A simple gui tool for scanning through MELODIC probabalistic ICA runs and quickly making decisions about which components to retain.  This tool does one thing, but it does it quickly and easily using only keyboard input.

Basically, PICAchooser loads the results of a MELODIC ICA run and lets you step through the components, look at them, and decide if you want to keep them or discard them.  After you load the dataset, you get a window showing the active IC component (both the timecourse and the spatial map), the power spectrum of the active IC component, and the motion timecourses for comparison.  By default, components are flagged to be kept (and the timecourses are in green[^*]).


# Usage

``` bash
usage: PICAchooser featdir melodicdir runmode [options]

A program to review (and alter) melodic component selections.

positional arguments:
  featdir               The FEAT directory associated with this MELODIC run.
  melodicdir            The .ica directory for this MELODIC run.
  runmode               Analysis mode. Valid choices are "melodic", "aroma", and "fix". In "melodic"
                        mode, the default output file is named "badcomponents.txt" and will be
                        written to MELODICDIR as comma separated integers. In "aroma" mode, the file
                        "classified_motion_ICs.txt" must exist in the parent of MELODICDIR; by
                        default the output will be written to "classified_motion_ICs_revised.txt"
                        in the same directory. In "fix" mode, the default output file is named
                        "hand_labels_noise.txt" and will be written to MELODICDIR as comma
                        separated integers with square brackets surrounding the line.

optional arguments:
  -h, --help            show this help message and exit
  --initfile INITFILE   The name of an initial bad component file (this overrides the default
                        input file for AROMA).
  --outputfile OUTPUTFILE
                        The name of the newly written bad component file (this overrides the
                        default output file name).
  --displaythresh DISPLAYTHRESH
                        z threshold for the displayed ICA components. Default is 2.3.
```

You'll then get a window that looks like this:

![PICAchooser screenshot](https://github.com/bbfrederick/picachooser/blob/master/images/picachooser_screenshot.png)

# Controls


To toggle whether the current component should be kept or discarded, press the up or down arrow key.  You can change back and forth as much as you want. Components to be discarded are in red, ones to be kept are in green[^*].

To go to the next (or previous) component, press the right (or left) arrow.  You'll wrap around if you hit the end.

Press the escape key at any time to save the current version of the component list.  The component list is saved automatically when you quit.


Options
=======
`--initfile` lets you read in a bad component file from anywhere to use as a starting point in your classification.  This is the normal behavior in aroma mode, but you can do it in any mode with this flag, and it will override the aroma classifications.

`--outputdir` lets you write the bad component file anywhere you want, rather than just the default location.

`--displaythresh` sets the z-threshold for the component maps.

[^*]: You can override the default keepcolor and discardcolor by editing the file ${HOME}/.picachooser.json. This file is created is created with default values if it is not present.  You can use any valid python color specification string, e.g. "r", "ff0000", or "FF0000" could all be used for red.
