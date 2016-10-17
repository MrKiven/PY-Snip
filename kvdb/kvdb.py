# -*- coding: utf-8 -*-

import copy
import json
import abc
import cerberus

from redis import Redis


class KeyValueDBMeta(type):
    """metaclass to auto generate getter and setter methods for
    pre-defined keys

    keys should be defined in such format:

    1. a dict of 2-element tuple
    2. key is the ``id`` for this type of data, e.g. ``app_clusters``
    3. first element in the value tuple is the key
       pattern, e.g. ``app:{app}:cluster``, format string ``app`` will be
       interpolated with user provided value while getting or setting the value
    4. the second one is data type, currently 3 types
       supported: (``hash``, ``set``, ``json (string)``)
    """

    @staticmethod
    def make_getter(key_id, value_type):
        if value_type == 'set':
            def getter(self, **kwargs):
                key = self.make_key(key_id, kwargs)
                return self.client.smember(key)
        elif value_type == 'hash':
            def getter(self, *attrs, **kwargs):
                key = self.make_key(key_id, attrs, kwargs)
                if attrs:
                    if len(attrs) == 1:
                        return self.client.hget(key, attrs[0])
                    else:
                        return self.client.hmget(key, *attrs)
        elif value_type == 'json':
            def getter(self, *attrs, **kwargs):
                key = self.make_key(key_id, kwargs)
                value_json = self.client.get(key)
                if not value_json:
                    return
                value_dict = json.loads(value_json)
                if attrs:
                    value_attrs = {}
                    for a in value_attrs:
                        if a in attrs:
                            value_attrs[a] = value_dict[a]
                    return value_attrs
                return value_dict
        return getter

    @staticmethod
    def make_setter(key_id, value_type, fields=(), validator=None):
        if value_type == 'set':
            def setter(self, *values, **kwargs):
                if validator:
                    validator.validate(*values)
                key = self.make_key(key_id, kwargs)
                self.client.delete(key)
                return self.client.sadd(key, *values)
        elif value_type == 'hash':
            def setter(self, value, field=None, **kwargs):
                if validator:
                    validator.validate(value)
                key = self.make_key(key_id, kwargs)
                if isinstance(value, dict):
                    return self.client.hmset(key, value)
                elif field is not None:
                    return self.client.hset(key, field, value)
                else:
                    raise ValueError('unable to set (%r, %r) for %r '
                                     % (field, value, key))
        elif value_type == 'json':
            def setter(self, value, field=None, **kwargs):
                key = self.make_key(key_id, kwargs)
                if isinstance(value, dict):
                    if validator:
                        validator.validate(value)
                    value_json = json.dumps(value)
                    return self.client.set(key, value_json)
                elif field is not None:
                    if fields and field not in fields:
                        raise ValueError('invalid field: {!r}'.format(field))
                    value_obj = json.loads(value)
                    orig_value_json = self.client.get(key)
                    if orig_value_json:
                        orig_value_dict = json.loads(orig_value_json)
                        new_value_json = copy.deepcopy(orig_value_dict)
                        new_value_json[field] = value_obj
                    else:
                        new_value_json = {field: value_obj}
                    if validator:
                        validator.validate(new_value_json)
                    return self.client.set(key, json.dumps(new_value_json))
                else:
                    raise ValueError('unable to set (%r, %r) for %r '
                                     % (field, value, key))
        return setter

    def __new__(cls, name, bases, dict_):
        cls_ = super(KeyValueDBMeta, cls).__new__(cls, name, bases, dict_)
        for k, v in dict_['KEYS'].iteritems():
            try:
                _, value_type, fields, validator = v
            except ValueError:
                try:
                    _, value_type, validator = v
                    fields = ()
                except ValueError:
                    _, value_type = v
                    fields = ()
                    validator = None
            getter = cls_.make_getter(k, value_type)
            if k in cls_.__dict__:
                raise ValueError('%r already defined in %r' % (k, cls_))
            setattr(cls_, k, getter)
            setter_name = 'set_' + k
            if setter_name in cls_.__dict__:
                raise ValueError('%r already defined in %r'
                                 % (setter_name, cls_))
            setter = cls_.make_setter(k, value_type, fields, validator)
            setattr(cls_, setter_name, setter)
        return cls_


