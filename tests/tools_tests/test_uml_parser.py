from tools.UML_parser import UMLParser
from UML_model.uml_class import UMLClass, UMLAttribute, UMLOperation, UMLVisibility, UMLDataType
from UML_model.uml_enum import UMLEnum, UMLValue
import unittest

class TestUMLParser(unittest.TestCase):
    # attribute tests
    def test_parse_attributes_invalid(self):
        uml_line_1 = ""
        uml_line_2 = "   "
        uml_line_3 = "na me: Str"
        uml_line_4 = " : String"
        self.assertIsNone(UMLParser.parse_attribute(uml_line_1))
        self.assertIsNone(UMLParser.parse_attribute(uml_line_2))
        self.assertIsNone(UMLParser.parse_attribute(uml_line_3))
        self.assertEqual(UMLParser.parse_attribute(uml_line_4), UMLAttribute(name="--error--", data_type=UMLDataType.STR))

    def test_parse_attributes_valid_basic(self):
        uml_line = "name"
        expected = UMLAttribute(name="name")
        result = UMLParser.parse_attribute(uml_line)
        self.assertEqual(result, expected)

    def test_parse_attributes_valid_with_type(self):
        uml_line_1 = "name: String"
        expected_1 = UMLAttribute(name="name", data_type=UMLDataType.STR)
        uml_line_2 = "name: int"
        expected_2 = UMLAttribute(name="name", data_type=UMLDataType.INT)
        uml_line_3 = "name: float"
        expected_3 = UMLAttribute(name="name", data_type=UMLDataType.FLOAT)
        uml_line_4 = "name: bool"
        expected_4 = UMLAttribute(name="name", data_type=UMLDataType.BOOL)
        uml_line_5 = "name: test"
        expected_5 = UMLAttribute(name="name", data_type=UMLDataType.UNKNOWN)
        result = UMLParser.parse_attribute(uml_line_1)
        self.assertEqual(result, expected_1)
        result = UMLParser.parse_attribute(uml_line_2)
        self.assertEqual(result, expected_2)
        result = UMLParser.parse_attribute(uml_line_3)
        self.assertEqual(result, expected_3)
        result = UMLParser.parse_attribute(uml_line_4)
        self.assertEqual(result, expected_4)
        result = UMLParser.parse_attribute(uml_line_5)
        self.assertEqual(result, expected_5)

    def test_parse_attributes_valid_with_initial(self):
        uml_line = "name: String = 'value'"
        expected = UMLAttribute(name="name", data_type=UMLDataType.STR, initial="'value'")
        result = UMLParser.parse_attribute(uml_line)
        self.assertEqual(result, expected)

    def test_parse_attributes_valid_with_visibility(self):
        uml_line_1 = "+name"
        expected_1 = UMLAttribute(name="name", visibility=UMLVisibility.PUBLIC)
        uml_line_2 = "-name"
        expected_2 = UMLAttribute(name="name", visibility=UMLVisibility.PRIVATE)
        uml_line_3 = "# name"
        expected_3 = UMLAttribute(name="name", visibility=UMLVisibility.PROTECTED)
        uml_line_4 = "~ name"
        expected_4 = UMLAttribute(name="name", visibility=UMLVisibility.PACKAGE)

        result = UMLParser.parse_attribute(uml_line_1)
        self.assertEqual(result, expected_1)
        result = UMLParser.parse_attribute(uml_line_2)
        self.assertEqual(result, expected_2)
        result = UMLParser.parse_attribute(uml_line_3)
        self.assertEqual(result, expected_3)
        result = UMLParser.parse_attribute(uml_line_4)
        self.assertEqual(result, expected_4)

    def test_parse_attributes_valid_with_derived(self):
        uml_line = "/name"
        expected = UMLAttribute(name="name", derived=True)
        result = UMLParser.parse_attribute(uml_line)
        self.assertEqual(result, expected)

    def test_parse_attributes_valid_with_all(self):
        uml_line = "-/name: String = 'value'"
        expected = UMLAttribute(name="name", data_type=UMLDataType.STR, initial="'value'", visibility=UMLVisibility.PRIVATE, derived=True)
        result = UMLParser.parse_attribute(uml_line)
        self.assertEqual(result, expected)
    
    # operation tests
    def test_parse_operations_invalid(self):
        uml_line_1 = ""
        uml_line_2 = "   "
        uml_line_3 = "na me()"

        self.assertRaises(ValueError, UMLParser.parse_operation, uml_line_1)
        self.assertRaises(ValueError, UMLParser.parse_operation, uml_line_2)
        self.assertRaises(ValueError, UMLParser.parse_operation, uml_line_3)

    def test_parse_operations_valid_basic(self):
        uml_line = "name()"
        expected = UMLOperation(name="name")
        result = UMLParser.parse_operation(uml_line)
        self.assertEqual(result, expected)

    def test_parse_operations_valid_with_params(self):
        uml_line_1 = "name(param1: String, param2: int, param3: float, param4: bool)"
        expected_1 = UMLOperation(name="name", params={"param1": UMLDataType.STR, "param2": UMLDataType.INT, "param3": UMLDataType.FLOAT, "param4": UMLDataType.BOOL})
        uml_line_2 = "name(param1, param2)"
        expected_2 = UMLOperation(name="name", params={"param1": UMLDataType.UNKNOWN, "param2": UMLDataType.UNKNOWN})
        uml_line_3 = "name(param1: test1, param2: test2)"
        expected_3 = UMLOperation(name="name", params={"param1": UMLDataType.UNKNOWN, "param2": UMLDataType.UNKNOWN})
        uml_line_4 = "name(param1: String, param2, param3: test3)"
        expected_4 = UMLOperation(name="name", params={"param1": UMLDataType.STR, "param2": UMLDataType.UNKNOWN, "param3": UMLDataType.UNKNOWN})

        result = UMLParser.parse_operation(uml_line_1)
        self.assertEqual(result, expected_1)
        result = UMLParser.parse_operation(uml_line_2)
        self.assertEqual(result, expected_2)
        result = UMLParser.parse_operation(uml_line_3)
        self.assertEqual(result, expected_3)
        result = UMLParser.parse_operation(uml_line_4)
        self.assertEqual(result, expected_4)

    def test_parse_operations_valid_with_visibility(self):
        uml_line_1 = "+name()"
        expected_1 = UMLOperation(name="name", visibility=UMLVisibility.PUBLIC)
        uml_line_2 = "-name()"
        expected_2 = UMLOperation(name="name", visibility=UMLVisibility.PRIVATE)
        uml_line_3 = "# name()"
        expected_3 = UMLOperation(name="name", visibility=UMLVisibility.PROTECTED)
        uml_line_4 = "~ name()"
        expected_4 = UMLOperation(name="name", visibility=UMLVisibility.PACKAGE)

        result = UMLParser.parse_operation(uml_line_1)
        self.assertEqual(result, expected_1)
        result = UMLParser.parse_operation(uml_line_2)
        self.assertEqual(result, expected_2)
        result = UMLParser.parse_operation(uml_line_3)
        self.assertEqual(result, expected_3)
        result = UMLParser.parse_operation(uml_line_4)
        self.assertEqual(result, expected_4)

    def test_parse_operations_valid_with_return_type(self):
        uml_line_1 = "name() : String"
        expected_1 = UMLOperation(name="name", return_types=[UMLDataType.STR])
        uml_line_2 = "name() : int"
        expected_2 = UMLOperation(name="name", return_types=[UMLDataType.INT])
        uml_line_3 = "name() : float"
        expected_3 = UMLOperation(name="name", return_types=[UMLDataType.FLOAT])
        uml_line_4 = "name() : bool"
        expected_4 = UMLOperation(name="name", return_types=[UMLDataType.BOOL])
        uml_line_5 = "name() : test"
        expected_5 = UMLOperation(name="name", return_types=[UMLDataType.UNKNOWN])
        uml_line_6 = "name() : void"
        expected_6 = UMLOperation(name="name", return_types=[UMLDataType.VOID])
        uml_line_7 = "name() : String, Integer"
        expected_7 = UMLOperation(name="name", return_types=[UMLDataType.STR, UMLDataType.INT])

        result = UMLParser.parse_operation(uml_line_1)
        self.assertEqual(result, expected_1)
        result = UMLParser.parse_operation(uml_line_2)
        self.assertEqual(result, expected_2)
        result = UMLParser.parse_operation(uml_line_3)
        self.assertEqual(result, expected_3)
        result = UMLParser.parse_operation(uml_line_4)
        self.assertEqual(result, expected_4)
        result = UMLParser.parse_operation(uml_line_5)
        self.assertEqual(result, expected_5)
        result = UMLParser.parse_operation(uml_line_6)
        self.assertEqual(result, expected_6)
        result = UMLParser.parse_operation(uml_line_7)
        self.assertEqual(result, expected_7)

    def test_parse_operations_valid_with_all(self):
        uml_line = "-name(param1: String, param2) : float"
        expected = UMLOperation(name="name", params={"param1": UMLDataType.STR, "param2": UMLDataType.UNKNOWN}, return_types=[UMLDataType.FLOAT], visibility=UMLVisibility.PRIVATE)
        result = UMLParser.parse_operation(uml_line)
        self.assertEqual(result, expected)

    # class tests
    def test_parse_classes_empty(self):
        uml_text = "@startuml\n@enduml"
        expected = []
        result = UMLParser.parse_plantuml_classes(uml_text)
        self.assertEqual(result, expected)

    def test_parse_classes_single_empty(self):
        uml_text_1 = """
        @startuml
        class TestClass 
        @enduml
        """
        uml_text_2 = """
        @startuml
        class TestClass as "T"
        @enduml
        """
        uml_text_3 = """
        @startuml
        class TestClass {}
        @enduml
        """
        uml_text_4 = """
        @startuml
        class TestClass As "T" {}
        @enduml
        """
        uml_text_5 = """
        @startuml
        class TestClass {

        }
        @enduml
        """
        uml_text_6 = """
        @startuml
        class TestClass AS "T" {

        }
        @enduml
        """

        expected = [UMLClass(name="TestClass", attributes=[], operations=[])]

        result = UMLParser.parse_plantuml_classes(uml_text_1)
        self.assertEqual(result, expected)
        result = UMLParser.parse_plantuml_classes(uml_text_2)
        self.assertEqual(result, expected)
        result = UMLParser.parse_plantuml_classes(uml_text_3)
        self.assertEqual(result, expected)
        result = UMLParser.parse_plantuml_classes(uml_text_4)
        self.assertEqual(result, expected)
        result = UMLParser.parse_plantuml_classes(uml_text_5)
        self.assertEqual(result, expected)
        result = UMLParser.parse_plantuml_classes(uml_text_6)
        self.assertEqual(result, expected)

    def test_parse_classes_single_not_empty(self):
        uml_text_1 = """
        @startuml
        class TestClass {
            +/attribute: String = "default"
            - method(p1: String, p2): int
        }
        @enduml
        """
        uml_text_2 = """
        @startuml
        class TestClass as "T" {
            +/attribute: String = "default"
            - method(p1: String, p2): int
        }
        @enduml
        """
        uml_text_3 = """
        @startuml
        class TestClass As "T" {
            +/attribute: String = "default"
            - method(p1: String, p2): int
        }
        @enduml
        """
        uml_text_4 = """
        @startuml
        class TestClass AS "T" {
            +/attribute: String = "default"
            - method(p1: String, p2): int
        }
        @enduml
        """

        expected = [
            UMLClass(name="TestClass", attributes=[UMLAttribute(name="attribute", data_type=UMLDataType.STR, visibility=UMLVisibility.PUBLIC, initial="\"default\"", derived=True)], operations=[UMLOperation(name="method", return_types=[UMLDataType.INT], visibility=UMLVisibility.PRIVATE, params={"p1": UMLDataType.STR, "p2": UMLDataType.UNKNOWN})])
        ]
        

        result = UMLParser.parse_plantuml_classes(uml_text_1)
        self.assertEqual(result, expected)
        result = UMLParser.parse_plantuml_classes(uml_text_2)
        self.assertEqual(result, expected)
        result = UMLParser.parse_plantuml_classes(uml_text_3)
        self.assertEqual(result, expected)
        result = UMLParser.parse_plantuml_classes(uml_text_4)
        self.assertEqual(result, expected)

    def test_parse_classes_multiple(self):
        uml_text = """
        @startuml
        class TestClass1 {
            +attribute1: String
            - method1(): int
        }
        
        class TestClass2 {
            +attribute2: int
            -method2(p1: String)
        }
        
        class TestClass3
        @enduml
        """

        expected = [
            UMLClass(name="TestClass1", attributes=[UMLAttribute(name="attribute1", data_type=UMLDataType.STR, visibility=UMLVisibility.PUBLIC)], operations=[UMLOperation(name="method1", return_types=[UMLDataType.INT], visibility=UMLVisibility.PRIVATE)]),
            UMLClass(name="TestClass2", attributes=[UMLAttribute(name="attribute2", data_type=UMLDataType.INT, visibility=UMLVisibility.PUBLIC)], operations=[UMLOperation(name="method2", return_types=[UMLDataType.VOID], visibility=UMLVisibility.PRIVATE, params={"p1": UMLDataType.STR})]),
            UMLClass(name="TestClass3")
        ]

        result = UMLParser.parse_plantuml_classes(uml_text)
        self.assertEqual(result, expected)

    # enum tests
    def test_parse_enums_empty(self):
        uml_text = "@startuml\n@enduml"
        expected = []
        result = UMLParser.parse_plantuml_enums(uml_text)
        self.assertEqual(result, expected)

    def test_parse_enums_single_empty(self):
        uml_text_1 = """
        @startuml
        enum TestEnum 
        @enduml
        """
        uml_text_2 = """
        @startuml
        enum TestEnum as "T"
        @enduml
        """
        uml_text_3 = """
        @startuml
        enum TestEnum {}
        @enduml
        """
        uml_text_4 = """
        @startuml
        enum TestEnum As "T" {}
        @enduml
        """
        uml_text_5 = """
        @startuml
        enum TestEnum {

        }
        @enduml
        """
        uml_text_6 = """
        @startuml
        enum TestEnum AS "T" {

        }
        @enduml
        """

        expected = [UMLEnum(name="TestEnum", values=[])]

        result = UMLParser.parse_plantuml_enums(uml_text_1)
        self.assertEqual(result, expected)
        result = UMLParser.parse_plantuml_enums(uml_text_2)
        self.assertEqual(result, expected)
        result = UMLParser.parse_plantuml_enums(uml_text_3)
        self.assertEqual(result, expected)
        result = UMLParser.parse_plantuml_enums(uml_text_4)
        self.assertEqual(result, expected)
        result = UMLParser.parse_plantuml_enums(uml_text_5)
        self.assertEqual(result, expected)
        result = UMLParser.parse_plantuml_enums(uml_text_6)
        self.assertEqual(result, expected)

    def test_parse_enums_single_not_empty(self):
        uml_text_1 = """
        @startuml
        enum TestEnum {
            VALUE1
            VALUE2
        }
        @enduml
        """
        uml_text_2 = """
        @startuml
        enum TestEnum as "T" {
            VALUE1
            VALUE2
        }
        @enduml
        """
        uml_text_3 = """
        @startuml
        enum TestEnum As "T" {
            VALUE1
            VALUE2
        }
        @enduml
        """
        uml_text_4 = """
        @startuml
        enum TestEnum AS "T" {
            VALUE1
            VALUE2
        }
        @enduml
        """

        expected = [UMLEnum(name="TestEnum", values=[UMLValue(name="VALUE1"), UMLValue(name="VALUE2")])]

        result = UMLParser.parse_plantuml_enums(uml_text_1)
        self.assertEqual(result, expected)
        result = UMLParser.parse_plantuml_enums(uml_text_2)
        self.assertEqual(result, expected)
        result = UMLParser.parse_plantuml_enums(uml_text_3)
        self.assertEqual(result, expected)
        result = UMLParser.parse_plantuml_enums(uml_text_4)
        self.assertEqual(result, expected)

    def test_parse_enums_multiple(self):
        uml_text = """
        @startuml
        enum TestEnum1 {
            VALUE1
            VALUE2
        }
        
        enum TestEnum2 {
            VALUE3
            VALUE4
        }
        
        enum TestEnum3
        @enduml
        """

        expected = [
            UMLEnum(name="TestEnum1", values=[UMLValue(name="VALUE1"), UMLValue(name="VALUE2")]),
            UMLEnum(name="TestEnum2", values=[UMLValue(name="VALUE3"), UMLValue(name="VALUE4")]),
            UMLEnum(name="TestEnum3")
        ]

        result = UMLParser.parse_plantuml_enums(uml_text)
        self.assertEqual(result, expected)

    # TODO: relation tests