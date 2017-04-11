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


class Node(object):

    def __init__(self, val):
        self.value = val
        self.next = None

    def __repr__(self):
        s = "%s" % self.value
        if self.next:
            s += " -> %s" % self.next.value
        return s


class ListNodes(object):

    def __init__(self, size=10):
        self.size = size
        self.head = None
        self.current = None
        self.last = None
        self.nodes = []

    def create_head(self, val="head", prefix="node"):
        if self.head:
            raise ValueError("List not empty!")
        self.head = Node('_'.join((prefix, str(val))))
        self.current = self.head
        self.nodes.append(self.head)

    def create_next(self, val, prefix="node"):
        if len(self.nodes) >= self.size:
            raise MaxNodesError("Max size of this list nodes is: %d" % self.size)
        if not self.head:
            raise ValueError("Create head node first!")
        node = Node('_'.join((prefix, str(val))))
        self.current.next = node
        self.current = node
        self.last = node
        self.nodes.append(node)

    def __str__(self):
        s = "%s" % self.head.value
        current = self.head
        while current.next:
            s += " -> %s" % current.next.value
            current = current.next
        return s


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


my_lists = ListNodes()
my_lists.create_head()
for i in xrange(8):
    my_lists.create_next(i)


print my_lists  # node_head -> node_0 -> node_1 -> node_2 -> node_3 -> node_4 -> node_5 -> node_6 -> node_7

"""
new_list = non_recurse(my_lists.head)
print combined_node_list(new_list)  # node_7 -> node_6 -> node_5 -> node_4 -> node_3 -> node_2 -> node_1 -> node_0 -> node_head
"""

new_list2 = recurse(my_lists.head, None)
print combined_node_list(new_list2)  # node_7 -> node_6 -> node_5 -> node_4 -> node_3 -> node_2 -> node_1 -> node_0 -> node_head
