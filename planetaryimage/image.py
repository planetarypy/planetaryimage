# -*- coding: utf-8 -*-
import os
import gzip
import bz2
import six
import pvl
import numpy


class PlanetaryImage(object):
    """A generic image reader. Parent object for PDS3Image and CubeFile

    Parameters
    ----------

    stream
        file object to read as an image file

    filename : string
        an optional filename to attach to the object

    compression : string
        an optional string that indicate the compression type 'bz2' or 'gz'

    Attributes
    ----------
    compression : string
        Compression type (i.e. 'gz', 'bz2', or None).

    data : numpy array
        A numpy array representing the image.

    filename : string
        The filename given.

    label : pvl module
        The image's label in dictionary form.

    Examples
    --------
    >>> from planetaryimage import PDS3Image
    >>> testfile = 'tests/mission_data/2p129641989eth0361p2600r8m1.img'
    >>> image = PDS3Image.open(testfile)
    >>> # Examples of attributes
    >>> image.bands
    1
    >>> image.lines
    64
    >>> image.samples
    64
    >>> str(image.format)
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

    See https://planetaryimage.readthedocs.io/en/latest/usage.html to see how
    to open images to view them and make manipulations.

    """

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

    def __init__(self, stream_string_or_array, filename=None, compression=None):
        """
        Create an Image object.
        """
        if isinstance(stream_string_or_array, six.string_types):
            error_msg = (
                'A file like object is expected for stream. '
                'Use %s.open(filename) to open a image file.'
            )
            raise TypeError(error_msg % type(self).__name__)

        if isinstance(stream_string_or_array, numpy.ndarray):
            self.filename = None
            self.compression = None
            self.data = stream_string_or_array
            self.label = self._create_label(stream_string_or_array)
        else:
            #: The filename if given, otherwise none.
            self.filename = filename

            self.compression = compression

            # TODO: rename to header and add footer?
            #: The parsed label header in dictionary form.
            self.label = self._load_label(stream_string_or_array)

            #: A numpy array representing the image
            self.data = self._load_data(stream_string_or_array)

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

        Enables working with ``self.data`` as if it were a PIL image.

        See https://planetaryimage.readthedocs.io/en/latest/usage.html to see
        how to open images to view them and make manipulations.

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
        """Total number of pixels"""
        return self.bands * self.lines * self.samples

    def _load_label(self, stream):
        return pvl.load(stream)

    def _load_data(self, stream):
        if self.data_filename is not None:
            return self._load_detached_data()

        stream.seek(self.start_byte)
        return self._decode(stream)

    def create_label(self, array):
        self._create_label(array)

    def _decode(self, stream):
        return self._decoder.decode(stream)

    def _load_detached_data(self):
        dirpath = os.path.dirname(self.filename)
        filename = os.path.abspath(os.path.join(dirpath, self.data_filename))

        with open(filename, 'rb') as stream:
            return self._decode(stream)
