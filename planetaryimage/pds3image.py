# -*- coding: utf-8 -*-
from pvl._collections import Units
from .image import PlanetaryImage
import numpy
import six


class PDS3Image(PlanetaryImage):

    """ A PDS3 image reader. """

    PIXEL_TYPES = {
        'UnsignedByte': numpy.dtype('uint8'),
        'SignedByte': numpy.dtype('int8'),
        'UnsignedWord': numpy.dtype('uint16'),
        'SignedWord': numpy.dtype('int16'),
        'UnsignedInteger': numpy.dtype('uint32'),
        'SignedInteger': numpy.dtype('int32'),
    }

    LABEL_MAPPING = {
        'bands': ['IMAGE', 'BANDS'],
        'lines': ['IMAGE', 'LINES'],
        'samples': ['IMAGE', 'LINE_SAMPLES'],
        'format': ['IMAGE', 'BAND_STORAGE_TYPE'],
        'bits': ['IMAGE', 'SAMPLE_BITS'],
        'sample_type': ['IMAGE', 'SAMPLE_TYPE']
    }

    BAND_STORAGE_TYPE = {
        'BAND_SEQUENTIAL': '_parse_band_sequential_data'
    }

    def __init__(self, *args, **kwargs):
        if 'memory_layout' not in kwargs:
            kwargs['memory_layout'] = 'IMAGE'
        super(PDS3Image, self).__init__(*args, **kwargs)

    @property
    def format(self):
        try:
            return self.get_nested_dict(self.label, self.LABEL_MAPPING['format'])
        except KeyError:
            return 'BAND_SEQUENTIAL'

    @property
    def byte_order(self):
        sample_type = self.get_nested_dict(self.label, self.LABEL_MAPPING['sample_type'])
        if "LSB" in sample_type:
            return '<'
        else:
            return '>'

    @property
    def start_byte(self):
        """Pointer types that are currently implemented are
            ^IMAGE = nnn
            ^IMAGE = nnn <BYTES>
        """
        pointer = self.label['^IMAGE']
        if isinstance(pointer, six.integer_types):
            return (pointer - 1) * self.label['RECORD_BYTES']
        elif isinstance(pointer, Units):
            if pointer.units == 'BYTES':
                return pointer.value
            else:
                raise ValueError(
                    'Expected <BYTES> as image pointer units but found (%s)'
                    % pointer.units)
        else:
            raise ValueError('Unsupported image pointer type')

    @property
    def pixel_type(self):
        sample_type = self.get_nested_dict(self.label, self.LABEL_MAPPING['sample_type'])
        bits = self.get_nested_dict(self.label, self.LABEL_MAPPING['bits'])

        if 'UNSIGNED' in sample_type:
            if bits == 8:
                return self.PIXEL_TYPES['UnsignedByte']
            if bits == 16:
                return self.PIXEL_TYPES['UnsignedWord']
            if bits == 32:
                return self.PIXEL_TYPES['UnsignedInteger']
        else:
            if bits == 8:
                return self.PIXEL_TYPES['SignedByte']
            if bits == 16:
                return self.PIXEL_TYPES['SignedWord']
            if bits == 32:
                return self.PIXEL_TYPES['SignedInteger']

        raise TypeError
