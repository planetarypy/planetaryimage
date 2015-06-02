# -*- coding: utf-8 -*-
from .image import PlanetaryImage
import numpy


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
        'BAND_SEQUENTIAL': '_band_sequential'
    }

    def __init__(self, *args, **kwargs):
        super(PDS3Image, self).__init__(*args, **kwargs)

    @property
    def byte_order(self):
        sample_type = self.get_nested_dict(self.label, self.LABEL_MAPPING['sample_type'])
        if "LSB" in sample_type:
            return '<'
        else:
            return '>'

    @property
    def start_byte(self):
        return self.label['^IMAGE'] - 1

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
