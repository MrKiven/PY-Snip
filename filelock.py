# -*- coding: utf-8 -*-

import os
import sys
from contextlib import contextmanager


def trylock(fd):
    import fcntl
    import errno
    try:
        fcntl.lockf(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError, e:
        if e.errno in (errno.EACCES, errno.EAGAIN):
            return False
        else:
            raise
    return True


@contextmanager
def with_multi_lock(tag, n, unlock_after_with=True):

    get_lock_file_path = lambda i: os.path.join(
        '/tmp/', tag + '.lock' + (str(i) if i else ''))

    for i in range(n):
        lock_file_path = get_lock_file_path(i)
        fd = os.open(lock_file_path, os.O_CREAT | os.O_RDWR, 0660)
        try:
            if trylock(fd):
                yield True
                break
        finally:
            if unlock_after_with:
                os.close(fd)
    else:
        yield False


def multi_processes(n, argv_num=1):
    def deco(f):
        def _(*a, **kw):
            lock_tag = (os.path.abspath(sys.argv[0]).lstrip('/') + ''.join(sys.argv[1:])).replace('/', '_')   # noqa
            with with_multi_lock(lock_tag, n) as is_success:
                if is_success:
                    return f(*a, **kw)
                else:
                    print >> sys.stderr, "There is %s instance(s) of" % n, sys.argv, "running. Quit"  # noqa
                    sys.exit(0)
        return _
    return deco

single_process = multi_processes(1)
