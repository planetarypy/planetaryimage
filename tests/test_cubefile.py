# -*- coding: utf-8 -*-
import pytest
import os
import numpy
from numpy.testing import assert_almost_equal
from planetaryimage import CubeFile


DATA_DIR = os.path.join(os.path.dirname(__file__), 'data/')


def test_cubefile_labels():
    filename = os.path.join(DATA_DIR, 'pattern.cub')
    image = CubeFile.open(filename)

    assert image.filename == filename
    assert image.bands == 1
    assert image.lines == 90
    assert image.samples == 90
    assert image.tile_lines == 128
    assert image.tile_samples == 128
    assert image.format == 'Tile'
    assert image.dtype == numpy.dtype('float32')
    assert image.base == 0.0
    assert image.multiplier == 1.0
    assert image.start_byte == 65536
    assert image.shape == (1, 90, 90)
    assert image.size == 8100

    filename = os.path.join(DATA_DIR, 'pattern.cub')
    image = CubeFile.open(filename)

    assert image.data.shape == (1, 90, 90)
    assert image.data.size == 8100

    expected_filename = os.path.join(DATA_DIR, 'pattern.txt')
    expected = numpy.loadtxt(expected_filename, skiprows=2).reshape((1, 90, 90))

    assert_almost_equal(image.data, expected)


def test_cubefile_save():
    filename = os.path.join(DATA_DIR, 'pattern.cub')
    image = CubeFile.open(filename)
    with pytest.raises(NotImplementedError):
        image.save('Temp_Image.cub')


def test_stream_error():
    with pytest.raises(TypeError):
        CubeFile('filename.cub')
