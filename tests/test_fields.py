import unittest

import attr
from zope.interface import Interface, implementer
import zope.schema

import hashidtools
from hashidtools.interfaces import IHashIDGenerator, IHashID
from hashidtools import HashIDGenerator, HashID
from hashidtools import fields


class IFoo(Interface):
    id = fields.HashID()

@implementer(IFoo)
@attr.s(auto_attribs=True)
class Foo:
    id: HashID = None


@implementer(IFoo)
@attr.s(auto_attribs=True)
class Foo2:
    id: HashID = fields.hashid()


class TestHashID(unittest.TestCase):
    def makeFoo(self, *args, **kwargs):
        return Foo(*args, **kwargs)

    def makeFoo2(self, *args, **kwargs):
        return Foo2(*args, **kwargs)

    # def test_schema_field(self):
    #     foo = self.makeFoo()
    #
    #     for name, field in zope.schema.getFields(IFoo).items():
    #         bound = field.bind(foo)
    #         bound.set(foo, name)
    #
    #         bound.validate(bound.get(foo))
    #
    #         errors = zope.schema.getValidationErrors(IFoo, foo)
    #         self.assertEqual(errors, [])

    # def test_attrs_field(self):
    #     foo = self.makeFoo2()
    #
    #     for name, field in zope.schema.getFields(IFoo).items():
    #         bound = field.bind(foo)
    #         bound.set(foo, name)
    #
    #         bound.validate(bound.get(foo))
    #
    #         errors = zope.schema.getValidationErrors(IFoo, foo)
    #         self.assertEqual(errors, [])
