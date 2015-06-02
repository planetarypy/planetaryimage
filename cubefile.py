# -*- coding: utf-8 -*-
import numpy

from six import string_types
from six.moves import range

from image import PlanetaryImage
from specialpixels import SPECIAL_PIXELS


class CubeFile(PlanetaryImage):
    """A Isis Cube file reader."""

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

    LABEL_MAPPING = {
        'bands': ['IsisCube', 'Core', 'Dimensions', 'Bands'],
        'lines': ['IsisCube', 'Core', 'Dimensions', 'Lines'],
        'samples': ['IsisCube', 'Core', 'Dimensions', 'Samples'],
        'format': ['IsisCube', 'Core', 'Format'],
        'base': ['IsisCube', 'Core', 'Pixels', 'Base'],
        'multiplier': ['IsisCube', 'Core', 'Pixels', 'Multiplier'],
    }

    BYTE_ORDERS = {
        'NoByteOrder': '=',  # system
        'Lsb': '<',          # little-endian
        'Msb': '>'           # big-endian
    }

    SPECIAL_PIXELS = SPECIAL_PIXELS

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
    def byte_order(self):
        return self.BYTE_ORDERS[self.pixels_group['ByteOrder']]

    @property
    def pixels_group(self):
        return self.label['IsisCube']['Core']['Pixels']

    @property
    def pixel_type(self):
        return self.PIXEL_TYPES[self.pixels_group['Type']]

    @property
    def specials(self):
        pixel_type = self.label['IsisCube']['Core']['Pixels']['Type']
        return self.SPECIAL_PIXELS[pixel_type]

    @property
    def start_byte(self):
        """Index of the start of the image data (zero indexed)."""
        return self.label['IsisCube']['Core']['StartByte'] - 1