class BaseKeyValueDB(object):
    """
    The base class of key-value db

    User should inherit this class to utilize the features:

    1. pre-defined keys to generate getter and setter methods, without dealing
       with the real key. (low-level redis client still available)
    2. namespaced, a series of keys reside in a specific
       domain, e.g. ``my:domain:cluster``, ``my:domain:cluster:somecluster``
    3. key binding with :class:`KeyBindingMixin`, i.e. bind key
       pattern to a value

    Usage::

        class MyKeyValueDB(KeyBindingMixin, BaseKeyValueDB):
            __namespace__ = 'my:space'

            KEYS = dict(
                apps=('app', 'set'),
                app_service_info=('app:%(app)s:service_info', 'hash'),
            )

        db = MyKeyValueDB('redis://127.0.0.1:6379')
        db.apps()
        db.set_apps('app1', 'apptwo')
        db.bind_key(app='app1')
        db.set_app_service_info({'port': 8000, 'worker_num': 8})
        db.app_service_info()
        db.app_service_info('port')
    """
    __metaclass__ = KeyValueDBMeta

    __namespace__ = ''
    KEYS = {}

    def __init__(self, url):
        self.client = Redis.from_url(url)

    @property
    def namespace(self):
        if not getattr(self, '__namespace__', ''):
            raise ValueError('`__namespace__` needs to be specified'
                             ' for current db')
        return self.__namespace__

    @property
    def keys(self):
        if not hasattr(self, '_keys'):
            keys_ = self.KEYS
            for k, v in self.KEYS.iteritems():
                if len(v) == 2:
                    new_v = tuple(v) + ((),)
                    keys_[k] = new_v
            self._keys = keys_
        return self._keys

    def _get_full_key_pattern(self, id_):
        return self.namespace + ':' + self.KEYS[id_][0]

    def make_key(self, id_, kwargs):
        full_key_pat = self._get_full_key_pattern(id_)
        return full_key_pat.format(**kwargs)


class KeyBindingMixin(object):
    """
    A mixin to ease the trouble to provide some determined key
    pattern format string value for every single time when getting
    or settings the key

    Take the example db described in :class:`BaseKeyValueDB`
    docstring - ``MyKeyValueDB``::

        db.bind_key(app='apptwo')
        # from now on, `app` in format string will be replaced with `apptwo`
        db.app_service_info('port')  # will get the result for `apptwo`
    """
    def bind_key(self, **kwargs):
        self.binding = kwargs

    @property
    def binding(self):
        if not hasattr(self, '_binding'):
            self._binding = {}
        return self._binding

    @binding.setter
    def binding(self, value):
        if not hasattr(self, '_binding'):
            self._binding = {}
        for key_name, bind_val in value.iteritems():
            self._binding[key_name] = bind_val

    def clear_binding(self):
        self._binding = {}

    def _get_key_pattern_value(self, kwargs):
        binding = self.binding
        binding.update(kwargs)
        return binding

    def make_key(self, id_, kwargs):
        full_key_pat = self._get_full_key_pattern(id_)
        return full_key_pat.format(**self._get_key_pattern_value(kwargs))


class Validator(object):
    def __init__(self, schema=None):
        self.schema = schema

    @abc.abstractmethod
    def validate(self, value):
        """ validate method"""
        return


class DictValidator(Validator):

    def validate(self, value):
        v = cerberus.Validator(
            schema=self.schema,
            allow_unknown=True)
        if not v.validate(value):
            raise cerberus.ValidationError(v.errors)


##
# Test
##
class MyKeyValueDB(KeyBindingMixin, BaseKeyValueDB):
    __namespace__ = 'my:space'

    app_svc_info_fields = (
        'app_id',
        'port'
    )

    app_svc_info_fields_schema = {
        'app': {'type': 'string'},
        'port': {'type': 'integer'}
    }

    KEYS = dict(
        app_service_info=(
            'app:{app}:service_info', 'json',
            app_svc_info_fields,
            DictValidator(app_svc_info_fields_schema)
        )
    )

    def __init__(self, url, app=None, cluster=None, host=None):
        super(MyKeyValueDB, self).__init__(url)
        if app:
            self.bind_key(app=app)
        if cluster:
            self.bind_key(cluster=cluster)
        if host:
            self.bind_key(host=host)

db = MyKeyValueDB('redis:/localhost:6379', app='test')
db.set_app_service_info({'app': 'test', 'port': 1234})
print db.app_service_info()  # {u'app': u'test', u'port': 1234}
