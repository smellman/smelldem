# -*- coding: utf-8

import struct
import gzip
import array

class DEMHeader(object):
    def __init__(self, x, y, z):
        self.x = int(x)
        self.y = int(y)
        self.z = int(z)

    def setMaxMinHeight(self, max_height, min_height):
        self.max_height = max_height
        self.min_height = min_height

class DEMAvailable(object):
    def __init__(self):
        self.availables = array.array('b')

    def addNoData(self):
        self.availables.append(0)

    def addHasData(self):
        self.availables.append(1)

    def toByteArray(self):
        t = 0b0
        ret = array.array('B')
        for i in range(0, len(self.availables)):
            bit = i % 8
            if self.availables[i] == 1:
                t = t + (1 << bit)
            if bit == 7:
                ret.append(t)
                t = 0b0
        return ret

class DEMData(object):
    def __init__(self):
        self.heights = array.array('f')

    def addHeight(self, height):
        self.heights.append(height)

    def getMaxMinHeight(self):
        return max(self.heights), min(self.heights)

    def encode(self):
        maxHeight, minHeight = self.getMaxMinHeight()
        heights = array.array('H')
        for h in self.heights:
            height = int((h - minHeight) / (maxHeight - minHeight) * 32767)
            heights.append(height)
        self.encoded_heights = zigZagEncodeArray(heights)

    def setEncodedHeights(self, h):
        self.encoded_heights = h

    def decode(self, maxHeight, minHeight):
        self.heights = array.array('f')
        decoded = zigZagDecodeArray(self.encoded_heights)
        for v in decoded:
            height = ((v / 32767.0) * (maxHeight - minHeight)) + minHeight
            self.addHeight(height)

class DEM(object):
    def __init__(self, x, y, z):
        self.header = DEMHeader(x, y, z)
        self.availables = DEMAvailable()
        self.data = DEMData()

    def write(self, f):
        # header
        print(self.header.x)
        f.write(struct.pack("I", self.header.x)) # unsigned int
        print(self.header.y)
        f.write(struct.pack("I", self.header.y))
        print(self.header.z)
        f.write(struct.pack("b", self.header.z)) # unsigned char
        f.write(struct.pack("f", self.header.max_height)) # float
        f.write(struct.pack("f", self.header.min_height))

        # available
        for b in self.availables.toByteArray():
            f.write(struct.pack("B", b))

        # data
        f.write(struct.pack("I", len(self.data.encoded_heights))) # unsigned int
        for b in self.data.encoded_heights:
            f.write(struct.pack("H", b)) # unsigned short
        f.close()

    @staticmethod
    def generateFromGSIDem(x, y, z, input_file, output_file, gzipped=False):
        dem = DEM(x, y, z)
        fp = open(input_file, 'r')
        lines = fp.readlines()
        fp.close()
        for l in lines:
            l = l.strip()
            for h in l.split(","):
                if h == "e":
                    dem.availables.addNoData()
                else:
                    height = float(h)
                    dem.availables.addHasData()
                    dem.data.addHeight(height)
        dem.data.encode()
        maxHeight, minHeight = dem.data.getMaxMinHeight()
        dem.header.setMaxMinHeight(maxHeight, minHeight)

        if gzipped:
            f = gzip.open(output_file, 'wb')
        else:
            f = open(output_file, 'wb')
        dem.write(f)

    @staticmethod
    def read(input_file, gzipped=False):
        if gzipped:
            f = gzip.open(input_file, 'rb')
        else:
            f = open(input_file, 'rb')
        # header
        x, y = struct.unpack('II', f.read(4 * 2))
        (z,) = struct.unpack('b', f.read(1))
        maxHeight, minHeight = struct.unpack('ff', f.read(4*2))

        dem = DEM(x, y, z)
        dem.header.setMaxMinHeight(maxHeight, minHeight)

        # available
        a = array.array('b')
        for t in range(0, int(256*256 / 8)):
            (v,) = struct.unpack('B', f.read(1))
            for i in range(0, 8):
                if v & (1 << i) != 0:
                    a.append(1)
                else:
                    a.append(0)
        dem.availables.availables = a

        # data
        (length,) = struct.unpack("I", f.read(4))
        h = array.array('H') # encoded value
        for i in range(0, length):
            (v,) = struct.unpack('H', f.read(2))
            h.append(v)
        dem.data.setEncodedHeights(h)
        dem.data.decode(maxHeight, minHeight)
        f.close()
        return dem

    def outputGSIDEM(self, output_file):
        fp = open(output_file, 'w')
        data_pos = 0
        for y in range(0, 256):
            line = []
            for x in range(0, 256):
                pos = (y * 256) + x
                if self.availables.availables[pos] == 0:
                    line.append("e")
                else:
                    line.append(str(round(self.data.heights[data_pos], 2)))
                    data_pos = data_pos + 1
            fp.write(",".join(line))
            fp.write("\n")
        fp.close()

    @staticmethod
    def readDEMandWriteGSIDEM(input_file, output_file):
        dem = DEM.read(input_file)
        dem.outputGSIDEM(output_file)

def zigZagEncodeArray(values):
    ret = array.array('H')
    pre = 0
    for buf in values:
        value = ((buf << 1) ^ (buf >> 15))
        if pre <= value:
            ret.append(value - pre)
        else:
            ret.append(pre - value - 1)
        pre = value
    return ret

def zigZagDecodeArray(values):
    ret = array.array('H')
    t = 0
    for v in values:
        t += (v >> 1) ^ (-(v & 1))
        ret.append(t)
    return ret
