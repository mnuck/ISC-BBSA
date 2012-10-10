#!/usr/bin/env python
#
# BBSA Auto-Benchmark

import random
from bitarray import bitarray


class bit_string(object):
    def __init__(self, data=''):
        self.data = bitarray(data)

    def get_neighbors(self):
        result = list()
        for i in xrange(len(self.data)):
            data = bitarray(self.data)
            data[i] ^= 1
            result.append(bit_string(data))
        return result

    def get_random(self, length=None):
        if length is None:
            length = len(self.data)
        data = ''.join([random.choice(['0', '1'])
                        for i in xrange(length)])
        return bit_string(data)

    def __eq__(self, other):
        return self.data == other.data

    def __str__(self):
        return self.data.to01()

    def __repr__(self):
        return self.__str__()
