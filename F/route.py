# -*- coding: utf-8 -*-


class NotFlask():

    def __init__(self, name):
        self.name = name
        self.view_functions = {}

    def route(self, r):
        def _(f):
            self.view_functions[r] = f
            return f
        return _

    def serve(self, path):
        """Mock http server"""
        v_f = self.view_functions.get(path)
        if v_f:
            return v_f()
        else:
            raise ValueError("Route {!r} has not been registered".format(path))


app = NotFlask(__name__)


@app.route('/index')
def index():
    return "Index"

assert app.serve('/index') == 'Index'
