# PICAchooser
 A simple gui tool for scanning through MELODIC ICA runs and quickly making decisions about which components to retain.  This tool does one thing, but it does it quickly and easily using only keyboard input.


Basically, PICAchooser loads the results of a MELODIC ICA run and lets you step through the components, look at them, and decide if you want to keep them or discard them.  After you load the dataset, you get a window showing the active IC component (both the timecourse and the spatial map), the power spectrum of the active IC component, and the motion timecourses for comparison.  By default, components are flagged to be kept (and the timecourses are in green).  To toggle whether the component should be kept or discarded, press the up or down arrow key.  You can change back and forth as much as you want.  To go to the next component, press the right arrow, and press the left arrow to go to the previous one.  Press the escape key at any tie to save the current version of the component list.  The component list is saved automatically when you quit.


