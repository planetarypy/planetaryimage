# -*- coding: utf-8 -*-
from pvl._collections import Units
from .image import PlanetaryImage
import numpy
import six


class PDS3Image(PlanetaryImage):

    """A PDS3 image reader.

    Examples
    --------

    >>> from planetaryimage import PDS3Image
    >>> image = PDS3Image.open('tests/mission_data/2p129641989eth0361p2600r8m1.img')
    >>> image
    tests/mission_data/2p129641989eth0361p2600r8m1.img
    >>> image.label['IMAGE']['LINES']
    64

    """

    LSB_INTEGER_TYPES = ['LSB_INTEGER', 'PC_INTEGER', 'VAX_INTEGER']
    LSB_UNSIGNED_INTEGER_TYPES = ['LSB_UNSIGNED_INTEGER', 'PC_UNSIGNED_INTEGER',
                                  'VAX_UNSIGNED_INTEGER']
    MSB_INTEGER_TYPES = ['MSB_INTEGER', 'MAC_INTEGER', 'SUN_INTEGER', 'INTEGER']
    MSB_UNSIGNED_INTEGER_TYPES = ['MSB_UNSIGNED_INTEGER', 'UNSIGNED_INTEGER',
                                  'MAC_UNSIGNED_INTEGER', 'SUN_UNSIGNED_INTEGER'
                                  ]
    IEEE_REAL_TYPES = ['IEEE_REAL', 'MAC_REAL', 'SUN_REAL', 'REAL', 'FLOAT']
    PC_REAL_TYPES = ['PC_REAL']

    BAND_STORAGE_TYPE = {
        'BAND_SEQUENTIAL': '_parse_band_sequential_data'
    }

    def __init__(self, *args, **kwargs):
        if 'memory_layout' not in kwargs:
            kwargs['memory_layout'] = 'IMAGE'
        if 'compression' not in kwargs:
            kwargs['compression'] = None
        super(PDS3Image, self).__init__(*args, **kwargs)

    @staticmethod
    def parse_pointer(pointer_data, record_bytes):
        """Parses the pointer label.

        Parameters
        ----------
        pointer_data
            Supported values for `pointer_data` are::

                ^PTR = nnn
                ^PTR = nnn <BYTES>
                ^PTR = "filename"
                ^PTR = ("filename")
                ^PTR = ("filename", nnn)
                ^PTR = ("filename", nnn <BYTES>)

        record_bytes
            Record multiplier value

        Returns
        -------
        object_location : array
            Returns an array like::

                [start_byte, filename]
                [start_byte, None]
                [0, filename]
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
        format_val = self.label.get('IMAGE').get('format')
        return format_val if format_val else 'BAND_SEQUENTIAL'

    @property
    def byte_order(self):
        return self.data.dtype.byteorder

    @property
    def start_byte(self):
        record_bytes = self.label.get('RECORD_BYTES', None)
        return self.parse_pointer(self.label['^IMAGE'], record_bytes)[0]

    @property
    def data_filename(self):
        return self.parse_pointer(self.label['^IMAGE'], 0)[1]

    @property
    def bands(self):
        bands = self.label.get('IMAGE').get('BANDS')
        return bands if bands else 1

    @property
    def lines(self):
        """Number of lines in the image."""
        return self.label['IMAGE']['LINES']

    @property
    def samples(self):
        """Number of samples in a line."""
        return self.label['IMAGE']['LINE_SAMPLES']

    @property
    def dtype(self):
        """
        Pixel data type overrides the implementation in PlanetaryImage
        because PDS3 SAMPLE_TYPE expresses BOTH byte ordering and type.
        Unlike ISIS CubeFile labels, which apparently express these as
        separate label values.
        """
        return self.pixel_type

    @property
    def pixel_type(self):
        """The ``numpy.dtype`` of the pixels in the image."""
        sample_type = self.label['IMAGE']['SAMPLE_TYPE']
        bits = self.label['IMAGE']['SAMPLE_BITS']
        # get bytes to match NumPy dtype expressions
        sample_bytes = str(int(bits / 8))

        if sample_type in self.LSB_INTEGER_TYPES:
            return numpy.dtype('<i' + sample_bytes)

        if sample_type in self.LSB_UNSIGNED_INTEGER_TYPES:
            return numpy.dtype('<u' + sample_bytes)

        if sample_type in self.MSB_INTEGER_TYPES:
            return numpy.dtype('>i' + sample_bytes)

        if sample_type in self.MSB_UNSIGNED_INTEGER_TYPES:
            return numpy.dtype('>u' + sample_bytes)

        # I am guessing byte order by process of elimination
        if sample_type in self.IEEE_REAL_TYPES:
            return numpy.dtype('>f' + sample_bytes)

        # The byte order used here worked properly for the HiRISE product
        # DTEEC_008520_2085_009232_2085_A01.IMG
        # I'd like a little better understand of this.
        if sample_type in self.PC_REAL_TYPES:
            return numpy.dtype('<f' + sample_bytes)

        raise TypeError
