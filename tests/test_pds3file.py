# -*- coding: utf-8 -*-
import pytest
import os
import numpy
from numpy.testing import assert_almost_equal
from planetaryimage import PDS3Image
from pvl._collections import Units


DATA_DIR = os.path.join(os.path.dirname(__file__), 'data/')
filename = os.path.join(DATA_DIR, 'pds3_1band.IMG')


@pytest.fixture
def pattern_data():
    return numpy.loadtxt(os.path.join(DATA_DIR, 'pds3_1band.txt'))


def test_pds3_1band_labels():
    image = PDS3Image.open(filename)

    assert image.filename == filename
    assert image.bands == 1
    assert image.lines == 10
    assert image.samples == 10
    assert image.format == 'BAND_SEQUENTIAL'
    assert image.pixel_type == numpy.dtype('>i2')
    assert image.dtype == numpy.dtype('>i2')
    assert image.start_byte == 640
    assert image.shape == (1, 10, 10)
    assert image.byte_order == '>'
    assert image.size == 100


def test_pds3_1band_image_format(pattern_data):
    image = PDS3Image.open(filename)

    assert image.data.shape == (10, 10)
    assert image.data.size == 100

    assert_almost_equal(image.data, pattern_data.reshape(10, 10))


def test_pds3_1band_disk_format(pattern_data):
    image = PDS3Image(open(filename, 'rb'), memory_layout='DISK')

    assert image.data.shape == (1, 10, 10)
    assert image.data.size == 100

    assert_almost_equal(image.data[0], pattern_data)


def test_parse_pointer():
    # Example tests/mission_data/1p432690858esfc847p2111l2m1.img
    assert PDS3Image.parse_pointer(56, 640) == [35200, None]
    # Example tests/mission_data/W1782844276_1.LBL
    assert PDS3Image.parse_pointer(["W1782844276_1.IMG", 5], 1024) == [4096, 'W1782844276_1.IMG']
    # TODO: Awaiting other known valid examples to implement remaining conditions
    #print PDS3Image.parse_pointer("W1782844276_1.IMG", 1024)
    #print PDS3Image.parse_pointer(["W1782844276_1.IMG"], 1024)
    # ^IMAGE                         = 101337 <BYTES>
    assert PDS3Image.parse_pointer(Units(value=101337, units='BYTES'), None) == [101337, None]
