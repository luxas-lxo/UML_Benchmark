from UML_model.uml_model import UMLModel
from UML_model.uml_class import UMLVisibility, UMLAttribute, UMLDataType, UMLClass, UMLOperation
from UML_model.uml_enum import UMLEnum, UMLValue
from UML_model.uml_relation import UMLRelation, UMLRelationType

import unittest

class TestUMLModel(unittest.TestCase):
    def setUp(self):
        # Initialize test data for UMLClass, UMLEnum, and UMLRelation
        self.att1 = UMLAttribute(name="attribute1", data_type=UMLDataType.STR, visibility=UMLVisibility.PUBLIC)
        self.att2 = UMLAttribute(name="attribute2", data_type=UMLDataType.INT, visibility=UMLVisibility.PRIVATE)
        self.op1 = UMLOperation(name="operation1", return_types=[UMLDataType.VOID], visibility=UMLVisibility.PUBLIC)
        self.op2 = UMLOperation(name="operation2", return_types=[UMLDataType.INT], visibility=UMLVisibility.PRIVATE)
        self.uml_class = UMLClass(name="TestClass", attributes=[self.att1, self.att2], operations=[self.op1, self.op2])

        self.value1 = UMLValue(name="VALUE1")
        self.value2 = UMLValue(name="VALUE2")
        self.uml_enum = UMLEnum(name="TestEnum", values=[self.value1, self.value2])

        self.uml_relation_1 = UMLRelation(source=self.uml_class, destination=self.uml_enum, type=UMLRelationType.ASSOCIATION)
        self.uml_swapped_relation_1 = self.uml_relation_1.swap_source_destination()
        self.uml_relation_2 = UMLRelation(source=self.uml_enum, destination=self.uml_class, type=UMLRelationType.AGGREGATION)

    def test_uml_model_initialization_empty(self):
        uml_model = UMLModel()
        self.assertIsInstance(uml_model, UMLModel)
        self.assertEqual(len(uml_model.class_list), 0)
        self.assertEqual(len(uml_model.enum_list), 0)
        self.assertEqual(len(uml_model.relation_list), 0)

    def test_uml_model_initialization_empty_string(self):
        uml_model = UMLModel("")
        self.assertIsInstance(uml_model, UMLModel)
        self.assertEqual(len(uml_model.class_list), 0)
        self.assertEqual(len(uml_model.enum_list), 0)
        self.assertEqual(len(uml_model.relation_list), 0)

    def test_uml_model_intialization_empty_objects(self):
        uml_model = UMLModel(class_list=[], enum_list=[], relation_list=[])
        self.assertEqual(len(uml_model.class_list), 0)
        self.assertEqual(len(uml_model.enum_list), 0)
        self.assertEqual(len(uml_model.relation_list), 0)

    def test_uml_model_initialization_with_classes(self):
        uml_model = UMLModel(class_list=[self.uml_class])
        self.assertEqual(len(uml_model.class_list), 1)
        self.assertEqual(uml_model.class_list[0].name, "TestClass")
        self.assertEqual(len(uml_model.class_list[0].attributes), 2)
        self.assertIn(self.att1, uml_model.class_list[0].attributes)
        self.assertIn(self.att2, uml_model.class_list[0].attributes)
        self.assertEqual(len(uml_model.class_list[0].operations), 2)
        self.assertIn(self.op1, uml_model.class_list[0].operations)
        self.assertIn(self.op2, uml_model.class_list[0].operations)
        self.assertEqual(len(uml_model.class_list[0].relations), 0)

    def test_uml_model_initialization_with_enums(self):
        uml_model = UMLModel(enum_list=[self.uml_enum])
        self.assertEqual(len(uml_model.enum_list), 1)
        self.assertEqual(uml_model.enum_list[0].name, "TestEnum")
        self.assertEqual(len(uml_model.enum_list[0].values), 2)
        self.assertIn(self.value1, uml_model.enum_list[0].values)
        self.assertIn(self.value2, uml_model.enum_list[0].values)
        self.assertEqual(len(uml_model.enum_list[0].relations), 0)

    def test_uml_model_initialization_with_class_enum_and_relation(self):
        uml_model = UMLModel(class_list=[self.uml_class], enum_list=[self.uml_enum], relation_list=[self.uml_relation_1])
        # Check class initialization
        self.assertEqual(len(uml_model.class_list), 1)
        self.assertEqual(uml_model.class_list[0].name, "TestClass")
        self.assertEqual(len(uml_model.class_list[0].attributes), 2)
        self.assertIn(self.att1, uml_model.class_list[0].attributes)
        self.assertIn(self.att2, uml_model.class_list[0].attributes)
        self.assertEqual(len(uml_model.class_list[0].operations), 2)
        self.assertIn(self.op1, uml_model.class_list[0].operations)
        self.assertIn(self.op2, uml_model.class_list[0].operations)
        self.assertEqual(len(uml_model.class_list[0].relations), 1)
        self.assertIn(self.uml_relation_1, uml_model.class_list[0].relations)

        # Check enum initialization
        self.assertEqual(len(uml_model.enum_list), 1)
        self.assertEqual(uml_model.enum_list[0].name, "TestEnum")
        self.assertEqual(len(uml_model.enum_list[0].values), 2)
        self.assertIn(self.value1, uml_model.enum_list[0].values)
        self.assertIn(self.value2, uml_model.enum_list[0].values)
        self.assertEqual(len(uml_model.enum_list[0].relations), 1)
        self.assertIn(self.uml_swapped_relation_1, uml_model.enum_list[0].relations)

        # Check relation initialization
        self.assertEqual(len(uml_model.relation_list), 1)
        self.assertEqual(uml_model.relation_list[0].source, self.uml_class)
        self.assertEqual(uml_model.relation_list[0].destination, self.uml_enum)
        self.assertEqual(uml_model.relation_list[0].type, UMLRelationType.ASSOCIATION)
        self.assertEqual(uml_model.relation_list[0].s_multiplicity, "1")
        self.assertEqual(uml_model.relation_list[0].d_multiplicity, "1")

    def test_uml_model_repr(self):
        uml_model = UMLModel(class_list=[self.uml_class], enum_list=[self.uml_enum], relation_list=[self.uml_relation_1])
        expected_repr = f"UMLModel(\nClasses = [{self.uml_class.name}], \nEnums = [{self.uml_enum.name}], \nRelations = [{self.uml_relation_1}])"
        self.assertEqual(repr(uml_model), expected_repr)

    def test_uml_model_str(self):
        uml_model = UMLModel(class_list=[self.uml_class], enum_list=[self.uml_enum], relation_list=[self.uml_relation_1])
        expected_str = "UMLModel(Classes: 1, Enums: 1, Relations: 1)"
        self.assertEqual(str(uml_model), expected_str)

    def test_uml_model_to_plantuml(self):
        uml_model = UMLModel(class_list=[self.uml_class], enum_list=[self.uml_enum], relation_list=[self.uml_relation_1])
        expected_plantuml_lines = [
            "@startuml",
            "skinparam Linetype ortho",
            "skinparam nodesep 100",
            "skinparam ranksep 100",
            "hide empty attributes",
            "hide empty methods",
            "class TestClass {",
            "\t+attribute1: str",
            "\t-attribute2: int",
            "\t+operation1(): void",
            "\t-operation2(): int",
            "}",
            "enum TestEnum {",
            "\tVALUE1",
            "\tVALUE2",
            "}",
            "TestClass \"1\" -- \"1\" TestEnum",
            "@enduml"
        ]
        expected_plantuml = '\n'.join(expected_plantuml_lines)
        self.assertEqual(uml_model.to_plantuml().strip(), expected_plantuml)

    def test_uml_model_asign_relations(self):
        uml_model = UMLModel(class_list=[self.uml_class], enum_list=[self.uml_enum])
        uml_model.relation_list.append(self.uml_relation_1)
        uml_model.relation_list.append(self.uml_relation_2)
        uml_model.assign_relations()
        # Check if the relation is assigned to the class
        self.assertIn(self.uml_relation_1, self.uml_class.relations)        
        self.assertNotIn(self.uml_relation_2, self.uml_class.relations)
        # Check if the swapped relation, relation 2 are assigned to the enum
        self.assertIn(self.uml_swapped_relation_1, self.uml_enum.relations)
        self.assertIn(self.uml_relation_2, self.uml_enum.relations)

    def test_find_element(self):
        uml_model = UMLModel(class_list=[self.uml_class], enum_list=[self.uml_enum], relation_list=[self.uml_relation_1])
        found_class = uml_model.find_element("TestClass")
        found_enum = uml_model.find_element("TestEnum")
        found_relation = uml_model.find_element("(TestClass, TestEnum)")

        self.assertEqual(found_class, self.uml_class)
        self.assertEqual(found_enum, self.uml_enum)
        self.assertEqual(found_relation, self.uml_relation_1)
        self.assertIsNone(uml_model.find_element("NonExistent"))

    def test_find_class(self):
        uml_model = UMLModel(class_list=[self.uml_class], enum_list=[self.uml_enum], relation_list=[self.uml_relation_1])
        found_class = uml_model.find_class("TestClass")
        self.assertEqual(found_class, self.uml_class)
        self.assertIsNone(uml_model.find_class("NonExistent"))

    def test_find_enum(self):
        uml_model = UMLModel(class_list=[self.uml_class], enum_list=[self.uml_enum], relation_list=[self.uml_relation_1])
        found_enum = uml_model.find_enum("TestEnum")
        self.assertEqual(found_enum, self.uml_enum)
        self.assertIsNone(uml_model.find_enum("NonExistent"))

    def test_find_relation(self):
        uml_model = UMLModel(class_list=[self.uml_class], enum_list=[self.uml_enum], relation_list=[self.uml_relation_1])
        found_relation = uml_model.find_relation("(TestClass, TestEnum)")
        self.assertEqual(found_relation, self.uml_relation_1)
        self.assertIsNone(uml_model.find_relation("NonExistent"))

    # NOTE: print_details is just for terminal output, not tested here
