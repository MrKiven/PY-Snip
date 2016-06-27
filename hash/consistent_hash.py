# -*- coding: utf-8 -*-

import hashlib


class YHash(object):
    def __init__(self, nodes=None, n_number=3):
        """
        :param nodes:     all nodes
        :param n_number:  v_nodes per node
        """
        self._n_number = n_number
        self._node_dict = dict()
        self._sort_list = []
        self.nodes = nodes
        if self.nodes:
            for node in self.nodes:
                self.add_node(node)

    def add_node(self, node):
        self._add_nodes_map(node)
        self._sort_list.sort()

    def _add_nodes_map(self, node):
        for i in xrange(self._n_number):
            node_str = "%s%s" % (node, i)
            key = self._gen_key(node_str)
            self._node_dict[key] = node
            self._sort_list.append(key)

    def remove_node(self, node):
        for i in xrange(self._n_number):
            node_str = "%s%s" % (node, i)
            key = self._gen_key(node_str)
            del self._node_dict[key]
            self._sort_list.remove(key)

    def get_node(self, key_str):
        if self._sort_list:
            key = self._gen_key(key_str)
            for node_key in self._sort_list:
                if key <= node_key:
                    return self._node_dict[node_key]
            return self._node_dict[self._sort_list[0]]
        else:
            return None

    @staticmethod
    def _gen_key(key_str):
        md5_str = hashlib.md5(key_str).hexdigest()
        return long(md5_str, 16)

    def _sort_nodes(self):
        self._sort_list = sorted(self._sort_list, key=lambda x: x[0])


nodes = ['192.168.0.1', '192.168.0.2']

h = YHash(nodes)
for i in xrange(10):
    key = 'test_%s' % i
    server = h.get_node(key)
    print key, '===>', server
