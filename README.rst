======================================================
planetaryimage - Open PDS and Isis CubeFiles in Python
======================================================

.. image:: https://img.shields.io/travis/planetarypy/planetaryimage.svg
        :target: https://travis-ci.org/planetarypy/planetaryimage

.. image:: https://img.shields.io/pypi/v/planetaryimage.svg
        :target: https://pypi.python.org/pypi/planetaryimage


Planetary image parser

* Free software: BSD license
* Documentation: https://planetaryimage.readthedocs.org.

Features
--------

* Reads in PDS Images as NumPy arrays.
* Reads in Isis Cube Files as NumPy arrays.

Quickstart
----------

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

Now run python::

  $ ipython notebook

Create a new notebook in your web browser and then paste the following code
into a cell and execute it by pressing Shift+ENTER.  This will load and display
the image::

  %matplotlib inline
  import matplotlib.pyplot as plt
  from planetaryimage import PDS3Image
  image = PDS3Image.open('1p380322615effbr43p2443l1m1.img')
  plt.imshow(image.data, cmap='gray')
