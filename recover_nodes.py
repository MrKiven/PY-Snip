# -*- coding: utf-8 -*-


def combined_node_list(head):
    """Format node list to print for human ^ ^
    """
    s = "%s" % head.value
    while head.next:
        s += " -> %s" % head.next.value
        head = head.next
    return s


class MaxNodesError(Exception):
    pass


class ExistsNodeError(Exception):
    pass


class Node(object):

    def __init__(self, val):
        self.value = val
        self.next = None

    def __str__(self):
        s = "%s" % self.value
        if self.next:
            s += " -> %s" % self.next.value
        return s

    def __repr__(self):
        return '<Node %s>' % str(self)


class ListNodes(object):

    def __init__(self, size=10):
        self.size = size
        self.head = None
        self.current = None
        self.last = None
        self.nodes_map = {}

    def create_head(self, val="head", prefix="node"):
        if self.head:
            raise ValueError("List not empty!")
        self.head = Node('_'.join((prefix, str(val))))
        self.current = self.head
        self.nodes_map[self.head.value] = self.head

    def create_next(self, val, prefix="node"):
        if len(self.nodes_map) >= self.size:
            raise MaxNodesError("Max size of this list nodes is: %d" % self.size)
        if not self.head:
            raise ValueError("Create head node first!")
        if val in self.nodes_map:
            raise ExistsNodeError("Node exists: %s" % self.nodes_map[val])
        node = Node('_'.join((prefix, str(val))))
        self.current.next = node
        self.current = node
        self.last = node
        self.nodes_map[val] = node

    def __str__(self):
        if not self.head:
            return "Empty"
        s = "%s" % self.head.value
        current = self.head
        while current.next:
            s += " -> %s" % current.next.value
            current = current.next
        return s

    def __repr__(self):
        return "<List %s>" % str(self)


def non_recurse(head):
    if head is None or head.next is None:
        return head

    pre, current, h = None, head, head
    while current:
        h = current
        temp = current.next
        current.next = pre
        pre = current
        current = temp

    return h


def recurse(head, newhead):
    if head is None:
        return head
    if head.next is None:
        newhead = head
    else:
        newhead = recurse(head.next, newhead)
        head.next.next = head
        head.next = None
    return newhead


def example():
    max_size = 10
    mylist = ListNodes(size=max_size)
    mylist.create_head()
    for i in xrange(max_size - 1):
        mylist.create_next(i)
    print repr(mylist)  # <List node_head -> node_0 -> node_1 -> node_2 -> node_3 -> node_4 -> node_5 -> node_6 -> node_7 -> node_8>
