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

    @staticmethod
    def parse_pointer(pointer_data, record_bytes):
        """Parses the pointer label.
        Supported types are
            ^PTR = nnn
            ^PTR = nnn <BYTES>
            ^PTR = "filename"
            ^PTR = ("filename")
            ^PTR = ("filename", nnn)
            ^PTR = ("filename", nnn <BYTES>)

        :param pointer_data: Pointer data read from file

        :param record_bytes: Record multiplier value

        :returns: an array [start_byte, filename or None]
        """
        if isinstance(pointer_data, six.integer_types):
            return [(pointer_data - 1) * record_bytes, None]
        elif isinstance(pointer_data, Units):
            if pointer_data.units == 'BYTES':
                return [pointer_data.value, None]
            else:
                raise ValueError(
                    'Expected <BYTES> as image pointer units but found (%s)'
                    % pointer_data.units)
        elif isinstance(pointer_data, six.string_types):
            return [0, pointer_data]
        elif isinstance(pointer_data, list):
            if len(pointer_data) == 1:
                return [0, pointer_data]
            else:
                if isinstance(pointer_data[1], six.integer_types):
                    return [(pointer_data[1] - 1) * record_bytes, pointer_data[0]]
                elif isinstance(pointer_data[1], Units):
                    if pointer_data[1].units == 'BYTES':
                        return [pointer_data[1].value, pointer_data[0]]
                    else:
                        raise ValueError(
                            'Expected <BYTES> as image pointer units but found (%s)'
                            % pointer_data.units)
        else:
            raise ValueError('Unsupported pointer type')

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
#        elif isinstance(pointer, list):

        else:
            raise ValueError('Unsupported image pointer type')

    @property
    def data_filename(self):
        return None

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
