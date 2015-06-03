# -*- coding: utf-8 -*-
import pytest
import os
import numpy
from numpy.testing import assert_almost_equal
from planetaryimage import PDS3Image


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
    assert image.pixel_type == numpy.dtype('int16')
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
