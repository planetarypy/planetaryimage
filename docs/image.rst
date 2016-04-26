PlanetaryImage uses three main classes: PlanetaryImage_, PDS3Image_,
and CubeFile_. PlanetaryImage_ is the base class for
PDS3Image_ and CubeFile_ and can be inherited for other image
readers. PDS3Image_ and CubeFile_ are used to read images. See `Usage <https://
planetaryimage.readthedocs.org/en/latest/usage.html>`_ to see more in depth
examples using PDS3Image_ and CubeFile_.

.. contents::


==============
PlanetaryImage
==============

.. automodule:: planetaryimage.image
.. autoclass:: PlanetaryImage
    :members:

Examples
--------
  >>> from planetaryimage import PDS3Image
  >>> import matplotlib.pyplot as plt
  >>> testfile = 'tests/mission_data/2p129641989eth0361p2600r8m1.img'
  >>> image = PDS3Image.open(testfile)
  >>> # Examples of attributes
  >>> image.bands
  1
  >>> image.lines
  64
  >>> image.samples
  64
  >>> image.format
  'BAND_SEQUENTIAL'
  >>> image.data_filename
  >>> image.dtype
  dtype('>i2')
  >>> image.start_byte
  34304
  >>> image.shape
  (1, 64, 64)
  >>> image.size
  4096


=========
PDS3Image
=========

.. currentmodule:: planetaryimage.pds3image
.. autoclass:: PDS3Image
    :members:
    :show-inheritance:

Examples
--------
  >>> from planetaryimage import PDS3Image
  >>> testfile = 'tests/mission_data/2p129641989eth0361p2600r8m1.img'
  >>> image = PDS3Image.open(testfile)
  >>> # Display image in plot
  >>> plt.imshow(image.image, cmap='gray')
  >>> # Examples of PDS3Image Attributes
  >>> image.dtype
  dtype('>i2')
  >>> image.record_bytes
  128
  >>> image.data_filename


=========
CubeFile
=========

.. currentmodule:: planetaryimage.cubefile
.. autoclass:: CubeFile
    :members:
    :show-inheritance:

Examples
--------
  >>> from planetaryimage import CubeFile
  >>> image = CubeFile.open('tests/data/pattern.cub')
  >>> # Display image in plot
  >>> plt.imshow(image.image, cmap='gray')
  >>> # Examples of PDS3Image Attributes
  >>> image.base
  0.0
  >>> image.multiplier
  1.0
  >>> image.specials
  {'His': -3.4028233e+38,
   'Hrs': -3.4028235e+38,
   'Lis': -3.4028231e+38,
   'Lrs': -3.4028229e+38,
   'Max': 3.4028235e+38,
   'Min': -3.4028225e+38,
   'Null': -3.4028227e+38}
  >>> image.tile_lines
  128
  >>> image.tile_samples
  128
  >>> image.tile_shape
  (128, 128)




