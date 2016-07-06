# -*- coding: utf-8 -*-

"""Condition synchronization
"""

import time
import threading
import random


class Producer(threading.Thread):

    def __init__(self, integers, condition):
        super(Producer, self).__init__()
        self.integers = integers
        self.condition = condition

    def run(self):
        for i in range(10):
            integer = random.randint(0, 256)
            with self.condition:
                print 'condition acquired by %s' % self.name
                self.integers.append(integer)
                print '%d append to list by %s' % (integer, self.name)
                print 'condition notified by %s' % self.name
                self.condition.notify()
                print 'condition released by %s' % self.name
            time.sleep(1)


class Consumer(threading.Thread):

    def __init__(self, integers, condition):
        super(Consumer, self).__init__()
        self.integers = integers
        self.condition = condition

    def run(self):
        while True:
            with self.condition:
                print 'condition acquire by %s' % self.name
                while True:
                    if self.integers:
                        integer = self.integers.pop()
                        print '%d poped from list by %s' % (integer, self.name)
                        break
                    print 'condition wait by %s' % self.name
                    self.condition.wait()
                print 'condition released by %s' % self.name


def main():
    integers = []
    condition = threading.Condition()
    t1 = Producer(integers, condition)
    t2 = Consumer(integers, condition)
    t1.start()
    t2.start()
    t1.join()
    t2.join()


if __name__ == '__main__':
    main()
