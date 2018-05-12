# pylint: disable=inherit-non-class,no-self-argument,no-method-argument
# pylint: disable=unexpected-special-method-signature,arguments-differ

"""
hashidtools.interfaces
~~~~~~~~~~~~~~~~

Zope compatible interfaces and schemata for this package.

:copyright: (c) 2018 by Joseph Black.
:license: MIT, see LICENSE for more details.
"""

import re

from zope.interface import Interface
import zope.schema
from zope.component import queryUtility


class IHashIDAware(Interface):
    """Marker for interfaces that support HashIDs."""


class IHashIDGenerator(Interface):
    """Generator of HashID encoded ID's."""

    salt = zope.schema.TextLine(
        title='salt', description="a short string to use as crypto salt",
        readonly=True, required=True, default='$2a$12$AAAAAAAAAAAAAACgpDEPGQ'
    )
    min_length = zope.schema.Int(
        title='minimum id length',
        description="The minimum length for the generated hashid",
        readonly=True, required=True, default=32, min=32, max=128
    )
    alphabet = zope.schema.TextLine(
        title='Hashid alphabet',
        description="A custom alphabet to use when generating hashids",
        readonly=True,
        default=('abcdefghijklmnopqrstuvwxyz'
                 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890')
    )

    def __call__():
        """Shortcut to new()"""

    def seed():
        """Return a randomly generated ~64bit int seed."""

    def new():
        """Return a new hashid value."""

    def decode(hashid):
        """Decode a hashid value to it's base integer."""


class IHashID(IHashIDAware):
    """HashID type of 64bit integer, used for ZODB object ID generation."""

    id = zope.schema.TextLine(
        title='HashID', description="A HashIDs based ID.",
        readonly=True, required=True, constraint=re.compile(r'^\w{32}$').match,
        defaultFactory=queryUtility(IHashIDGenerator))

    def __int__():
        """Return integer representation of the HashID value."""
