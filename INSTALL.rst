Required dependencies
=====================

PICAchooser requires some external libraries to be installed first:

-  Python 3.x
-  numpy>=1.16
-  scipy
-  pandas
-  nibabel
-  pyqt5
-  pyqtgraph
-  pillow


Installing Python
-----------------

The simplest way BY FAR to get this all done is to use Anaconda python
from Continuum Analytics. It’s a free, curated scientific Python
distribution that is easy to maintain and takes a lot of headaches out
of maintaining a distribution. It also already comes with almost all of the
dependancies for PICAchooser installed by default. You can get it here:
https://www.continuum.io. You should download the most recent Python 3 version.

After installing Anaconda python, install the remaining dependency
To do this most easily, you should have
conda-forge as one of your source channels.  To add conda-forge, type:

::

   conda config --add channels conda-forge


Then install the additional dependencies:

::

   conda install pyqtgraph nibabel pillow



Done.

Installing PICAchooser
--------------------

Once you have installed the prerequisites, cd into the package
directory, and type the following:

::

   python setup.py install


to install all of the tools in the package. You should be able to run
them from the command line then (after rehashing).

Updating
--------

If you’ve previously installed PICAchooser and want to update, cd into the
package directory and do a git pull first:

::

   git pull
   python setup.py install


Usage
-----
Run PICAchooser to look at a series of timecourses and assign them a rating:
::

    tidepool


(then select the file rapidtide/data/examples/dst/dgsr_lagtimes.nii.gz to load the dataset):
