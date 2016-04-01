# -*- coding: utf-8 -*-
import pytest
import os
import numpy
from numpy.testing import assert_almost_equal
from planetaryimage.pds3image import PDS3Image, Pointer
from pvl import Units


DATA_DIR = os.path.join(os.path.dirname(__file__), 'data/')
filename = os.path.join(DATA_DIR, 'pds3_1band.IMG')
filename_3bands = os.path.join(DATA_DIR, 'pds3_3bands.IMG')
filename_float = os.path.join(DATA_DIR, 'pds3_1band_float.IMG')
gzipped_filename = os.path.join(DATA_DIR, 'pds3_1band.IMG.gz')
bz2_filename = os.path.join(DATA_DIR, 'pds3_1band.IMG.bz2')


@pytest.fixture
def expected():
    return numpy.loadtxt(os.path.join(DATA_DIR, 'pds3_1band.txt')).reshape(
        (1, 10, 10)
    )


def test_pds3_1band_labels(expected):
    image = PDS3Image.open(filename)

    assert image.filename == filename
    assert image.bands == 1
    assert image.lines == 10
    assert image.samples == 10
    assert image.format == 'BAND_SEQUENTIAL'
    assert image.dtype == numpy.dtype('>i2')
    assert image.start_byte == 640
    assert image.shape == (1, 10, 10)
    # FIXME: Doublecheck that consolidating pixel_type and byte order
    #        is actually OK for PDS images.  I think here at the object level
    #        its OK even though in the PDS labels the information is separate.
    assert image.size == 100
    assert image.compression is None

    # Testing .label
    assert image.label['FILE_RECORDS'] == 42
    assert image.label['IMAGE']['SAMPLE_TYPE'] == 'MSB_INTEGER'

    # Testing .data
    assert image.data.shape == (1, 10, 10)
    assert image.data.dtype == numpy.dtype('>i2')
    assert_almost_equal(image.data, expected)


def test_gz_pds3_1band_labels(expected):
    image = PDS3Image.open(gzipped_filename)
    assert image.filename == gzipped_filename
    assert image.bands == 1
    assert image.lines == 10
    assert image.samples == 10
    assert image.format == 'BAND_SEQUENTIAL'
    assert image.dtype == numpy.dtype('>i2')
    assert image.start_byte == 640
    assert image.shape == (1, 10, 10)
    assert image.size == 100
    assert image.compression == 'gz'

    # Testing .label
    assert image.label['FILE_RECORDS'] == 42
    assert image.label['IMAGE']['SAMPLE_TYPE'] == 'MSB_INTEGER'

    # Testing .data
    assert image.data.shape == (1, 10, 10)
    assert image.data.dtype == numpy.dtype('>i2')
    assert_almost_equal(image.data, expected)


def test_image_save():
    image = PDS3Image.open(filename)
    image.save('Temp_Image.IMG')
    new_image = PDS3Image.open('Temp_Image.IMG')
    assert image.bands == new_image.bands
    assert image.lines == new_image.lines
    assert image.samples == new_image.samples
    assert image.format == new_image.format
    assert image.dtype == new_image.dtype
    assert image.start_byte == new_image.start_byte
    assert image.shape == new_image.shape
    assert image.size == new_image.size

    # Testing .label
    assert image.label['FILE_RECORDS'] == new_image.label['FILE_RECORDS']
    label_sample_type = image.label['IMAGE']['SAMPLE_TYPE']
    assert label_sample_type == new_image.label['IMAGE']['SAMPLE_TYPE']

    # Testing .data
    assert image.data.shape == new_image.data.shape
    assert image.data.dtype == image.data.dtype
    os.remove('Temp_Image.IMG')


def test_image_save_overwrite():
    image = PDS3Image.open(filename)
    image.save('Temp_Image.IMG')
    image_temp = PDS3Image.open('Temp_Image.IMG')
    image_temp.save(overwrite=True)
    new_image = PDS3Image.open(image_temp.filename)
    assert image_temp.filename == new_image.filename
    assert image_temp.bands == new_image.bands
    assert image_temp.lines == new_image.lines
    assert image_temp.samples == new_image.samples
    assert image_temp.format == new_image.format
    assert image_temp.dtype == new_image.dtype
    assert image_temp.start_byte == new_image.start_byte
    assert image_temp.shape == new_image.shape
    assert image_temp.size == new_image.size

    # Testing .label
    assert image_temp.label['FILE_RECORDS'] == new_image.label['FILE_RECORDS']
    label_sample_type = image_temp.label['IMAGE']['SAMPLE_TYPE']
    assert label_sample_type == new_image.label['IMAGE']['SAMPLE_TYPE']

    # Testing .data
    assert image_temp.data.shape == new_image.data.shape
    assert image_temp.data.dtype == image.data.dtype
    os.remove('Temp_Image.IMG')


def test_image_save_samefile():
    image = PDS3Image.open(filename)
    with pytest.raises(IOError):
        image.save(image.filename)


def test_image_save_lines_linesamples():
    image = PDS3Image.open(filename)
    image.data = image.data[0, 3:8, 3:8]
    image.save('Temp_Image.IMG')
    image_temp = PDS3Image.open('Temp_Image.IMG')
    assert image_temp.lines == 5
    assert image_temp.samples == 5
    os.remove('Temp_Image.IMG')


