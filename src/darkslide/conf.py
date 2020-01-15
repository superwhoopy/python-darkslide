"""TODO"""

import codecs
import collections
import itertools
import os

from six import string_types
from six.moves import configparser, filter

from . import utils

class UserConfig(collections.UserDict):
    """TODO"""
    VALID_LINENOS = ('no', 'inline', 'table')

    DEFAULT_VALUES = {
        'linenos' : 'inline',
        'source' : [],
        'copy_theme' : False,
        'destination_file' : 'presentation.html',
        'direct' : False,
        'embed' : False,
        'encoding' : 'utf8',
        'extensions' : '',
        'maxtoclevel' : 2,
        'no_rcfile': False,
        'presenter_notes' : True,
        'relative' : False,
        'theme' : 'default',
        'verbose': False,
        'watch' : False,
        'user_css' : [],
        'user_js' : [],
    }

    ALIASES = {
        'css': 'user_css',
        'js': 'user_js',
        'destination': 'destination_file',
        'max-toc-level': 'maxtoclevel',
        'presenter-notes': 'presenter_notes',
        'copy-theme': 'copy_theme',
        'no-rcfile': 'no_rcfile',
    }

    def __init__(self, *args, base_dir=None, **kwargs):
        super().__init__(*args, **kwargs)

        for key in self.data:
            if key not in self.allopts():
                raise ValueError("Unknown config parameter '%s'" % key)

        self.base_dir = base_dir or os.path.normpath('.')

        # set default values
        for key, val in self.DEFAULT_VALUES.items():
            # make sure not to go through __setitem__ here
            self.data.setdefault(key, val)


    def __getitem__(self, key):
        return super().__getitem__(self.alias(key))


    def __setitem__(self, key, value):
        key = self.alias(key)

        if key not in self.DEFAULT_VALUES:
            raise ValueError("Unknown config parameter '%s'" % (key))
        if key == 'linenos':
            super().__setitem__(key, (value if value in self.VALID_LINENOS
                                      else 'inline'))
        else:
            super().__setitem__(key, value)


    def update(self, other):
        """TODO"""
        super().update(other)
        self.base_dir = other.base_dir or self.base_dir


    @classmethod
    def alias(cls, key):
        """TODO"""
        return cls.ALIASES.get(key, key)


    @classmethod
    def allopts(cls):
        """TODO"""
        allkeys = itertools.chain(cls.ALIASES, cls.DEFAULT_VALUES)
        return ((key, type(cls.DEFAULT_VALUES[cls.alias(key)]))
                for key in allkeys)


    @classmethod
    def from_configfile(cls, configfile):
        """TODO"""
        assert os.path.isfile(configfile)

        raw_config = configparser.RawConfigParser()
        try:
            raw_config.read(configfile)
        except configparser.Error as exc:
            raise RuntimeError(u"Invalid configuration file: %s" % exc)

        section_name = ('landslide' if raw_config.has_section('landslide') else
                        'darkslide')

        typed_getter_funcs = {
            int: raw_config.getint,
            bool: raw_config.getboolean,
            str: raw_config.get,
            list: lambda section, key: raw_config.get(section, key).split('\n'),
        }

        config = {}
        for key, key_type in cls.allopts():
            assert key_type in typed_getter_funcs
            getter_func = typed_getter_funcs[key_type]
            try:
                value = getter_func(section_name, key)
            except configparser.Error as exc:
                raise ValueError("Invalid value for key %s in config file: %s"
                                 % (key, exc))
            if value is not None:
                config[cls.alias(key)] = value

        return cls(config, base_dir=os.path.dirname(configfile))
