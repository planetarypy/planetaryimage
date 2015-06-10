# -*- coding: utf-8 -*-
from pvl._collections import Units
from .image import PlanetaryImage
import numpy
import six


class PDS3Image(PlanetaryImage):

    """ A PDS3 image reader. """

    LSB_INTEGER_TYPES = ['LSB_INTEGER', 'PC_INTEGER', 'VAX_INTEGER']
    LSB_UNSIGNED_INTEGER_TYPES = ['LSB_UNSIGNED_INTEGER', 'PC_UNSIGNED_INTEGER',
                                  'VAX_UNSIGNED_INTEGER']
    MSB_INTEGER_TYPES = ['MSB_INTEGER', 'MAC_INTEGER', 'SUN_INTEGER', 'INTEGER']
    MSB_UNSIGNED_INTEGER_TYPES = ['MSB_UNSIGNED_INTEGER', 'UNSIGNED_INTEGER',
                                  'MAC_UNSIGNED_INTEGER', 'SUN_UNSIGNED_INTEGER']
    IEEE_REAL_TYPES = ['IEEE_REAL', 'MAC_REAL', 'SUN_REAL', 'REAL', 'FLOAT']
    PC_REAL_TYPES = ['PC_REAL']

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
        sample_type = self.get_nested_dict(
            self.label, self.LABEL_MAPPING['sample_type'])
        if "LSB" in sample_type:
            return '<'
        else:
            return '>'

    @property
    def start_byte(self):
        return self.parse_pointer(self.label['^IMAGE'], self.label['RECORD_BYTES'])[0]

    @property
    def data_filename(self):
        return self.parse_pointer(self.label['^IMAGE'], 0)[1]

    @property
    def pixel_type(self):
        sample_type = self.get_nested_dict(
            self.label, self.LABEL_MAPPING['sample_type'])
        bits = str(self.get_nested_dict(self.label, self.LABEL_MAPPING['bits']))

        if sample_type in self.LSB_INTEGER_TYPES:
            return numpy.dtype('int' + bits).newbyteorder('<')

        if sample_type in self.LSB_UNSIGNED_INTEGER_TYPES:
            return numpy.dtype('uint' + bits).newbyteorder('<')

        if sample_type in self.MSB_INTEGER_TYPES:
            return numpy.dtype('int' + bits).newbyteorder('>')

        if sample_type in self.MSB_UNSIGNED_INTEGER_TYPES:
            return numpy.dtype('uint' + bits).newbyteorder('>')

        # FIXME: IEEE_REAL and PC_REAL should be different
        if sample_type in self.IEEE_REAL_TYPES:
            return numpy.dtype('float' + bits)

        if sample_type in self.PC_REAL_TYPES:
            return numpy.dtype('float' + bits)


        raise TypeError
