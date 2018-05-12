"""
hashidtools.hashid
~~~~~~~~~~~~~~~~

Miscellaneous HashID Tools

:copyright: (c) 2018 by Joseph Black.
:license: MIT, see LICENSE for more details.
"""

import random
from typing import ClassVar, Union
from weakref import WeakKeyDictionary

import hashids
from zope.interface import implementer
from zope.component import queryUtility
from zope.event import notify
from zope.intid.interfaces import IntIdMissingError
from zope.security.proxy import removeSecurityProxy as unwrap
from zc.intid.interfaces import (
    IIntIds, IntIdInUseError, AddedEvent, RemovedEvent)
from zc.intid.utility import IntIds
import BTrees
import attr
from attr.validators import instance_of

from .interfaces import IHashIDGenerator, IHashID
from .exceptions import InvalidHashID, IDRegisterError


@implementer(IHashIDGenerator)
@attr.s(frozen=True)
class HashIDGenerator:
    """Generator of HashID encoded ID's.

    :param salt str: A short string to use as the unique salt.
    :param min_length int: (32) The minimum length of of the generated HashID.
    :return: a HashIDGenerator object.
    :rtype: :inst:`HashIDGenerator`

    Usage::

        >>> from hashidtools import HashIDGenerator
        >>> HashIDGenerator(salt='my random salt', min_length=32)

        >>> from hashidtools.interfaces import IHashIDGenerator
        ... from zope.component import queryUtility
        ... queryUtility(IHashIDGenerator)
        HashIDGenerator(salt='$2a$12$AAAAAAAAAAAAAACgpDEPGQ', min_length=32)

        >>> queryUtility(IHashIDGenerator)()
        '...'
        >>> queryUtility(IHashIDGenerator).decode('k62K3zOn4Y5Kkxmg7pWOAqPyd8NVjrmX')
        1032596908023458124
    """

    salt: str = attr.ib(
        default='$2a$12$AAAAAAAAAAAAAACgpDEPGQ',
        converter=str,
        validator=instance_of(str))
    min_length: int = attr.ib(
        default=32,
        converter=int,
        validator=instance_of(int))
    alphabet: str = attr.ib(
        default=('abcdefghijklmnopqrstuvwxyz'
                 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                 '1234567890'),
        validator=instance_of(str),
        repr=False
    )

    def __attrs_post_init__(self):
        super(HashIDGenerator, self).__setattr__(
            '_gen', hashids.Hashids(self.salt, self.min_length, self.alphabet))

    def __call__(self):
        return self.new()

    def seed(self):
        """Return a randomly generated ~64bit int seed."""
        return random.getrandbits(64-1)

    def encode(self, value):
        """HashID encode an integer value."""
        return self._gen.encode(value)

    def new(self, seed=None):
        """Return a new hashid value."""
        seed = seed or self.seed()
        return self.encode(seed)

    def decode(self, hashid):
        """Decode a hashid value to it's base integer."""
        return self._gen.decode(hashid)[0]


@implementer(IHashID)
@attr.s(frozen=True, hash=False, repr=False, cmp=False)
class HashID:
    """HashID type of 64bit integer, used for ZODB object ID generation.

    :param id str: A short string representing the HashID.
    :return: A HashID object.
    :rtype: :inst:`HashID`

    Usage::

        >>> from hashidtools import HashID
        >>> HashID()
        '...'
        >>> HashID('8nKqkABjlYB5A7430M917zAJao1Me4mN')
        '8nKqkABjlYB5A7430M917zAJao1Me4mN'

    """

    id = attr.ib(validator=instance_of(str))

    @id.default
    def _default_id(self):
        return queryUtility(IHashIDGenerator)()

    def __hash__(self):
        return hash(str(self.id))

    def __len__(self):
        return len(self.id)

    def __eq__(self, other):
        if isinstance(other, str):
            return str(self.id) == str(other)
        return str(self.id) == str(other.id)

    def __gt__(self, other):
        if isinstance(other, str):
            return str(self.id) > str(other)
        return str(self.id) > str(other.id)

    def __lt__(self, other):
        if isinstance(other, str):
            return str(self.id) < str(other)
        return str(self.id) < str(other.id)

    def __repr__(self):
        return repr(self.id)

    def __str__(self):
        return str(self.id)

    def __int__(self):
        return queryUtility(IHashIDGenerator).decode(self.id)


# https://media.readthedocs.org/pdf/zopecatalog/latest/zopecatalog.pdf
@implementer(IIntIds)
@attr.s
class HashIDManager(IntIds):
    """HashID IntId Manager.

    :param BTrees.family type: A short string representing the HashID.
    :return: A HashIDManager object.
    :rtype: :inst:`HashIDManager`

    Usage::

        >>> intid = HashIDManager()
        ... intid
        HashIDManager(attribute='id')
        ... intid.generateId()
        '...'

        >>> from zc.intid.interfaces import AddedEvent, RemovedEvent
        ... import zope.event.classhandler
        ...
        >>> @zope.event.classhandler.handler(AddedEvent)
        ... def handler(event):
        ...     print(event.id, event.object, event.idmanager)
        ...
        ... @zope.event.classhandler.handler(RemovedEvent)
        ... def handler(event):
        ...     print(event.id, event.object, event.idmanager)

        >>> import attr
        ... Test = attr.make_class(
        ...   'Test', {'id': fields.hashid(init=False),
        ...            'name': attr.ib(default='default-name')})
        ...

        >>> t = Test()
        ... intid.register(t)
        '...'

        ... id = intid.getId(t)
        ... intid.getObject(id)
        Test(id='...', name='default-name')

        >>> intid.unregister(t)

    """

    family: ClassVar[type] = BTrees.family64
    attribute: str = attr.ib(
        default='id',
        validator=instance_of(str))

    def __attrs_post_init__(self):
        self.ids = self.family.OO.BTree()
        self.refs = self.family.OO.BTree()

    def generateId(self, obj=None):
        """Generate ID."""
        return queryUtility(IHashIDGenerator)()

    def getId(self, obj):
        """Return the ID for passed object."""
        unwrapped = unwrap(obj)
        uid = getattr(unwrapped, self.attribute, None)
        if not isinstance(uid, str):
            uid = str(uid)
        if uid is None:
            raise IntIdMissingError(obj)
        return uid

    def register(self, obj):
        """Register objects to ID."""
        obj = unwrap(obj)
        uid = self.queryId(obj)
        if uid is None:
            uid = self.generateId(obj)
            if uid in self.refs:
                raise IntIdInUseError("id generator returned used id")
        if uid != getattr(obj, self.attribute):
            raise IDRegisterError(f'uid: {uid} != obj.id: {obj.id}')
        self.refs[uid] = obj
        notify(AddedEvent(obj, self, uid))
        return uid
