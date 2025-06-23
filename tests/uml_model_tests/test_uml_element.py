from UML_model.uml_element import UMLElement
import unittest

class TestUMLElement(unittest.TestCase):

    def test_uml_element_abstract(self):
        class TestClass(UMLElement):
            def __init__(self, name: str):
                super().__init__(name)
            def to_plantuml(self) -> str:
                return "Test PlantUML"
               
        test_element = TestClass("TestElement")
        self.assertEqual(test_element.name, "TestElement")
        self.assertEqual(str(test_element), "TestClass(TestElement)")
        self.assertEqual(test_element.to_plantuml(), "Test PlantUML")

    def test_uml_element_missing_abstract_method(self):
        class IncompleteClass(UMLElement):
            def __init__(self, name: str):
                super().__init__(name)

        with self.assertRaises(TypeError) as context:
            IncompleteClass("TestElement")
