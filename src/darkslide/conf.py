"""TODO"""

import collections
import itertools
import os

from six.moves import configparser

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for key in self.data:
            if not self.is_key_valid(key):
                raise ValueError("Unknown config parameter '%s'" % key)

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


    @classmethod
    def alias(cls, key):
        """TODO"""
        return cls.ALIASES.get(key, key)

    @classmethod
    def is_key_valid(cls, key):
        """TODO"""
        return key in cls.ALIASES or key in cls.DEFAULT_VALUES

    @classmethod
    def allopts(cls):
        """TODO"""
        return itertools.chain(cls.ALIASES, cls.DEFAULT_VALUES)


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
        base_dir = os.path.dirname(configfile)
        for key in cls.allopts():
            key_type = type(cls.DEFAULT_VALUES[cls.alias(key)])
            assert key_type in typed_getter_funcs
            getter_func = typed_getter_funcs[key_type]
            try:
                value = getter_func(section_name, key)
            except configparser.NoOptionError:
                continue
            except configparser.Error as exc:
                raise ValueError("Invalid value for key %s in config file: %s"
                                 % (key, exc))

            # resolve relative paths
            if key in ('source', 'user_css', 'user_js'):
                value = [
                    val if os.path.isabs(val) else os.path.join(base_dir, val)
                    for val in value
                ]

            config[cls.alias(key)] = value

        return cls(config)
