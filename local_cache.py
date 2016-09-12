# -*- coding: utf-8 -*-

import time


def clear_local_cache(local_cache):
    local_cache.__clear_local_cache__()


class LocalCache(object):
    __slots__ = ('__storage__',)
    cache_time = 0

    def __init__(self):
        object.__setattr__(self, '__storage__', {})

    def get_cache_time(self):
        return self.cache_time

    def get_data(self, name):
        return 1

    def _set_cache(self, name, value):
        storage = self.__storage__
        ts = time.time() + self.get_cache_time()
        storage[name] = (ts, value)

    def clear(self, name):
        self.__storage__[name] = (0, 0)

    def __clear_local_cache__(self):
        self.__storage__.clear()

    def __iter__(self):
        return iter(self.__storage__.items())

    def __getattr__(self, name):
        storage = self.__storage__
        try:
            ts, data = storage[name]
            if ts < time.time():
                data = self.get_data(name)
                self._set_cache(name, data)
        except KeyError:
            data = self.get_data(name)
            self._set_cache(name, data)
        return data

    def __setattr__(self, name, value):
        self._set_cache(name, value)

    def __delattr__(self, name):
        try:
            del self.__storage__[name]
        except KeyError:
            raise AttributeError(name)

    def __getitem__(self, name):
        return self.__getattr__(name)

    def __setitem__(self, name, value):
        self.__setattr__(name, value)

    def __delitem__(self, name):
        self.__delattr__(name)


if __name__ == '__main__':
    import random
    LOCAL_CACHE_TIME = 5  # 5 seconds

    class TestLocalCache(LocalCache):
        cache_time = LOCAL_CACHE_TIME

        def get_data(self, name):
            return random.randrange(1, 100)

    test_cache = TestLocalCache()
    print '==========Get data======='
    for i in range(5):
        print i, test_cache[i]

    print '==========Get data from local cache======='
    for i in range(5):
        print i, test_cache[i]

    print '==========Clear local cache=========='
    clear_local_cache(test_cache)
    for i in range(5):
        print i, test_cache[i]

    print '==========Set local cache======='
    for i in range(5):
        test_cache[i] = 1
        print i, test_cache[i]

    print '==========Clear local cache of key 0======='
    test_cache.clear(0)
    for i in range(5):
        print i, test_cache[i]

    time.sleep(LOCAL_CACHE_TIME)
    print '==========Local cache expired======'
    for i in range(5):
        print i, test_cache[i]