def test_image_save_3bands():
    image = PDS3Image.open(filename)
    temp_data = numpy.array([image.data, image.data, image.data])
    image.data = temp_data.reshape(3, 10, 10)
    image.save('Temp_Image.IMG')
    image_temp = PDS3Image.open('Temp_Image.IMG')
    assert image_temp.bands == 3
    os.remove('Temp_Image.IMG')


def test_image_save_1band():
    image = PDS3Image.open(filename_3bands)
    image.data = image.data[0, :, :]
    image.save('Temp_Image.IMG')
    image_temp = PDS3Image.open('Temp_Image.IMG')
    assert image_temp.bands == 1
    os.remove('Temp_Image.IMG')


def test_image_save_int_to_float():
    image = PDS3Image.open(filename)
    ref_image = PDS3Image.open(filename_float)
    image.data = image.data.astype('>f4')
    image.data *= 1.5
    image.save('Temp_Image.IMG')
    image_temp = PDS3Image.open('Temp_Image.IMG')
    assert image_temp.dtype == ref_image.dtype
    assert_almost_equal(image.data, ref_image.data)
    os.remove('Temp_Image.IMG')


def test_image_save_float_to_int():
    image = PDS3Image.open(filename_float)
    ref_image = PDS3Image.open(filename)
    image.data /= 1.5
    image.data = image.data.astype('>i2')
    image.save('Temp_Image.IMG')
    image_temp = PDS3Image.open('Temp_Image.IMG')
    assert image_temp.dtype == ref_image.dtype
    assert_almost_equal(image.data, ref_image.data)
    os.remove('Temp_Image.IMG')


def test_numpy_array_save_i2():
    array = numpy.arange(100, dtype='>i2')
    array = array.reshape(1, 10, 10)
    temp = PDS3Image(array)
    temp.save('Temp_Image.IMG')
    image_temp = PDS3Image.open('Temp_Image.IMG')
    assert image_temp.bands == 1
    assert image_temp.lines == 10
    assert image_temp.samples == 10
    assert image_temp.format == 'BAND_SEQUENTIAL'
    assert image_temp.dtype == '>i2'
    assert image_temp.shape == (1, 10, 10)
    assert image_temp.size == 100
    assert_almost_equal(image_temp.data, array)
    os.remove('Temp_Image.IMG')


def test_numpy_array_save_f4():
    array = numpy.arange(100)
    array = array.reshape(1, 10, 10)
    array = array * 1.5
    array = array.astype('>f4')
    temp = PDS3Image(array)
    temp.save('Temp_Image.IMG')
    image_temp = PDS3Image.open('Temp_Image.IMG')
    assert image_temp.bands == 1
    assert image_temp.lines == 10
    assert image_temp.samples == 10
    assert image_temp.format == 'BAND_SEQUENTIAL'
    assert image_temp.dtype == '>f4'
    assert image_temp.shape == (1, 10, 10)
    assert image_temp.size == 100
    assert_almost_equal(image_temp.data, array)
    os.remove('Temp_Image.IMG')


def test_bz2_pds3_1band_labels(expected):
    image = PDS3Image.open(bz2_filename)
    assert image.filename == bz2_filename
    assert image.bands == 1
    assert image.lines == 10
    assert image.samples == 10
    assert image.format == 'BAND_SEQUENTIAL'
    assert image.dtype == numpy.dtype('>i2')
    assert image.start_byte == 640
    assert image.shape == (1, 10, 10)
    assert image.size == 100
    assert image.compression == 'bz2'

    # Testing .label
    assert image.label['FILE_RECORDS'] == 42
    assert image.label['IMAGE']['SAMPLE_TYPE'] == 'MSB_INTEGER'

    # Testing .data
    assert image.data.shape == (1, 10, 10)
    assert image.data.dtype == numpy.dtype('>i2')
    assert_almost_equal(image.data, expected)


def test_parse_pointer():
    # ^PTR = nnn
    # Example tests/mission_data/1p432690858esfc847p2111l2m1.img
    assert Pointer.parse(56, 640) == Pointer(None, 35200)

    # ^PTR = nnn <BYTES>
    assert Pointer.parse(Units(101337, 'BYTES'), 0) == Pointer(None, 101337)

    # ^PTR = "filename"
    assert Pointer.parse('W1782844276_1.IMG', 1024) == Pointer('W1782844276_1.IMG', 0)

    # ^PTR = ("filename")
    assert Pointer.parse(['W1782844276_1.IMG'], 1024) == Pointer('W1782844276_1.IMG', 0)

    # ^PTR = ("filename", nnn)
    # Example tests/mission_data/W1782844276_1.LBL
    assert Pointer.parse(['W1782844276_1.IMG', 5], 1024) == Pointer('W1782844276_1.IMG', 4096)

    # ^PTR = ("filename", nnn <BYTES>)
    assert Pointer.parse(['W1782844276_1.IMG', Units(101337, 'BYTES')], 1024) == Pointer('W1782844276_1.IMG', 101337)

    # Test bad type
    with pytest.raises(ValueError):
        Pointer.parse(None, 64)

    # Test wrong sized arrays
    with pytest.raises(ValueError):
        Pointer.parse([], 64)

    with pytest.raises(ValueError):
        Pointer.parse(['W1782844276_1.IMG', 5, 6], 64)
