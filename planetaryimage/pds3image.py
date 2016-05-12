# -*- coding: utf-8 -*-
import numpy
import six
import os
import pvl
import collections

from .image import PlanetaryImage
from .decoders import BandSequentialDecoder


class Pointer(collections.namedtuple('Pointer', ['filename', 'bytes'])):
    @staticmethod
    def _parse_bytes(value, record_bytes):
        if isinstance(value, six.integer_types):
            return (value - 1) * record_bytes

        if isinstance(value, pvl.Units) and value.units == 'BYTES':
            return value.value

        raise ValueError('Unsupported pointer type')

    @classmethod
    def parse(cls, value, record_bytes):
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
        Pointer object
        """
        if isinstance(value, six.string_types):
            return cls(value, 0)

        if isinstance(value, list):
            if len(value) == 1:
                return cls(value[0], 0)

            if len(value) == 2:
                return cls(value[0], cls._parse_bytes(value[1], record_bytes))

            raise ValueError('Unsupported pointer type')

        return cls(None, cls._parse_bytes(value, record_bytes))


class PDS3Image(PlanetaryImage):
    """A PDS3 image reader.

    Examples
    --------
      >>> from planetaryimage import PDS3Image
      >>> testfile = 'tests/mission_data/2p129641989eth0361p2600r8m1.img'
      >>> image = PDS3Image.open(testfile)
      >>> # Examples of PDS3Image Attributes
      >>> image.dtype
      dtype('>i2')
      >>> image.record_bytes
      128
      >>> image.data_filename

    """

    SAMPLE_TYPES = {
        'MSB_INTEGER': '>i',
        'INTEGER': '>i',
        'MAC_INTEGER': '>i',
        'SUN_INTEGER': '>i',

        'MSB_UNSIGNED_INTEGER': '>u',
        'UNSIGNED_INTEGER': '>u',
        'MAC_UNSIGNED_INTEGER': '>u',
        'SUN_UNSIGNED_INTEGER': '>u',

        'LSB_INTEGER': '<i',
        'PC_INTEGER': '<i',
        'VAX_INTEGER': '<i',

        'LSB_UNSIGNED_INTEGER': '<u',
        'PC_UNSIGNED_INTEGER': '<u',
        'VAX_UNSIGNED_INTEGER': '<u',

        'IEEE_REAL': '>f',
        'FLOAT': '>f',
        'REAL': '>f',
        'MAC_REAL': '>f',
        'SUN_REAL': '>f',

        'IEEE_COMPLEX': '>c',
        'COMPLEX': '>c',
        'MAC_COMPLEX': '>c',
        'SUN_COMPLEX': '>c',

        'PC_REAL': '<f',
        'PC_COMPLEX': '<c',

        'MSB_BIT_STRING': '>S',
        'LSB_BIT_STRING': '<S',
        'VAX_BIT_STRING': '<S',
    }

    DTYPES = {
        '>i': 'MSB_INTEGER',
        '>u': 'MSB_UNSIGNED_INTEGER',
        '<i': 'LSB_INTEGER',
        '<u': 'LSB_UNSIGNED_INTEGER',
        '>f': 'IEEE_REAL',
        '>c': 'IEEE_COMPLEX',
        '<f': 'PC_REAL',
        '<c': 'PC_COMPLEX',
        '>S': 'MSB_BIT_STRING',
        '<S': 'LSB_BIT_STRING',
    }

    def _save(self, file_to_write, overwrite):
        """Save PDS3Image object as PDS3 file.

        Parameters
        ----------
        filename: Set filename for the pds image to be saved.
        Overwrite: Use this keyword to save image with same filename.

        Usage: image.save('temp.IMG', overwrite=True)

        """
        if overwrite:
            file_to_write = self.filename
        elif os.path.isfile(file_to_write):
            msg = 'File ' + file_to_write + ' already exists !\n' + \
                  'Call save() with "overwrite = True" to overwrite the file.'
            raise IOError(msg)

        encoder = pvl.encoder.PDSLabelEncoder
        serial_label = pvl.dumps(self.label, cls=encoder)
        label_sz = len(serial_label)
        image_pointer = int(label_sz / self.label['RECORD_BYTES']) + 1
        self.label['^IMAGE'] = image_pointer + 1

        if self._sample_bytes != self.label['IMAGE']['SAMPLE_BITS'] * 8:
            self.label['IMAGE']['SAMPLE_BITS'] = self.data.itemsize * 8

        sample_type_to_save = self.DTYPES[self._sample_type[0] + self.dtype.kind]
        self.label['IMAGE']['SAMPLE_TYPE'] = sample_type_to_save

        if len(self.data.shape) == 3:
            self.label['IMAGE']['BANDS'] = self.data.shape[0]
            self.label['IMAGE']['LINES'] = self.data.shape[1]
            self.label['IMAGE']['LINE_SAMPLES'] = self.data.shape[2]
        else:
            self.label['IMAGE']['BANDS'] = 1
            self.label['IMAGE']['LINES'] = self.data.shape[0]
            self.label['IMAGE']['LINE_SAMPLES'] = self.data.shape[1]

        diff = 0
        if len(pvl.dumps(self.label, cls=encoder)) != label_sz:
            diff = abs(label_sz - len(pvl.dumps(self.label, cls=encoder)))
        pvl.dump(self.label, file_to_write, cls=encoder)
        offset = image_pointer * self.label['RECORD_BYTES'] - label_sz
        stream = open(file_to_write, 'a')
        for i in range(0, offset+diff):
            stream.write(" ")

        if (self._bands > 1 and self._format != 'BAND_SEQUENTIAL'):
            raise NotImplementedError
        else:
            self.data.tofile(stream, format='%' + self.dtype.kind)
        stream.close()

    def _create_label(self, array):
        """Create sample PDS3 label for NumPy Array.
        It is called by 'image.py' to create PDS3Image object
        from Numpy Array.

        Returns
        -------
        PVLModule label for the given NumPy array.

        Usage: self.label = _create_label(array)

        """
        if len(array.shape) == 3:
            bands = array.shape[0]
            lines = array.shape[1]
            line_samples = array.shape[2]
        else:
            bands = 1
            lines = array.shape[0]
            line_samples = array.shape[1]
        record_bytes = line_samples * array.itemsize
        label_module = pvl.PVLModule([
            ('PDS_VERSION_ID', 'PDS3'),
            ('RECORD_TYPE', 'FIXED_LENGTH'),
            ('RECORD_BYTES', record_bytes),
            ('LABEL_RECORDS', 1),
            ('^IMAGE', 1),
            ('IMAGE',
                {'BANDS': bands,
                 'LINES': lines,
                 'LINE_SAMPLES': line_samples,
                 'MAXIMUM': 0,
                 'MEAN': 0,
                 'MEDIAN': 0,
                 'MINIMUM': 0,
                 'SAMPLE_BITS': array.itemsize * 8,
                 'SAMPLE_TYPE': 'MSB_INTEGER',
                 'STANDARD_DEVIATION': 0})
            ])
        return self._update_label(label_module, array)

    def _update_label(self, label, array):
        """Update PDS3 label for NumPy Array.
        It is called by '_create_label' to update label values
        such as,
        - ^IMAGE, RECORD_BYTES
        - STANDARD_DEVIATION
        - MAXIMUM, MINIMUM
        - MEDIAN, MEAN

        Returns
        -------
        Update label module for the NumPy array.

        Usage: self.label = self._update_label(label, array)

        """
        maximum = float(numpy.max(array))
        mean = float(numpy.mean(array))
        median = float(numpy.median(array))
        minimum = float(numpy.min(array))
        stdev = float(numpy.std(array, ddof=1))

        encoder = pvl.encoder.PDSLabelEncoder
        serial_label = pvl.dumps(label, cls=encoder)
        label_sz = len(serial_label)
        image_pointer = int(label_sz / label['RECORD_BYTES']) + 1

        label['^IMAGE'] = image_pointer + 1
        label['LABEL_RECORDS'] = image_pointer
        label['IMAGE']['MEAN'] = mean
        label['IMAGE']['MAXIMUM'] = maximum
        label['IMAGE']['MEDIAN'] = median
        label['IMAGE']['MINIMUM'] = minimum
        label['IMAGE']['STANDARD_DEVIATION'] = stdev

        return label

    @property
    def _bands(self):
        try:
            if len(self.data.shape) == 3:
                return self.data.shape[0]
            else:
                return 1
        except AttributeError:
            return self.label['IMAGE'].get('BANDS', 1)

    @property
    def _lines(self):
        try:
            if len(self.data.shape) == 3:
                return self.data.shape[1]
            else:
                return self.data.shape[0]
        except AttributeError:
            return self.label['IMAGE']['LINES']

    @property
    def _samples(self):
        try:
            if len(self.data.shape) == 3:
                return self.data.shape[2]
            else:
                return self.data.shape[1]
        except AttributeError:
            return self.label['IMAGE']['LINE_SAMPLES']

    @property
    def _format(self):
        return self.label['IMAGE'].get('BAND_STORAGE_TYPE', 'BAND_SEQUENTIAL')

    @property
    def _start_byte(self):
        return self._image_pointer.bytes

    @property
    def _data_filename(self):
        return self._image_pointer.filename

    @property
    def _dtype(self):
        return self._pixel_type.newbyteorder(self._byte_order)

    @property
    def record_bytes(self):
        """Number of bytes for fixed length records."""
        return self.label.get('RECORD_BYTES', 0)

    @property
    def _image_pointer(self):
        return Pointer.parse(self.label['^IMAGE'], self.record_bytes)

    @property
    def _sample_type(self):
        sample_type = self.label['IMAGE']['SAMPLE_TYPE']
        try:
            return self.SAMPLE_TYPES[sample_type]
        except KeyError:
            raise ValueError('Unsupported sample type: %r' % sample_type)

    @property
    def _sample_bytes(self):
        # get bytes to match NumPy dtype expressions
        try:
            return self.data.itemsize
        except AttributeError:
            return int(self.label['IMAGE']['SAMPLE_BITS'] / 8)

    # FIXME:  This dtype overrides the Image.dtype right?  Then whats the point
    # of _dtype above here ^^, should we just rename this one _dtype and remove
    # the other one?
    @property
    def dtype(self):
        """Pixel data type."""
        try:
            return self.data.dtype
        except AttributeError:
            return numpy.dtype('%s%d' % (self._sample_type, self._sample_bytes))

    @property
    def _decoder(self):
        if self.format == 'BAND_SEQUENTIAL':
            return BandSequentialDecoder(
                self.dtype, self.shape, self.compression
            )
        raise ValueError('Unkown format (%s)' % self.format)
