import numpy
from six.moves import range


class BandSequentialDecoder(object):
    def __init__(self, dtype, shape, compression=None):
        self.dtype = dtype
        self.shape = shape
        self.sample_bytes = dtype.itemsize
        self.compression = compression

    @property
    def size(self):
        return numpy.product(self.shape)

    def decode(self, stream):
        if self.compression:
            data = numpy.fromstring(stream.read(self.size*self.sample_bytes), self.dtype)
        else:
            data = numpy.fromfile(stream, self.dtype, self.size)
        return data.reshape(self.shape)


class TileDecoder(object):
    def __init__(self, dtype, shape, tile_shape):
        self.dtype = dtype
        self.shape = shape
        self.tile_shape = tile_shape

    def decode(self, stream):
        bands, lines, samples = self.shape
        tile_lines, tile_samples = self.tile_shape
        tile_size = tile_lines * tile_samples
        data = numpy.empty(self.shape, dtype=self.dtype)

        for band in data:
            for line in range(0, lines, tile_lines):
                for sample in range(0, samples, tile_samples):
                    sample_end = sample + tile_samples
                    line_end = line + tile_lines
                    chunk = band[line:line_end, sample:sample_end]

                    tile = numpy.fromfile(stream, self.dtype, tile_size)
                    tile = tile.reshape((tile_lines, tile_samples))

                    chunk_lines, chunk_samples = chunk.shape
                    chunk[:] = tile[:chunk_lines, :chunk_samples]

        return data
