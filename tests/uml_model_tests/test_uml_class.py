from UML_model.uml_class import UMLAttribute, UMLDataType, UMLVisability, UMLOperation, UMLClass
from UML_model.uml_element import UMLElement
from UML_model.uml_relation import UMLRelation, UMLRelationType
from grading.grade_reference import GradeReference
import unittest

class TestUMLDataType(unittest.TestCase):
    def test_data_type_enum(self):
        # Test the data type enum values
        self.assertEqual(UMLDataType.STR.value, "str")
        self.assertEqual(UMLDataType.INT.value, "int")
        self.assertEqual(UMLDataType.FLOAT.value, "float")
        self.assertEqual(UMLDataType.BOOL.value, "bool")
        self.assertEqual(UMLDataType.VOID.value, "void")
        self.assertEqual(UMLDataType.UNKNOWN.value, "")

    def test_from_string_valid_types(self):
        # Test valid data type strings
        self.assertEqual(UMLDataType.from_string("str"), UMLDataType.STR)
        self.assertEqual(UMLDataType.from_string("string"), UMLDataType.STR)
        self.assertEqual(UMLDataType.from_string("int"), UMLDataType.INT)
        self.assertEqual(UMLDataType.from_string("integer"), UMLDataType.INT)
        self.assertEqual(UMLDataType.from_string("float"), UMLDataType.FLOAT)
        self.assertEqual(UMLDataType.from_string("double"), UMLDataType.FLOAT)
        self.assertEqual(UMLDataType.from_string("bool"), UMLDataType.BOOL)
        self.assertEqual(UMLDataType.from_string("boolean"), UMLDataType.BOOL)
        self.assertEqual(UMLDataType.from_string("void"), UMLDataType.VOID)
        self.assertEqual(UMLDataType.from_string("none"), UMLDataType.VOID)

    def test_from_string_invalid_type(self):
        # Test invalid data type strings
        self.assertEqual(UMLDataType.from_string("unknown_type"), UMLDataType.UNKNOWN)
        self.assertEqual(UMLDataType.from_string("123"), UMLDataType.UNKNOWN)

class TestUMLVisability(unittest.TestCase):
    def test_visability_enum(self):
        # Test the visability enum values
        self.assertEqual(UMLVisability.PUBLIC.value, "+")
        self.assertEqual(UMLVisability.PRIVATE.value, "-")
        self.assertEqual(UMLVisability.PROTECTED.value, "#")
        self.assertEqual(UMLVisability.PACKAGE.value, "~")
        self.assertEqual(UMLVisability.UNKNOWN.value, "")

