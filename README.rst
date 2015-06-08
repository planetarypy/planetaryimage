======================================================
planetaryimage - Open PDS and Isis CubeFiles in Python
======================================================

.. image:: https://img.shields.io/travis/planetarypy/planetaryimage.svg
        :target: https://travis-ci.org/planetarypy/planetaryimage

.. image:: https://img.shields.io/pypi/v/planetaryimage.svg
        :target: https://pypi.python.org/pypi/planetaryimage

**NOTE** This is Alpha quality software that is being actively developed, use
at your own risk.

Planetary image parser

* Free software: BSD license
* Documentation: https://planetaryimage.readthedocs.org.

Features
--------

* Reads in PDS Images as NumPy arrays.
* Reads in Isis Cube Files as NumPy arrays.

Check out a few simple examples of
`opening and viewing PDS and Isis CubeFiles in an IPython notebook <http://nbviewer.ipython.org/urls/gist.githubusercontent.com/godber/dfb5d012fda603619ab9/raw/b1db599f53a5c468075ff854e9056698bd005cc7/gistfile1.json>`_.

Quickstart
----------

The example below will walk you through setting up a Python virtual
environment and installing the necessary software as well as a few handy
extras.  It then downloads a sample Pancam PDS image, opens and displays that
image in your web browser in an
`IPython Notebook <http://ipython.org/notebook.html>`_.  The example assumes
you have ``Python``, ``virtualenv``, and ``pip`` installed on your system.  If you
don't, don't know what this means or aren't thrilled by the opportunity to
learn what this means, this software may be a little too immature for you to
use at this point.

Create and activate a virtual environment::

  virtualenv venv
  source venv/bin/activate

Upgrade pip, then pip install the package and IPython notebook and matplotlib
to help display the image::

  pip install -U pip
  pip install planetaryimage matplotlib ipython[notebook]

This quick example will show how to open and display a Pancam PDS image using
this module.  First, grab a sample image::

  wget http://pds-imaging.jpl.nasa.gov/data/mer/opportunity/mer1po_0xxx/data/sol2840/edr/1p380322615effbr43p2443l1m1.img

Now run python in an IPython Notebook (a browser window should pop up after
entering the following command)::

  $ ipython notebook

Create a new notebook in your web browser and then paste the following code
into a cell and execute it by pressing Shift+ENTER.  This will load and display
the image::

  %matplotlib inline
  import matplotlib.pyplot as plt
  from planetaryimage import PDS3Image
  image = PDS3Image.open('1p380322615effbr43p2443l1m1.img')
  plt.imshow(image.data, cmap='gray')
