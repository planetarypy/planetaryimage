# -*- coding: utf-8 -*-
import numpy

from six.moves import range

from .image import PlanetaryImage
from .specialpixels import SPECIAL_PIXELS


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

    BYTE_ORDERS = {
        'NoByteOrder': '=',  # system
        'Lsb': '<',          # little-endian
        'Msb': '>'           # big-endian
    }

    BAND_STORAGE_TYPE = {
        'BAND_SEQUENTIAL': '_band_sequential',
        'Tile': '_parse_tile_data'
    }

    SPECIAL_PIXELS = SPECIAL_PIXELS

    def __init__(self, *args, **kwargs):
        if 'memory_layout' not in kwargs:
            kwargs['memory_layout'] = 'DISK'
        super(CubeFile, self).__init__(*args, **kwargs)

    @property
    def tile_lines(self):
        """Number of lines per tile."""
        if self.format != 'Tile':
            return None
        return self.label['IsisCube']['Core']['TileLines']

    @property
    def bands(self):
        return self.label['IsisCube']['Core']['Dimensions']['Bands']

    @property
    def lines(self):
        return self.label['IsisCube']['Core']['Dimensions']['Lines']

    @property
    def samples(self):
        return self.label['IsisCube']['Core']['Dimensions']['Samples']

    @property
    def format(self):
        return self.label['IsisCube']['Core']['Format']

    @property
    def base(self):
        return self.label['IsisCube']['Core']['Pixels']['Base']

    @property
    def multiplier(self):
        return self.label['IsisCube']['Core']['Pixels']['Multiplier']

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

    @property
    def data_filename(self):
        """Return detached filename else None. """
        return self.label['IsisCube']['Core'].get('^Core')

    def _parse_tile_data(self, stream):
        tile_lines = self.tile_lines
        tile_samples = self.tile_samples
        tile_size = tile_lines * tile_samples

        lines = range(0, self.lines, self.tile_lines)
        samples = range(0, self.samples, self.tile_samples)

        dtype = self.dtype
        data = numpy.empty(self.shape, dtype=dtype)

        for band in data:
            for line in lines:
                for sample in samples:
                    sample_end = sample + tile_samples
                    line_end = line + tile_lines
                    chunk = band[line:line_end, sample:sample_end]

                    tile = numpy.fromfile(stream, dtype, tile_size)
                    tile = tile.reshape((tile_lines, tile_samples))

                    chunk_lines, chunk_samples = chunk.shape
                    chunk[:] = tile[:chunk_lines, :chunk_samples]

        if self.memory_layout == 'IMAGE':
            if self.bands == 1:
                return data.squeeze()
            else:
                return numpy.dstack((data))
        else:
            return data
