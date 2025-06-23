from UML_model.uml_enum import UMLEnum, UMLValue
from UML_model.uml_element import UMLElement
from UML_model.uml_relation import UMLRelation, UMLRelationType
import unittest

class TestUMLValue(unittest.TestCase):
    def test_uml_value_init(self):
        value = UMLValue("WHITE")
        self.assertEqual(value.name, "WHITE")

    def test__uml_value_repr(self):
        value = UMLValue("WHITE")
        self.assertEqual(repr(value), "UMLValue(WHITE)")

    def test_uml_value_eq_equals(self):
        value1 = UMLValue("WHITE")
        value2 = UMLValue("WHITE")
        self.assertEqual(value1, value2)

    def test_uml_value_eq_not_equals(self):
        value1 = UMLValue("WHITE")
        value2 = UMLValue("BLACK")
        self.assertNotEqual(value1, value2)

    def test_uml_value_eq_different_class(self):
        value = UMLValue("WHITE")
        self.assertNotEqual(value, "WHITE")

    def test_uml_value_hash(self):
        value1 = UMLValue("WHITE")
        value2 = UMLValue("WHITE")
        self.assertEqual(hash(value1), hash(value2))

class TestUMLEnum(unittest.TestCase):
    def setUp(self):
        self.enum = UMLEnum("Color", [UMLValue("WHITE"), UMLValue("BLACK")])

    def test_uml_enum_init_full(self):
        enum = UMLEnum("Color", [UMLValue("WHITE"), UMLValue("BLACK")])
        self.assertEqual(enum.name, "Color")
        self.assertEqual(enum.values, [UMLValue("WHITE"), UMLValue("BLACK")])
        self.assertEqual(enum.relations, [])
        self.assertIsInstance(enum, UMLElement)

    def test_uml_enum_init_empty(self):
        enum = UMLEnum("Color")
        self.assertEqual(enum.name, "Color")
        self.assertEqual(enum.values, [])
        self.assertEqual(enum.relations, [])
        self.assertIsInstance(enum, UMLElement)

    def test_uml_enum_repr(self):
        self.assertEqual(repr(self.enum), "UMLEnum(Color): values [WHITE, BLACK]")

    def test_uml_enum_str(self):
        self.assertEqual(str(self.enum), "UMLEnum(Color)")
        
    def test_uml_enum_to_plantuml(self):
        expected = "enum Color {\n\tWHITE\n\tBLACK\n}"
        self.assertEqual(self.enum.to_plantuml(), expected)

    def test_uml_enum_eq_equals(self):
        enum1 = UMLEnum("Color", [UMLValue("WHITE"), UMLValue("BLACK")])
        enum2 = UMLEnum("Color", [UMLValue("WHITE"), UMLValue("BLACK")])
        self.assertEqual(enum1, enum2)

    def test_uml_enum_eq_not_equals(self):
        enum1 = UMLEnum("Color", [UMLValue("WHITE"), UMLValue("BLACK")])
        enum2 = UMLEnum("Color", [UMLValue("WHITE"), UMLValue("RED")])
        self.assertNotEqual(enum1, enum2)

    def test_uml_enum_eq_different_class(self):
        enum = UMLEnum("Color", [UMLValue("WHITE"), UMLValue("BLACK")])
        self.assertNotEqual(enum, "Color")

    def test_uml_enum_hash(self):
        enum1 = UMLEnum("Color", [UMLValue("WHITE"), UMLValue("BLACK")])
        enum2 = UMLEnum("Color", [UMLValue("WHITE"), UMLValue("BLACK")])
        self.assertEqual(hash(enum1), hash(enum2))

    def test_uml_enum_add_relation(self):
        relation = UMLRelation(source=self.enum, destination=UMLEnum("Shape"), type=UMLRelationType.ASSOCIATION)
        self.enum.add_relation(relation)
        self.assertIn(relation, self.enum.relations)