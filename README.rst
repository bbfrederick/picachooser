PICAchooser
===========

A simple gui tool for scanning through MELODIC ICA runs and quickly making decisions about which components to retain.  This tool does one thing, but it does it quickly and easily using only keyboard input.

Basically, PICAchooser loads the results of a MELODIC ICA run and lets you step through the components, look at them, and decide if you want to keep them or discard them.  After you load the dataset, you get a window showing the active IC component (both the timecourse and the spatial map), the power spectrum of the active IC component, and the motion timecourses for comparison.  By default, components are flagged to be kept (and the timecourses are in green).


Usage
=====

::
usage: PICAchooser featdir melodicdir runmode [options]

A program to review (and alter) melodic component selections.

positional arguments:
  featdir               The FEAT directory associated with this MELODIC run.
  melodicdir            The .ica directory for this MELODIC run.
  runmode               Analysis mode. Valid choices are "melodic", "AROMA", and "FIX". In
                        melodic mode, the default output file is named "badcomponents.txt" and
                        will be written to MELODICDIR as comma separated integers. In AROMA mode,
                        the file "classified_motion_ICs.txt" must exist in the parent of
                        MELODICDIR; by default the output will be written to
                        "classified_motion_ICs_revised.txt" in the same directory. In FIX mode,
                        the default output file is named "hand_labels_noise.txt" and will be
                        written to MELODICDIR as comma separated integers with square brackets
                        surrounding the line.

optional arguments:
  -h, --help            show this help message and exit
  --outputfile OUTPUTFILE
                        The name of the newly written bad component file (this overrides the
                        default output file name).
  --displaythresh DISPLAYTHRESH
                        z threshold for the displayed ICA components. Default is 2.3.


Controls
========

To toggle whether the current component should be kept or discarded, press the up or down arrow key.  You can change back and forth as much as you want.

To go to the next (or previous) component, press the right (or left) arrow.  You'll wrap around if you hit the end.

Press the escape key at any time to save the current version of the component list.  The component list is saved automatically when you quit.


Options
=======
If you invoke PICAchooser with the --melodicdir MELODICDIR option, it just treats it as an ordinary melodic analysis for you to hand tag.  By default, it will write out a file called

If you invoke PICAchooser with the --fixmelodicdir option, it makes a hand labelling file in the appropriate format with the appropriate name, if you’re making a training set.

And if you invoke with the --aromadir option, it displays what components AROMA flagged and lets you change the selections.

