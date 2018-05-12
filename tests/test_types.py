import unittest

import attr
from zope import component
import zope.schema
from zc.intid.interfaces import IIntIds, AddedEvent, RemovedEvent
import zope.event.classhandler

import hashidtools
from hashidtools import fields
from hashidtools.interfaces import IHashIDGenerator, IHashID
from hashidtools.types import HashIDGenerator, HashID, HashIDManager


class TestHashIDGenerator(unittest.TestCase):
    def makeOne(self, salt='sdfs', min_length=32):
        return HashIDGenerator(salt=salt, min_length=min_length)

    def test_interface(self):
        gen = self.makeOne()
        self.assertTrue(IHashIDGenerator.providedBy(gen))

    def test_schema(self):
        gen = self.makeOne()
        errors = zope.schema.getSchemaValidationErrors(IHashIDGenerator, gen)
        self.assertEqual(errors, [])

    def test_hashid_generator_basic(self):
        salt = 'sdfs'
        min_length = 34
        gen = self.makeOne(salt, min_length)
        self.assertEqual(gen.salt, salt)
        self.assertEqual(gen.min_length, min_length)

    def test_hashid_generator_seed(self):
        gen = self.makeOne()
        seed = gen.seed()
        self.assertIsInstance(seed, int)
        bit_length = int(seed).bit_length()
        self.assertGreater(bit_length, 50)
        self.assertLess(bit_length, 64)

    def test_hashid_generator_encode_decode(self):
        gen = self.makeOne()
        seed = 1762352222709391612
        hashid = gen.encode(seed)

        self.assertIsInstance(hashid, str)
        self.assertEqual(hashid, 'bNo4jLpM8mK2PW6l4260YGXnyQlBE1k3')
        self.assertEqual(seed, gen.decode(hashid))

    def test_hashid_generator_new(self):
        gen = self.makeOne()
        hashid = gen.new()
        self.assertEqual(len(hashid), 32)
        self.assertRegex(hashid, r'^\w{32}$')
        self.assertIsInstance(hashid, str)

    def test_immutable_attributes(self):
        from attr.exceptions import FrozenInstanceError

        gen = self.makeOne()
        with self.assertRaises(FrozenInstanceError):
            gen.salt = 'new'

        with self.assertRaises(FrozenInstanceError):
            gen.min_length = 43

        with self.assertRaises(FrozenInstanceError):
            gen.seed_bits = 32



class TestHashID(unittest.TestCase):
    def makeOne(self, id=None):
        if id:
            return HashID(id)
        else:
            return HashID()

    def test_interface(self):
        hashid = self.makeOne()
        self.assertTrue(IHashID.providedBy(hashid))

    def test_schema(self):
        hashid = self.makeOne()
        errors = zope.schema.getSchemaValidationErrors(IHashID, hashid)
        self.assertEqual(errors, [])

    def test_hashid_provided(self):
        id = '5MopkXVL7Ej9dWkaR9kBqNGYway3RAbd'
        hashid = self.makeOne(id)
        self.assertIsInstance(hashid, HashID)
        self.assertEqual(len(hashid), 32)
        self.assertEqual(hashid.id, id)

    def test_hashid_generated(self):
        hashid = self.makeOne()
        self.assertIsInstance(hashid, HashID)
        self.assertEqual(len(hashid), 32)

    def test_hashid_reprs(self):
        hashid = self.makeOne()
        self.assertEqual(repr(hashid), '{!r}'.format(hashid.id))
        self.assertTrue(str(hashid), '{!s}'.format(hashid.id))

    def test_hashid_int_cast(self):
        gen = HashIDGenerator()
        seed = gen.seed()
        hashid = HashID(gen.encode(seed))
        self.assertEqual(int(hashid), seed)

    def test_hashid_dictionary_key(self):
        id1 = self.makeOne()
        id2 = self.makeOne()
        d = {
            id1: 'value',
            id2: 'value2'
        }
        self.assertEqual(d[id1], d[str(id1)])
        self.assertEqual(d[id2], d[str(id2)])

    def test_immutable_attributes(self):
        from attr.exceptions import FrozenInstanceError

        hashid = self.makeOne()
        with self.assertRaises(FrozenInstanceError):
            hashid.id = 'new'


@attr.s
class Fixture:
    id: str = fields.hashid(init=False)
    name: str = attr.ib(default='default-name')


class TestHashIDManager(unittest.TestCase):
    def makeOne(self):
        return HashIDManager()

    def test_interface(self):
        intid = self.makeOne()
        self.assertTrue(IIntIds.providedBy(intid))

    def test_hashid_provided(self):
        inst = Fixture('test')

        intid = self.makeOne()
        hashid = intid.generateId(inst)

        self.assertRegex(hashid, r'^\w{32}$')

        _hid = intid.getId(inst)
        self.assertEqual(_hid, str(inst.id))

        added = []
        @zope.event.classhandler.handler(AddedEvent)
        def added_handler(event):
            added.append(event)
            print(f'id: {event.id} obj:{event.object} intid:{event.idmanager}')

        removed = []
        @zope.event.classhandler.handler(RemovedEvent)
        def removed_handler(event):
            removed.append(event)
            print(f'id: {event.id} obj:{event.object} intid:{event.idmanager}')

        _hid = intid.register(inst)
        self.assertEqual(_hid, str(inst.id))
        self.assertEqual(len(added), 1)

        intid.unregister(inst)
        self.assertEqual(len(removed), 1)
