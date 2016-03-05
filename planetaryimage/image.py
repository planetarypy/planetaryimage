# -*- coding: utf-8 -*-
import os
import gzip
import bz2
import six
import pvl
import numpy


class PlanetaryImage(object):
    """A generic image reader. """

    @classmethod
    def open(cls, filename):
        """ Read an image file from disk

        Parameters
        ----------
        filename : string
            Name of file to read as an image file.  This file may be gzip
            (``.gz``) or bzip2 (``.bz2``) compressed.
        """
        if filename.endswith('.gz'):
            fp = gzip.open(filename, 'rb')
            try:
                return cls(fp, filename, compression='gz')
            finally:
                fp.close()
        elif filename.endswith('.bz2'):
            fp = bz2.BZ2File(filename, 'rb')
            try:
                return cls(fp, filename, compression='bz2')
            finally:
                fp.close()
        else:
            with open(filename, 'rb') as fp:
                return cls(fp, filename)

    def __init__(self, stream, filename=None, compression=None):
        """Create an Image object.

        Parameters
        ----------

        stream
            file object to read as an image file

        filename : string
            an optional filename to attach to the object

        compression : string
            an optional string that indicate the compression type 'bz2' or 'gz'
        """
        if isinstance(stream, six.string_types):
            error_msg = (
                'A file like object is expected for stream. '
                'Use %s.open(filename) to open a image file.'
            )
            raise TypeError(error_msg % type(self).__name__)

        #: The filename if given, otherwise none.
        self.filename = filename

        self.compression = compression

        # TODO: rename to header and add footer?
        #: The parsed label header in dictionary form.
        self.label = self._load_label(stream)

        #: A numpy array representing the image
        self.data = self._load_data(stream)

    def __repr__(self):
        # TODO: pick a better repr
        return self.filename

    def save(self, file_to_write=None, overwrite=False):
        self._save(file_to_write, overwrite)

    @property
    def image(self):
        """An Image like array of ``self.data`` convenient for image processing tasks

        * 2D array for single band, grayscale image data
        * 3D array for three band, RGB image data

        Enables working with ``self.data`` as if it were a PIL image::

         >>> from planetaryimage import PDS3Image
         >>> import matplotlib.pyplot as plt
         >>> testfile = 'tests/mission_data/2p129641989eth0361p2600r8m1.img'
         >>> image = PDS3Image.open(testfile)
         >>> _ = plt.imshow(image.image, cmap='gray')
        """
        if self.bands == 1:
            return self.data.squeeze()
        elif self.bands == 3:
            return numpy.dstack(self.data)
        # TODO: what about multiband images with 2, and 4+ bands?

    @property
    def bands(self):
        """Number of image bands."""
        return self._bands

    @property
    def lines(self):
        """Number of lines per band."""
        return self._lines

    @property
    def samples(self):
        """Number of samples per line."""
        return self._samples

    @property
    def format(self):
        """Image format."""
        return self._format

    _data_filename = None

    @property
    def data_filename(self):
        """Return detached filename else None."""
        return self._data_filename

    @property
    def dtype(self):
        """Pixel data type."""
        return self._dtype

    @property
    def start_byte(self):
        """Index of the start of the image data (zero indexed)."""
        return self._start_byte

    @property
    def shape(self):
        """Tuple of images bands, lines and samples."""
        return (self.bands, self.lines, self.samples)

    @property
    def size(self):
        """Total number of pixels."""
        return self.bands * self.lines * self.samples

    def _load_label(self, stream):
        return pvl.load(stream)

    def _load_data(self, stream):
        if self.data_filename is not None:
            return self._load_detached_data()

        stream.seek(self.start_byte)
        return self._decode(stream)

    def _decode(self, stream):
        return self._decoder.decode(stream)

    def _load_detached_data(self):
        dirpath = os.path.dirname(self.filename)
        filename = os.path.abspath(os.path.join(dirpath, self.data_filename))

        with open(filename, 'rb') as stream:
            return self._decode(stream)
