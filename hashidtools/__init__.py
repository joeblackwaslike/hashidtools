"""
hashidtools
~~~~~~~~~

HashID tools/components for async ID generation.

Designed for async data model ID generation for persisting objects to a graph
DB such as ZODB.  ZCA means it's simple to customize without editing any code.

Example: `k62K3zOn4Y5Kkxmg7pWOAqPyd8NVjrmX`

Usage::

    >>> from zc.intid.interfaces import IIntIds
    ... from zope.component import queryUtility
    ... from hashidtools.interfaces import IHashIDGenerator, IHashID, IHashID
    ...
    ... queryUtility(IHashIDGenerator)
    HashIDGenerator(salt='$2a$12$AAAAAAAAAAAAAACgpDEPGQ', min_length=32)

    >>> queryUtility(IHashIDGenerator)()
    '...'

    >>> queryUtility(IIntIds)
    HashIDManager(attribute='id')

    >>> intid = queryUtility(IIntIds)
    ... intid
    HashIDManager(attribute='id')

    >>> from zc.intid.interfaces import AddedEvent, RemovedEvent
    ... import zope.event.classhandler
    ...
    ... @zope.event.classhandler.handler(AddedEvent)
    ... def handler(event):
    ...     print(event.id, event.obj, event.idmanager)
    ...
    ... @zope.event.classhandler.handler(RemovedEvent)
    ... def handler(event):
    ...     print(event.id, event.obj, event.idmanager)

    >>> import attr
    ... Test = attr.make_class(
    ...   'Test', {'id': fields.hashid(init=False),
    ...            'name': attr.ib(default='default-name')})

    >>> t = Test()
    ... intid.register(t)
    '...'

    ... id = intid.getId(t)
    ... intid.getObject(id)
    Test(id='...', name='default-name')

    >>> intid.unregister(t)

:copyright: (c) 2018 by Joseph Black.
:license: MIT, see LICENSE for more details.
"""


__version__ = '1.0.2'
__title__ = "hashidtools"

from zope.configuration import xmlconfig

from . import interfaces, exceptions, types, fields
from .types import HashIDGenerator, HashID, HashIDManager


xmlconfig.file('configure.zcml', __import__('sys').modules[__name__])
