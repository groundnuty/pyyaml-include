# -*- coding: utf-8 -*-

"""
Include YAML files within YAML
"""

import io
import os
import re
from glob import iglob
from sys import version_info

import yaml

__all__ = ['YamlIncludeConstructor']

PYTHON_MAYOR_MINOR = '{0[0]}.{0[1]}'.format(version_info)

WILDCARDS_REGEX = re.compile(r'^.*(\*|\?|\[!?.+\]).*$')


class YamlIncludeConstructor:
    """The `include constructor` for PyYAML's loader

    Call :meth:`add_to_loader_class` to add it into loader.

    In YAML files, use ``!include`` to load other YAML files as below::

        !include [dir/**/*.yml, true]

    or::

        !include {pathname: dir/abc.yml, encoding: utf-16}

    """

    TAG = '!include'

    def __call__(self, loader, node):
        args = []
        kwargs = {}
        if isinstance(node, yaml.nodes.ScalarNode):
            args = [loader.construct_scalar(node)]
        elif isinstance(node, yaml.nodes.SequenceNode):
            args = loader.construct_sequence(node)
        elif isinstance(node, yaml.nodes.MappingNode):
            kwargs = loader.construct_mapping(node)
        return self.load(loader, *args, **kwargs)

    @classmethod
    def load(cls, loader, pathname, recursive=False, encoding=None):
        """Once add the constructor to PyYAML loader class,
        Loader will use this function to include other YAML fils
        on parsing ``"!include"`` tag

        :param loader: Instance of PyYAML's loader class
        :param str pathname: pathname can be either absolute (like /usr/src/Python-1.5/Makefile) or relative (like ../../Tools/*/*.gif), and can contain shell-style wildcards

        :param bool recursive: If recursive is true, the pattern ``"**"`` will match any files and zero or more directories and subdirectories. If the pattern is followed by an os.sep, only directories and subdirectories match.

            Note:
             Using the ``"**"`` pattern in large directory trees may consume an inordinate amount of time.

        :param str encoding: YAML file encoding

            :default: ``None``: ``"utf-8``

        :return: included YAML file, in Python data type

        .. tip:: You can a different tag by setting ``tag`` parameter in :meth:`add_to_loader_class`
        """
        if not encoding:
            encoding = 'utf-8'
        if WILDCARDS_REGEX.match(pathname):
            result = []
            if PYTHON_MAYOR_MINOR >= '3.5':
                iterator = iglob(pathname, recursive=recursive)
            else:
                iterator = iglob(pathname)
            for path in iterator:
                if os.path.isfile(path):
                    with io.open(path, encoding=encoding) as f:
                        result.append(yaml.load(f, type(loader)))
            return result
        else:
            with io.open(pathname, encoding=encoding) as f:
                return yaml.load(f, type(loader))

    @classmethod
    def add_to_loader_class(cls, loader_cls=None, tag=''):
        """
        Create an instance of the constructor, and add it to the YAML `Loader` class

        :param loader_cls:
          The `Loader` class add constructor to.

          :default: ``None``: Add to PyYAML's default `Loader`

        :type loader_cls: type(yaml.SafeLoader) | type(yaml.Loader) | type(yaml.CSafeLoader) | type(yaml.CLoader)

        :param str tag:
          tag name for the include constructor.

          :default: ``""``: use :attr:`TAG` as tag name.

        :return: New created object
        :rtype: YamlIncludeConstructor
        """
        if tag is None:
            tag = ''
        tag = tag.strip()
        if not tag:
            tag = cls.TAG
        instance = cls()
        if loader_cls is None:
            yaml.add_constructor(tag, instance)
        else:
            yaml.add_constructor(tag, instance, loader_cls)
        return instance
