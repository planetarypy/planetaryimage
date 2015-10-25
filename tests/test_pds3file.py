# -*- coding: utf-8 -*-
import pytest
import os
import numpy
from numpy.testing import assert_almost_equal
from planetaryimage.pds3image import PDS3Image, Pointer
from pvl import Units


DATA_DIR = os.path.join(os.path.dirname(__file__), 'data/')
filename = os.path.join(DATA_DIR, 'pds3_1band.IMG')
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
    print("Expected: ", expected, expected.dtype, expected.shape)
    print("Actual: ", image.data, image.data.dtype, image.data.shape)
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
    print("Expected: ", expected, expected.dtype, expected.shape)
    print("Actual: ", image.data, image.data.dtype, image.data.shape)
    assert_almost_equal(image.data, expected)


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
    print("Expected: ", expected, expected.dtype, expected.shape)
    print("Actual: ", image.data, image.data.dtype, image.data.shape)
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