class TestUMLAttribute(unittest.TestCase):
    def setUp(self):
        self.empty_attribute = UMLAttribute(name="testAttributeEmpty")
        self.full_attribute = UMLAttribute(name="testAttributeFull", data_type=UMLDataType.STR, initial="default", visibility=UMLVisability.PUBLIC, derived=False)
        self.derived_attribute = UMLAttribute(name="testAttributeDerived", data_type=UMLDataType.STR, initial="default", visibility=UMLVisability.PUBLIC, derived=True)
        self.no_initial_attribute = UMLAttribute(name="testAttributeNoInitial", data_type=UMLDataType.STR, visibility=UMLVisability.PUBLIC, derived=False)
        self.no_visibility_attribute = UMLAttribute(name="testAttributeNoVisibility", data_type=UMLDataType.STR, initial="default", derived=False)

    def test_uml_attribute_initialization_empty(self):
        # Test initialization with basic attributes
        uml_attribute = UMLAttribute(name="testAttribute")

        self.assertEqual(uml_attribute.name, "testAttribute")
        self.assertEqual(uml_attribute.data_type, UMLDataType.UNKNOWN)
        self.assertEqual(uml_attribute.initial, "")
        self.assertEqual(uml_attribute.visibility, UMLVisability.UNKNOWN)
        self.assertFalse(uml_attribute.derived)
        self.assertIsNone(uml_attribute.reference)

    def test_uml_attribute_initialization_full(self):
        # Test initialization with all attributes
        uml_attribute = UMLAttribute(
            name="testAttribute",
            data_type=UMLDataType.INT,
            initial="0",
            visibility=UMLVisability.PRIVATE,
            derived=True
        )

        self.assertEqual(uml_attribute.name, "testAttribute")
        self.assertEqual(uml_attribute.data_type, UMLDataType.INT)
        self.assertEqual(uml_attribute.initial, "0")
        self.assertEqual(uml_attribute.visibility, UMLVisability.PRIVATE)
        self.assertTrue(uml_attribute.derived)
        self.assertIsNone(uml_attribute.reference)

    def test_uml_attribute_repr_derived(self):
        # Test the __repr__ method
        expected_repr = "UMLAttribute(/testAttributeDerived): visability PUBLIC, datatype STR, initial = default"
        self.assertEqual(repr(self.derived_attribute), expected_repr)

    def test_uml_attribute_repr_no_initial(self):
        # Test the __repr__ method for non-derived attribute
        expected_repr = "UMLAttribute(testAttributeNoInitial): visability PUBLIC, datatype STR, initial None"
        self.assertEqual(repr(self.no_initial_attribute), expected_repr)

    def test_uml_attribute_str(self):
        # Test the __str__ method
        expected_str = "UMLAttribute(testAttributeDerived)"
        self.assertEqual(str(self.derived_attribute), expected_str)

    def test_uml_attribute_to_plantuml_full(self):
        # Test the to_plantuml method for a full attribute
        expected_plantuml = "+testAttributeFull: str = default"
        self.assertEqual(self.full_attribute.to_plantuml(), expected_plantuml)

    def test_uml_attribute_to_plantuml_derived(self):
        # Test the to_plantuml method
        expected_plantuml = "+/testAttributeDerived: str = default"
        self.assertEqual(self.derived_attribute.to_plantuml(), expected_plantuml)

    def test_uml_attribute_to_plantuml_no_initial(self):
        # Test the to_plantuml method without initial value
        expected_plantuml = "+testAttributeNoInitial: str"
        self.assertEqual(self.no_initial_attribute.to_plantuml(), expected_plantuml)

    def test_uml_attribute_to_plantuml_no_visibility(self):
        # Test the to_plantuml method without visibility
        expected_plantuml = "testAttributeNoVisibility: str = default"
        self.assertEqual(self.no_visibility_attribute.to_plantuml(), expected_plantuml)

    def test_uml_attribute_to_plantuml_empty(self):
        # Test the to_plantuml method for an empty attribute
        expected_plantuml = "testAttributeEmpty"
        self.assertEqual(self.empty_attribute.to_plantuml(), expected_plantuml)

    def test_uml_attribute_hash_equal(self):
        # Test the __hash__ method
        uml_attribute1 = UMLAttribute(name="testAttribute")
        uml_attribute2 = UMLAttribute(name="testAttribute")

        self.assertEqual(hash(uml_attribute1), hash(uml_attribute2))

    def test_uml_attribute_hash_not_equal(self):
        # Test the __hash__ method for different names
        uml_attribute1 = UMLAttribute(name="testAttribute1")
        uml_attribute2 = UMLAttribute(name="testAttribute2")

        self.assertNotEqual(hash(uml_attribute1), hash(uml_attribute2))

    def test_uml_attribute_eq_equal(self):
        # Test the __eq__ method
        uml_attribute1 = UMLAttribute(name="testAttribute", data_type=UMLDataType.INT, initial="0")
        uml_attribute2 = UMLAttribute(name="testAttribute", data_type=UMLDataType.INT, initial="0")

        self.assertEqual(uml_attribute1, uml_attribute2)

    def test_uml_attribute_eq_not_equal(self):
        # Test the __eq__ method for different names or parameters
        uml_attribute1 = UMLAttribute(name="testAttribute1", data_type=UMLDataType.INT, initial="0")
        uml_attribute2 = UMLAttribute(name="testAttribute2", data_type=UMLDataType.STR, initial="0")

        self.assertNotEqual(uml_attribute1, uml_attribute2)

    def test_uml_attribute_eq_different_class(self):
        # Test the __eq__ method for different classes
        uml_attribute1 = UMLAttribute(name="testAttribute", data_type=UMLDataType.INT, initial="0")
        uml_operation = UMLOperation(name="testOperation")

        self.assertNotEqual(uml_attribute1, uml_operation)

