# -*- coding: utf-8 -*-

import sys
import math
from bisect import bisect

if sys.version_info >= (2, 5):
    import hashlib
    md5_constructor = hashlib.md5
else:
    import md5
    md5_constructor = md5.new


class HashRing(object):
    def __init__(self, nodes=None, weights=None):
        self.ring = dict()
        self._sorted_keys = []
        self.nodes = nodes

        if not weights:
            weights = {}
        self.weights = weights

        self._generate_circle()

    def _generate_circle(self):
        total_weight = 0
        for node in self.nodes:
            total_weight += self.weights.get(node, 1)

        for node in self.nodes:
            weight = 1

            if node in self.weights:
                weight = self.weights.get(node)

            factor = math.floor((40 * len(self.nodes) * weight) / total_weight)

            for j in range(0, int(factor)):
                b_key = self._hash_digest('%s_%s' % (node, j))

                for i in range(0, 3):
                    key = self._hash_val(b_key, lambda x: x + i * 4)
                    self.ring[key] = node
                    self._sorted_keys.append(key)

        self._sorted_keys.sort()

    def get_node(self, string_key):
        pos = self.get_node_pos(string_key)
        if pos is None:
            return None
        return self.ring[self._sorted_keys[pos]]

    def get_node_pos(self, string_key):
        if not self.ring:
            return None
        key = self.gen_key(string_key)

        nodes = self._sorted_keys
        pos = bisect(nodes, key)
        if pos == len(nodes):
            return 0
        else:
            return pos

    def iterate_nodes(self, string_key, distinct=True):
        if not self.ring:
            yield None, None

        returned_values = set()

        def distinct_filter(value):
            if str(value) not in returned_values:
                returned_values.add(str(value))
                return value

        pos = self.get_node_pos(string_key)
        for key in self._sorted_keys[pos:]:
            val = distinct_filter(self.ring[key])
            if val:
                yield val

        for i, key in enumerate(self._sorted_keys):
            if i < pos:
                val = distinct_filter(self.ring[key])
                if val:
                    yield val

    def gen_key(self, key):
        b_key = self._hash_digest(key)
        return self._hash_val(b_key, lambda x: x)

    def _hash_val(self, b_key, entry_fn):
        return (
            (b_key[entry_fn(3)] << 24)
            |(b_key[entry_fn(2)] << 16)
            |(b_key[entry_fn(1)] << 8)
            |(b_key[entry_fn(0)])
        )

    def _hash_digest(self, key):
        m = md5_constructor()
        m.update(bytes(key))
        return list(map(ord, str(m.digest())))


servers = ['192.168.1.1', '192.168.1.2']
weights = {
    '192.168.1.1': 1,
    '192.168.1.2': 2
}
ring = HashRing(servers, weights)
for i in range(10):
    key = 'key_%s' % i
    server = ring.get_node(key)
    print key, '==>', server
