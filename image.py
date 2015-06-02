from six import string_types
from pvl import load as load_label
import numpy

try:
    # Python 3 moved reduce to the functools module
    from functools import reduce
except ImportError:
    # Python 2 reduce is a built-in
    pass


class PlanteraryImage(object):
    """A generic image reader. """

    BAND_STORAGE_TYPE = {
        'BAND_SEQUENTIAL': '_band_sequential'
    }

    @classmethod
    def open(cls, filename):
        """ Read an image file from disk

        :param filename: name of file to read as an image file
        """
        with open(filename, 'rb') as fp:
            return cls(fp, filename)

    def __init__(self, stream, filename=None):
        """Create an Image file.

        :param stream: file object to read as an image file

        :param filename: an optional filename to attach to the object
        """
        if isinstance(stream, string_types):
            error_msg = (
               'A file like object is expected for stream. '
               'Use %s.open(filename) to open a image file.'
            )
            raise TypeError(error_msg % type(self).__name__)

        #: The filename if given, otherwise none.
        self.filename = filename

        #: The parsed label header in dictionary form.
        self.label = self._parse_label(stream)

        #: A numpy array representing the image
        self.image = self._parse_image(stream)

    @staticmethod
    def get_nested_dict(item, key_list):
        """Get value from nested dictionary using a key list. """
        return reduce(lambda x, y: x[y], key_list, item)

    @property
    def bands(self):
        """Number of image bands."""
        return self.get_nested_dict(self.label, self.LABEL_MAPPING['bands'])

    @property
    def lines(self):
        """Number of lines per band."""
        return self.get_nested_dict(self.label, self.LABEL_MAPPING['lines'])

    @property
    def samples(self):
        """Number of samples per line."""
        return self.get_nested_dict(self.label, self.LABEL_MAPPING['samples'])

    @property
    def format(self):
        return self.get_nested_dict(self.label, self.LABEL_MAPPING['format'])

    @property
    def byte_order(self):
        """Byte order in numpy format('>', '<', '=').
        Defaults to msb.
        """
        return '>'

    @property
    def pixel_type(self):
        """Pixel value type as numpy.dtype. """
        raise NotImplementedError

    @property
    def dtype(self):
        """Pixel data type. """
        return self.pixel_type.newbyteorder(self.byte_order)

    @property
    def start_byte(self):
        """Index of the start of the image data (zero indexed)."""
        raise NotImplementedError

    @property
    def shape(self):
        """Tuple of images bands, lines and samples."""
        return (self.bands, self.lines, self.samples)

    @property
    def size(self):
        return self.bands * self.lines * self.samples

    def _parse_label(self, stream):
        return load_label(stream)

    def _parse_image(self, stream):
        stream.seek(self.start_byte)
        if self.format in self.BAND_STORAGE_TYPE:
            return getattr(self, self.BAND_STORAGE_TYPE[self.format])(stream)

    def _band_sequential(self, stream):
        """Band sequential storage type reader. """
        data = numpy.fromfile(stream, self.dtype, self.size)
        return data.reshape(self.shape)