class UMLOperationTest(unittest.TestCase):
    def setUp(self):
        self.empty_operation = UMLOperation(name="testOperationEmpty")
        self.full_operation = UMLOperation(name="testOperationFull", params={"param1": UMLDataType.INT, "param2": UMLDataType.UNKNOWN}, return_types=[UMLDataType.FLOAT], visibility=UMLVisability.PUBLIC)
        self.no_params_operation = UMLOperation(name="testOperationNoParams", return_types=[UMLDataType.VOID], visibility=UMLVisability.PRIVATE)
        self.no_return_operation = UMLOperation(name="testOperationNoReturn", params={"param1": UMLDataType.INT}, visibility=UMLVisability.PROTECTED)
        self.no_visibility_operation = UMLOperation(name="testOperationNoVisibility", params={"param1": UMLDataType.INT}, return_types=[UMLDataType.VOID])

    def test_uml_operation_initialization_empty(self):
        # Test initialization with basic attributes
        uml_operation = UMLOperation(name="testOperation")

        self.assertEqual(uml_operation.name, "testOperation")
        self.assertEqual(uml_operation.return_types, [UMLDataType.VOID])
        self.assertEqual(uml_operation.params, {})
        self.assertEqual(uml_operation.visibility, UMLVisability.UNKNOWN)
        self.assertIsNone(uml_operation.reference)

    def test_uml_operation_initialization_full(self):
        # Test initialization with all attributes
        uml_operation = UMLOperation(
            name="testOperation",
            params={"param1": UMLDataType.INT, "param2": UMLDataType.STR},
            return_types=[UMLDataType.FLOAT],
            visibility=UMLVisability.PUBLIC
        )

        self.assertEqual(uml_operation.name, "testOperation")
        self.assertEqual(uml_operation.params, {"param1": UMLDataType.INT, "param2": UMLDataType.STR})
        self.assertEqual(uml_operation.return_types, [UMLDataType.FLOAT])
        self.assertEqual(uml_operation.visibility, UMLVisability.PUBLIC)
        self.assertIsNone(uml_operation.reference)

    def test_uml_operation_repr(self):
        # Test the __repr__ method
        expected_repr = "UMLOperation(testOperationFull(param1: INT, param2: UNKNOWN)): visability PUBLIC, return type [FLOAT]"
        self.assertEqual(repr(self.full_operation), expected_repr)

    def test_uml_operation_str(self):
        # Test the __str__ method
        expected_str = "UMLOperation(testOperationFull)"
        self.assertEqual(str(self.full_operation), expected_str)

    def test_uml_operation_to_plantuml_full(self):
        # Test the to_plantuml method for a full operation
        expected_plantuml = "+testOperationFull(param1: int, param2): float"
        self.assertEqual(self.full_operation.to_plantuml(), expected_plantuml)

    def test_uml_operation_to_plantuml_no_params(self):
        # Test the to_plantuml method without parameters
        expected_plantuml = "-testOperationNoParams(): void"
        self.assertEqual(self.no_params_operation.to_plantuml(), expected_plantuml)

    def test_uml_operation_to_plantuml_no_return(self):
        # Test the to_plantuml method without return type
        expected_plantuml = "#testOperationNoReturn(param1: int): void"
        self.assertEqual(self.no_return_operation.to_plantuml(), expected_plantuml)
    
    def test_uml_operation_to_plantuml_no_visibility(self):
        # Test the to_plantuml method without visibility
        expected_plantuml = "testOperationNoVisibility(param1: int): void"
        self.assertEqual(self.no_visibility_operation.to_plantuml(), expected_plantuml)

    def test_uml_operation_hash_equal(self):
        # Test the __hash__ method
        uml_operation1 = UMLOperation(name="testOperation")
        uml_operation2 = UMLOperation(name="testOperation")

        self.assertEqual(hash(uml_operation1), hash(uml_operation2))

    def test_uml_operation_hash_not_equal(self):
        # Test the __hash__ method for different names
        uml_operation1 = UMLOperation(name="testOperation1")
        uml_operation2 = UMLOperation(name="testOperation2")

        self.assertNotEqual(hash(uml_operation1), hash(uml_operation2))

    def test_uml_operation_eq_equal(self):
        # Test the __eq__ method
        uml_operation1 = UMLOperation(name="testOperation", params={"param1": UMLDataType.INT}, return_types=[UMLDataType.FLOAT])
        uml_operation2 = UMLOperation(name="testOperation", params={"param1": UMLDataType.INT}, return_types=[UMLDataType.FLOAT])

        self.assertEqual(uml_operation1, uml_operation2)

    def test_uml_operation_eq_not_equal(self):
        # Test the __eq__ method for different names or parameters
        uml_operation1 = UMLOperation(name="testOperation1", params={"param1": UMLDataType.INT}, return_types=[UMLDataType.FLOAT])
        uml_operation2 = UMLOperation(name="testOperation2", params={"param1": UMLDataType.STR}, return_types=[UMLDataType.FLOAT])

        self.assertNotEqual(uml_operation1, uml_operation2)

    def test_uml_operation_eq_different_class(self):
        # Test the __eq__ method for different classes
        uml_operation1 = UMLOperation(name="testOperation", params={"param1": UMLDataType.INT}, return_types=[UMLDataType.FLOAT])
        uml_attribute = UMLAttribute(name="testAttribute")

        self.assertNotEqual(uml_operation1, uml_attribute)

