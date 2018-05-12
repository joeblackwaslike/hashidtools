"""
hashidtools.fields
~~~~~~~~~~~~~~~~

Fields helpers for zope.schema and attrs.

:copyright: (c) 2018 by Joseph Black.
:license: MIT, see LICENSE for more details.
"""

import re

from zope.interface import implementer
from zope.schema.interfaces import IFromUnicode
from zope.schema._field import NativeStringLine
from zope.component import queryUtility

import attr
from attr.validators import instance_of
from .interfaces import IHashID, IHashIDGenerator
from .types import HashID as HashIDType
from .exceptions import InvalidHashID

HASHID_REGEX = re.compile(r'^\w{32}$')


@implementer(IHashID, IFromUnicode)
class HashID(NativeStringLine):
    """HashID field for zope.schema.

    Values of HashID fields must be a alphanum string 32chars in length.
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('title', 'HashID')
        kwargs.setdefault(
            'description', 'A short string representing the HashID.')
        kwargs.setdefault('required', True)
        kwargs.setdefault('readonly', True)
        kwargs.setdefault('constraint', HASHID_REGEX.match)
        kwargs.setdefault(
            'defaultFactory',
            lambda: queryUtility(IHashIDGenerator).new())
        super(HashID, self).__init__(*args, **kwargs)

    def _validate(self, value):
        super(HashID, self)._validate(value)
        if HASHID_REGEX.match(value):
            return
        raise InvalidHashID(value)

    def fromUnicode(self, value):
        """See IFromUnicode."""
        v = value.strip()
        if isinstance(v, bytes):
            v = v.decode()
        v = HashIDType(v)
        self.validate(v)
        return v


def hashid(*args, **kwargs):
    """HashID field for attrs."""
    return attr.ib(
        validator=[instance_of(str)],
        factory=queryUtility(IHashIDGenerator),
        **kwargs)
