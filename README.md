# HashIDTools
[![Build Status](https://travis-ci.org/joeblackwaslike/hashidtools.svg?branch=master)](https://travis-ci.org/joeblackwaslike/hashidtools) [![Github Repo](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/joeblackwaslike/hashidtools) [![Pypi Version](https://img.shields.io/pypi/v/hashidtools.svg)](https://pypi.python.org/pypi/hashidtools) [![Pypi License](https://img.shields.io/pypi/l/hashidtools.svg)](https://pypi.python.org/pypi/hashidtools) [![Pypi Wheel](https://img.shields.io/pypi/wheel/hashidtools.svg)](https://pypi.python.org/pypi/hashidtools) [![Pypi Versions](https://img.shields.io/pypi/pyversions/hashidtools.svg)](https://pypi.python.org/pypi/hashidtools)


## Maintainer
Joe Black | <me@joeblack.nyc> | [github](https://github.com/joeblackwaslike)


## Introduction
HashID tools/components for async ID generation. Example: `k62K3zOn4Y5Kkxmg7pWOAqPyd8NVjrmX` Designed for async data model ID generation for persisting objects to a graph DB such as ZODB.  ZCA means it's simple to customize and override without editing any code.

#### Comes with
* Customizable Generator/encoder/decoder utility
* Type class (experimental)
* Persistent, 2x BTree-powered IntID/Ref Manager
* Custom fields for `zope.schema` and `attrs`, with default factory functions, validation, etc.

#### Also
* Random seed integer is just under 64bits.
* Derive seed integer at any time by casting type as an int.


## Installation
```shell
pip3 install hashidtools
```

## Usage

### HashIDGenerator
```python
>>> from hashidtools import HashIDGenerator
>>> gen = HashIDGenerator(salt='my random salt', min_length=32)

>>> gen.seed()
...
>>> gen
HashIDGenerator(salt='my random salt', min_length=32)
>>> gen.new()
'...'
>>> gen.decode(gen.new())
...
```


### HashID Type
```python
>>> from hashidtools import HashID
... HashID()
'...'
>>> HashID('8nKqkABjlYB5A7430M917zAJao1Me4mN')
'8nKqkABjlYB5A7430M917zAJao1Me4mN'
```


### Hashid IntID Indexing & Event System
```python
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
```


### Retrieving the utilities through the ZCA Registry
```python
>>> from zope.component import queryUtility
... from hashidtools.interfaces import IHashIDGenerator, IIntIds
...
... queryUtility(IHashIDGenerator)
HashIDGenerator(salt='$2a$12$AAAAAAAAAAAAAACgpDEPGQ', min_length=32)

>>> queryUtility(IIntIds)
HashIDs(attribute='id')
```


### Extending this Package
This package uses Zope Component Architecture for the ultimate in pluggable extendibility.


#### Quick example of customizing the HashID Generator:
```python
# Note: you can also create your own Generator class that implements the
# IHashIDGenerator interface and register it.
from zope.component import provideUtility

from hashidtools import HashIDGenerator
from hashidtools.interfaces import IHashIDGenerator

generator = HashIDGenerator(**custom_options)
provideUtility(generator, IHashIDGenerator)
```

Note: the following would preferrably be done using your project's ZCML directives.


## Changes
* [CHANGELOG](CHANGELOG.md)
