.. PICAchooser documentation master file, created by
   sphinx-quickstart on Thu Jun 16 15:27:19 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

PICAchooser
===========
PICAchooser is a simple, lightweight GUI that lets you sort through the components
of an FSL MELODIC ICA analysis, to decide which components to keep and which to filter
out.  It only does one thing, but it does it quickly.  You can do navigation and selection
using only the arrow keys.

PICAchooser has three modes:

Standard melodic mode: Tell PICAchooser how to find a .ica directory, and the associated .feat
directory, and it will create a "badcomponents.txt" file in the comma separated format that you 
would use with fsl_regfilt.

AROMA mode: Tell PICAchooser how to find the AROMA output directory, and the associated .feat
directory.  It will load the melodic components and the decisions that AROMA made about each one
(from the AROMADIR/classified_motion_ICs.txt file).  It writes out the revised components to
AROMADIR/classified_motion_ICs_revised.txt (or anywhere you want it to, if you use the --outputfile
option).  You can then refilter your data using the revised classifications.

FIX mode:  The same as Standard melodic mode, but the output file 
is named ICADIR/hhand_labels_noise.txt and has square brackets around the component list, as
expected for FIX training datasets.

.. image:: https://img.shields.io/badge/License-Apache%202.0-blue.svg
   :target: https://opensource.org/licenses/Apache-2.0

Contents
========
.. toctree::
   :maxdepth: 2

   introduction.rst
   whats_new.rst
   installation.rst
   usage.rst
   contributing.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
