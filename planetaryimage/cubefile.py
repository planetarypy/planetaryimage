# -*- coding: utf-8 -*-
import numpy

from .image import PlanetaryImage
from .specialpixels import SPECIAL_PIXELS
from .decoders import BandSequentialDecoder, TileDecoder


class CubeFile(PlanetaryImage):
    """A Isis Cube file reader.

    Examples
    --------
      >>> from planetaryimage import CubeFile
      >>> image = CubeFile.open('tests/data/pattern.cub')
      >>> # Examples of CubeFile Attributes
      >>> image.base
      0.0
      >>> image.multiplier
      1.0
      >>> image.specials['His']
      -3.4028233e+38
      >>> image.tile_lines
      128
      >>> image.tile_samples
      128
      >>> image.tile_shape
      (128, 128)

    """

    PIXEL_TYPES = {
        'UnsignedByte': numpy.dtype('uint8'),
        'SignedByte': numpy.dtype('int8'),
        'UnsignedWord': numpy.dtype('uint16'),
        'SignedWord': numpy.dtype('int16'),
        'UnsignedInteger': numpy.dtype('uint32'),
        'SignedInteger': numpy.dtype('int32'),
        'Real': numpy.dtype('float32'),
        'Double': numpy.dtype('float64')
    }

    BYTE_ORDERS = {
        'NoByteOrder': '=',  # system
        'Lsb': '<',          # little-endian
        'Msb': '>'           # big-endian
    }

    SPECIAL_PIXELS = SPECIAL_PIXELS

    def _save(self, file_to_write, overwrite):
        raise NotImplementedError

    def _create_label(self, array):
        raise NotImplementedError

    @property
    def _bands(self):
        return self.label['IsisCube']['Core']['Dimensions']['Bands']

    @property
    def _lines(self):
        return self.label['IsisCube']['Core']['Dimensions']['Lines']

    @property
    def _samples(self):
        return self.label['IsisCube']['Core']['Dimensions']['Samples']

    @property
    def _format(self):
        return self.label['IsisCube']['Core']['Format']

    @property
    def _start_byte(self):
        return self.label['IsisCube']['Core']['StartByte'] - 1

    @property
    def _dtype(self):
        return self._pixel_type.newbyteorder(self._byte_order)

    @property
    def base(self):
        """An additive factor by which to offset pixel DN."""
        return self.label['IsisCube']['Core']['Pixels']['Base']

    @property
    def multiplier(self):
        """A multiplicative factor by which to scale pixel DN."""
        return self.label['IsisCube']['Core']['Pixels']['Multiplier']

    @property
    def tile_lines(self):
        """Number of lines per tile."""
        if self.format != 'Tile':
            return None
        return self.label['IsisCube']['Core']['TileLines']

    @property
    def tile_samples(self):
        """Number of samples per tile."""
        if self.format != 'Tile':
            return None
        return self.label['IsisCube']['Core']['TileSamples']

    @property
    def tile_shape(self):
        """Shape of tiles."""
        if self.format != 'Tile':
            return None
        return (self.tile_lines, self.tile_samples)

    @property
    def _byte_order(self):
        return self.BYTE_ORDERS[self._pixels_group['ByteOrder']]

    @property
    def _pixels_group(self):
        return self.label['IsisCube']['Core']['Pixels']

    @property
    def _pixel_type(self):
        return self.PIXEL_TYPES[self._pixels_group['Type']]

    @property
    def specials(self):
        """Return the special pixel values"""
        pixel_type = self._pixels_group['Type']
        return self.SPECIAL_PIXELS[pixel_type]

    @property
    def data_filename(self):
        """Return detached filename else None."""
        return self.label['IsisCube']['Core'].get('^Core')

    def apply_scaling(self, copy=True):
        """Scale pixel values to there true DN.

        Parameters
        ----------
        copy: bool [True]
            Whether to apply the scaling to a copy of the pixel data
            and leave the original unaffected

        Returns
        -------
        Numpy Array
            A scaled version of the pixel data

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
        copy : bool [True]
            Whether to apply the new special values to a copy of the
            pixel data and leave the original unaffected

        Returns
        -------
        Numpy Array
            A numpy array with special values converted to numpy's nan, inf,
            and -inf
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
        An array where the value is `False` if the pixel is special
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

            from planetaryimage import CubeFile
            from PIL import Image

            # Read in the image and create the image data
            image = CubeFile.open('test.cub')
            data = image.get_image_array()

            # Save the first band to a new file
            Image.fromarray(data[0]).save('test.png')

        Returns
        -------
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
    def _decoder(self):
        if self.format == 'BandSequential':
            return BandSequentialDecoder(self.dtype, self.shape)

        if self.format == 'Tile':
            return TileDecoder(self.dtype, self.shape, self.tile_shape)

        raise ValueError('Unkown format (%s)' % self.format)
