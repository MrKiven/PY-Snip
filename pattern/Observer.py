# -*- coding: utf-8 -*-


class Subject(object):

    def __init__(self):
        self._observers = []

    def attach(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer):
        try:
            self._observers.remove(observer)
        except ValueError:
            pass

    def notify(self, modifier=None):
        for observer in self._observers:
            if modifier != observer:
                observer.update(self)


class Data(Subject):

    def __init__(self, name=''):
        super(Data, self).__init__()
        self.name = name
        self._data = 0

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value
        self.notify()


class HexViewer(object):
    def update(self, subject):
        print 'HexViewer: Subject %s has data %d' % (subject.name, subject.data)


if __name__ == '__main__':
    data = Data('Test')
    view = HexViewer()
    data.attach(view)

    data.data = 10  # HexViewer: Subject Test has data 10

    data.data = 5  # HexViewer: Subject Test has data 5
