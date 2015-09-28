from six import string_types
from pvl import load as load_label
import numpy
import os
import gzip
import bz2


try:
    # Python 3 moved reduce to the functools module
    from functools import reduce
except ImportError:
    # Python 2 reduce is a built-in
    pass


class PlanetaryImage(object):

    BAND_STORAGE_TYPE = {
        'BAND_SEQUENTIAL': '_parse_band_sequential_data'
    }

    @classmethod
    def open(cls, filename):
        """ Read an image file from disk

        Parameters
        ----------
        filename : string
            name of file to read as an image file
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

    def __init__(self, stream, filename=None, compression=None, memory_layout='DISK'):
        """Create an Image object.

        Parameters
        ----------

        stream
            file object to read as an image file

        filename : string
            an optional filename to attach to the object

        memory_layout : string
            format of the data that is returned supported values are "IMAGE"
            and "DISK"
        """
        if isinstance(stream, string_types):
            error_msg = (
                'A file like object is expected for stream. '
                'Use %s.open(filename) to open a image file.'
            )
            raise TypeError(error_msg % type(self).__name__)

        #: The filename if given, otherwise none.
        self.filename = filename

        if memory_layout not in ['IMAGE', 'DISK']:
            raise ValueError('Unsupported memory_layout value.\
                Expected "IMAGE" or "DISK"')

        self.memory_layout = memory_layout

        self.compression = compression

        #: The parsed label header in dictionary form.
        self.label = self._parse_label(stream)

        #: A numpy array representing the image
        self.data = self._parse_data(stream)

    def __repr__(self):
        return self.filename

    @staticmethod
    def get_nested_dict(item, key_list):
        """Get value from nested dictionary using a key list. """
        return reduce(lambda x, y: x[y], key_list, item)

    def apply_scaling(self, copy=True):
        """Scale pixel values to there true DN.

        Parameters
        ----------
        copy : boolean
            whether to apply the scalling to a copy of the pixel data
            and leave the orginial unaffected

        Returns
        -------
        scaled_pixel_data
            a scaled version of the pixel data
        """
        if copy:
            return self.multiplier * self.data + self.base

        if self.multiplier != 1:
            self.data *= self.multiplier

        if self.base != 0:
            self.data += self.base

        return self.data

    def apply_numpy_specials(self, copy=True):
        """Convert isis special pixel values to numpy special pixel values.

            =======  =======
             Isis     Numpy
            =======  =======
            Null     nan
            Lrs      -inf
            Lis      -inf
            His      inf
            Hrs      inf
            =======  =======

        Parameters
        ----------
        copy : boolean
            whether to apply the new special values to a copy of the
            pixel data and leave the orginial unaffected

        Returns
        -------
        modified_image_data
            a numpy array with special values converted to numpy's ``nan``,
            ``inf`` and ``-inf``
        """
        if copy:
            data = self.data.astype(numpy.float64)

        elif self.data.dtype != numpy.float64:
            data = self.data = self.data.astype(numpy.float64)

        else:
            data = self.data

        data[data == self.specials['Null']] = numpy.nan
        data[data < self.specials['Min']] = numpy.NINF
        data[data > self.specials['Max']] = numpy.inf

        return data

    def specials_mask(self):
        """Create a pixel map for special pixels.

        Returns
        -------
        mask_array
            an array where the value is `False` if the pixel is special
            and `True` otherwise
        """
        mask = self.data >= self.specials['Min']
        mask &= self.data <= self.specials['Max']
        return mask

    def get_image_array(self):
        """Create an array for use in making an image.

        Creates a linear stretch of the image and scales it to between `0` and
        `255`. `Null`, `Lis` and `Lrs` pixels are set to `0`. `His` and `Hrs`
        pixels are set to `255`.

        Usage::

            from pysis import CubeFile
            from PIL import Image

            # Read in the image and create the image data
            image = CubeFile.open('test.cub')
            data = image.get_image_array()

            # Save the first band to a new file
            Image.fromarray(data[0]).save('test.png')

        Returns
        -------
        stretched_array
            A uint8 array of pixel values.
        """
        specials_mask = self.specials_mask()
        data = self.data.copy()

        data[specials_mask] -= data[specials_mask].min()
        data[specials_mask] *= 255 / data[specials_mask].max()

        data[data == self.specials['His']] = 255
        data[data == self.specials['Hrs']] = 255

        return data.astype(numpy.uint8)

    @property
    def bands(self):
        """Number of image bands."""
        raise NotImplementedError

    @property
    def lines(self):
        """Number of lines per band."""
        raise NotImplementedError

    @property
    def samples(self):
        """Number of samples per line."""
        raise NotImplementedError

    @property
    def format(self):
        raise NotImplementedError

    @property
    def byte_order(self):
        """Byte order in numpy format('>', '<', '=')."""
        raise NotImplementedError

    @property
    def data_filename(self):
        """Return detached filename else None. """
        return None

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

    @property
    def base(self):
        """An additive factor by which to offset pixel DN."""
        raise NotImplementedError

    @property
    def multiplier(self):
        """A multiplicative factor by which to scale pixel DN."""
        raise NotImplementedError

    def _parse_label(self, stream):
        return load_label(stream)

    def _parse_data(self, stream):
        data_stream = stream
        try:
            if self.data_filename is not None:
                dirpath = os.path.dirname(self.filename)
                data_file = os.path.abspath(
                    os.path.join(dirpath, self.data_filename))

                data_stream = open(data_file, 'rb')

            data_stream.seek(self.start_byte)
            if self.format in self.BAND_STORAGE_TYPE:
                return getattr(self, self.BAND_STORAGE_TYPE[self.format])(data_stream)

            raise Exception('Unkown format (%s)' % self.format)

        finally:
            data_stream.close()

    def _parse_band_sequential_data(self, stream):
        if self.compression == 'none':
            data = numpy.fromfile(stream, self.dtype, self.size)
        else:
            data = numpy.fromstring(stream.read(self.size*4), self.dtype)
        data = data.reshape(self.shape)
        if self.memory_layout == 'IMAGE':
            if self.bands == 1:
                return data.squeeze()
            else:
                return numpy.dstack((data))
        else:
            return data