class TestUMLClass(unittest.TestCase):
    def setUp(self):
        # attributes and operations for testing
        self.attr1 = UMLAttribute(name="attr1", data_type=UMLDataType.INT)
        self.attr1_full = UMLAttribute(name="attr1", data_type=UMLDataType.INT, initial="0", visibility=UMLVisability.PUBLIC, derived=True)
        self.attr2_with_dt = UMLAttribute(name="attr2", data_type=UMLDataType.STR)

        self.op1 = UMLOperation(name="op1")
        self.op1_with_param = UMLOperation(name="op1", params={"param1": UMLDataType.STR})
        self.op1_full = UMLOperation(name="op1", params={"param1": UMLDataType.STR}, return_types=[UMLDataType.INT], visibility=UMLVisability.PUBLIC)
        self.op2 = UMLOperation(name="op2", params={"param2": UMLDataType.STR})

        # initialize UMLClass instances for testing
        self.empty_class = UMLClass(name="TestClassEmpty")
        self.full_class = UMLClass(name="TestClassFull", attributes=[self.attr1], operations=[self.op1_with_param])
        self.no_attributes_class = UMLClass(name="TestClassNoAttributes", operations=[self.op1])
        self.no_operations_class = UMLClass(name="TestClassNoOperations", attributes=[self.attr1])
   
    def test_uml_class_initialization_empty(self):
        # Test initialization with basic attributes
        uml_class = UMLClass(name="TestClass")

        self.assertEqual(uml_class.name, "TestClass")
        self.assertEqual(uml_class.attributes, [])
        self.assertEqual(uml_class.operations, [])
        self.assertEqual(uml_class.relations, [])
        self.assertIsNone(uml_class.super_class)
        self.assertIsInstance(uml_class, UMLElement)

    def test_uml_class_initialization_full(self):
        # Test initialization with all attributes
        uml_class = UMLClass(
            name="TestClass",
            attributes=[UMLAttribute(name="attr1", data_type=UMLDataType.INT, initial="0", visibility=UMLVisability.PUBLIC, derived=True)],
            operations=[UMLOperation(name="op1", params={"param1": UMLDataType.STR}, return_types=[UMLDataType.INT], visibility=UMLVisability.PUBLIC)]
        )

        self.assertEqual(uml_class.name, "TestClass")
        self.assertEqual(len(uml_class.attributes), 1)
        self.assertEqual(len(uml_class.operations), 1)
        self.assertEqual(uml_class.relations, [])
        self.assertIsNone(uml_class.super_class)
        self.assertIsInstance(uml_class, UMLElement)

        self.assertEqual(uml_class.attributes[0].name, "attr1")
        self.assertEqual(uml_class.attributes[0].data_type, UMLDataType.INT)
        self.assertEqual(uml_class.attributes[0].initial, "0")
        self.assertEqual(uml_class.attributes[0].visibility, UMLVisability.PUBLIC)
        self.assertTrue(uml_class.attributes[0].derived)
        # important: the reference is set to the class itself
        self.assertEqual(uml_class.attributes[0].reference, uml_class)

        self.assertEqual(uml_class.operations[0].name, "op1")
        self.assertEqual(uml_class.operations[0].params, {"param1": UMLDataType.STR})
        self.assertEqual(uml_class.operations[0].return_types, [UMLDataType.INT])
        self.assertEqual(uml_class.operations[0].visibility, UMLVisability.PUBLIC)
        # important: the reference is set to the class itself
        self.assertEqual(uml_class.operations[0].reference, uml_class)

    def test_uml_class_repr(self):
        # Test the __repr__ method
        expected_repr = "UMLClass(TestClassFull): \nattributes [UMLAttribute(attr1)], \noperations [UMLOperation(op1)], \nrelations []"
        self.assertEqual(repr(self.full_class), expected_repr)

    def test_uml_class_str(self):
        # Test the __str__ method
        expected_str = "UMLClass(TestClassFull)"
        self.assertEqual(str(self.full_class), expected_str)

    def test_uml_class_to_plantuml_empty(self):
        # Test the to_plantuml method for an empty class
        expected_plantuml = "class TestClassEmpty"
        self.assertEqual(self.empty_class.to_plantuml(), expected_plantuml)

    def test_uml_class_to_plantuml_full(self):
        # Test the to_plantuml method for a full class
        expected_plantuml = "class TestClassFull {\n\tattr1: int\n\top1(param1: str): void\n}"
        self.assertEqual(self.full_class.to_plantuml(), expected_plantuml)

    def test_uml_class_to_plantuml_no_attributes(self):
        # Test the to_plantuml method without attributes
        expected_plantuml = "class TestClassNoAttributes {\n\top1(): void\n}"
        self.assertEqual(self.no_attributes_class.to_plantuml(), expected_plantuml)

    def test_uml_class_to_plantuml_no_operations(self):
        # Test the to_plantuml method without operations
        expected_plantuml = "class TestClassNoOperations {\n\tattr1: int\n}"
        self.assertEqual(self.no_operations_class.to_plantuml(), expected_plantuml)

    def test_uml_class_eq_equal(self):
        # Test the __eq__ method for classes with same attributes and operations
        uml_class1 = UMLClass(name="TestClass", attributes=[UMLAttribute(name="attr1", data_type=UMLDataType.INT)], operations=[UMLOperation(name="op1")])
        uml_class2 = UMLClass(name="TestClass", attributes=[UMLAttribute(name="attr1", data_type=UMLDataType.INT)], operations=[UMLOperation(name="op1")])

        self.assertEqual(uml_class1, uml_class2)

    def test_uml_class_eq_not_equal(self):
        # Test the __eq__ method for different attributes and operations
        uml_class1 = UMLClass(name="TestClass", attributes=[UMLAttribute(name="attr1", data_type=UMLDataType.INT)], operations=[UMLOperation(name="op1")])
        uml_class2 = UMLClass(name="TestClass", attributes=[UMLAttribute(name="attr1", data_type=UMLDataType.STR)], operations=[UMLOperation(name="op2")])

        self.assertNotEqual(uml_class1, uml_class2)

    def test_uml_class_eq_different_class(self):
        # Test the __eq__ method for different classes
        uml_class = UMLClass(name="TestClass")
        uml_attribute = UMLAttribute(name="attr1")

        self.assertNotEqual(uml_class, uml_attribute)

    def test_uml_class_hash_equal(self):
        # Test the __hash__ method
        uml_class1 = UMLClass(name="TestClass")
        uml_class2 = UMLClass(name="TestClass")

        self.assertEqual(hash(uml_class1), hash(uml_class2))

    def test_uml_class_hash_not_equal(self):
        # Test the __hash__ method for different names
        uml_class1 = UMLClass(name="TestClass1")
        uml_class2 = UMLClass(name="TestClass2")

        self.assertNotEqual(hash(uml_class1), hash(uml_class2))

    def test_uml_class_assign_content_reference(self):
        # Test if the content reference is assigned correctly
        uml_class = UMLClass(name="TestClass")
        attr = UMLAttribute(name="attr1", data_type=UMLDataType.INT)
        op = UMLOperation(name="op1")

        uml_class.attributes.append(attr)
        uml_class.operations.append(op)

        UMLClass.assign_content_reference(uml_class)

        self.assertEqual(attr.reference, uml_class)
        self.assertEqual(op.reference, uml_class)

    def test_uml_class_add_relation(self):
        # Test adding a relation to the class
        uml_class = UMLClass(name="TestClass")
        relation = UMLRelation(source=uml_class, destination=UMLClass(name="TargetClass"), type=UMLRelationType.ASSOCIATION)
        uml_class.add_relation(relation)
        self.assertIn(relation, uml_class.relations)

    def test_uml_class_get_relation_ends_full(self):
        # Test getting relation ends
        uml_class1 = UMLClass(name="Class1")
        uml_class2 = UMLClass(name="Class2")
        relation = UMLRelation(source=uml_class1, destination=uml_class2, type=UMLRelationType.ASSOCIATION)
        uml_class1.add_relation(relation)
        self.assertIn(relation, uml_class1.relations)
        ends_class1 = uml_class1.get_relation_ends()
        self.assertIn(uml_class2, ends_class1)
        self.assertNotIn(uml_class1, ends_class1) 

    def test_uml_class_get_relation_ends_empty(self):
        # Test getting relation ends when there are no relations
        ends = self.empty_class.get_relation_ends()
        self.assertEqual(ends, [])

    def test_uml_class_find_attribute_exists(self):
        # Test finding an attribute by name
        uml_class = UMLClass(name="TestClass")
        uml_class.attributes.extend([self.attr1, self.attr2_with_dt])

        found_attr = uml_class.find_attribute("attr1")
        self.assertEqual(found_attr, self.attr1)
        self.assertNotEqual(found_attr, self.attr2_with_dt)

    def test_uml_class_find_attribute_not_exists(self):
        # Test finding an attribute that does not exist
        found_attr = self.full_class.find_attribute("nonExistentAttr")
        self.assertIsNone(found_attr)

    def test_uml_class_find_operation_exists(self):
        # Test finding an operation by name
        uml_class = UMLClass(name="TestClass")
        op1 = UMLOperation(name="op1", params={"param1": UMLDataType.INT})
        op2 = UMLOperation(name="op2", params={"param2": UMLDataType.STR})
        uml_class.operations.extend([op1, op2])

        found_op = uml_class.find_operation("op1")
        self.assertEqual(found_op, op1)
        self.assertNotEqual(found_op, op2)

    def test_uml_class_find_operation_not_exists(self):
        # Test finding an operation that does not exist
        found_op = self.full_class.find_operation("nonExistentOp")
        self.assertIsNone(found_op)

    # NOTE: print_details is not tested here as it is a console output function