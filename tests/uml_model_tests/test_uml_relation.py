from UML_model.uml_relation import UMLRelation, UMLRelationType
from UML_model.uml_element import UMLElement
from UML_model.uml_class import UMLClass
import unittest

class TestUMLRelationType(unittest.TestCase):
    def test_relation_enum(self):
        self.assertEqual(UMLRelationType.ASSOCIATION.value, "association")
        self.assertEqual(UMLRelationType.AGGREGATION.value, "aggregation")
        self.assertEqual(UMLRelationType.COMPOSITION.value, "composition")
        self.assertEqual(UMLRelationType.ASSOCIATION_LINK.value, "association link")
        self.assertEqual(UMLRelationType.UNKNOWN.value, "unknown")

class TestUMLRelation(unittest.TestCase):
    def setUp(self):
        self.source = UMLClass("Source")
        self.destination = UMLClass("Destination")
        self.relation = UMLRelation(type=UMLRelationType.ASSOCIATION, source=self.source, destination=self.destination, s_multiplicity="1", d_multiplicity="0..*")

    def test_uml_relation_init_full_directed(self):
        relation = UMLRelation(type=UMLRelationType.ASSOCIATION, source=self.source, destination=self.destination, s_multiplicity="1", d_multiplicity="0..*")
        self.assertEqual(relation.type, UMLRelationType.ASSOCIATION)
        self.assertEqual(relation.source, self.source)
        self.assertEqual(relation.destination, self.destination)
        self.assertEqual(relation.s_multiplicity, "1")
        self.assertEqual(relation.d_multiplicity, "0..*")
        self.assertFalse(relation.directed)
        self.assertIsInstance(relation, UMLElement)

    def test_uml_relation_init_full_not_directed(self):
        relation = UMLRelation(type=UMLRelationType.AGGREGATION, source=self.source, destination=self.destination, s_multiplicity="1", d_multiplicity="0..*")
        self.assertEqual(relation.type, UMLRelationType.AGGREGATION)
        self.assertEqual(relation.source, self.source)
        self.assertEqual(relation.destination, self.destination)
        self.assertEqual(relation.s_multiplicity, "1")
        self.assertEqual(relation.d_multiplicity, "0..*")
        self.assertTrue(relation.directed)
        self.assertIsInstance(relation, UMLElement)      

    def test_uml_relation_init_empty(self):
        relation = UMLRelation(type=UMLRelationType.ASSOCIATION, source=self.source, destination=self.destination)
        self.assertEqual(relation.type, UMLRelationType.ASSOCIATION)
        self.assertEqual(relation.source, self.source)
        self.assertEqual(relation.destination, self.destination)
        self.assertEqual(relation.s_multiplicity, "")
        self.assertEqual(relation.d_multiplicity, "")
        self.assertFalse(relation.directed)
        self.assertIsInstance(relation, UMLElement)

    def test_uml_relation_repr(self):
        expected = "UMLRelation(UMLClass(Source), UMLClass(Destination)): source multiplicity 1 -ASSOCIATION- destination multiplicity 0..*"
        self.assertEqual(repr(self.relation), expected)

    def test_uml_relation_str(self):
        expected = "UMLRelation((Source, Destination))"
        self.assertEqual(str(self.relation), expected)

    def test_uml_relation_to_plantuml_association(self):
        expected = 'Source "1" -- "0..*" Destination'
        self.assertEqual(self.relation.to_plantuml(), expected)

    def test_uml_relation_to_plantuml_aggregation(self):
        relation = UMLRelation(type=UMLRelationType.AGGREGATION, source=self.source, destination=self.destination, s_multiplicity="1", d_multiplicity="0..*")
        expected = 'Source "1" --o "0..*" Destination'
        self.assertEqual(relation.to_plantuml(), expected)

    def test_uml_relation_to_plantuml_composition(self):
        relation = UMLRelation(type=UMLRelationType.COMPOSITION, source=self.source, destination=self.destination, s_multiplicity="1", d_multiplicity="0..*")
        expected = 'Source "1" --* "0..*" Destination'
        self.assertEqual(relation.to_plantuml(), expected)

    def test_uml_relation_to_plantuml_association_link(self):
        asso_class = UMLClass("AssociationClass")
        relation = UMLRelation(type=UMLRelationType.ASSOCIATION_LINK, source=asso_class, destination=self.relation)
        expected = 'AssociationClass  ..  (Source, Destination)'
        self.assertEqual(relation.to_plantuml(), expected)

    def test_uml_relation_eq_same_direction_equals(self):
        relation1 = UMLRelation(type=UMLRelationType.AGGREGATION, source=self.source, destination=self.destination)
        relation2 = UMLRelation(type=UMLRelationType.AGGREGATION, source=self.source, destination=self.destination)
        self.assertEqual(relation1, relation2)

    def test_uml_relation_eq_same_direction_not_equals(self):
        relation1 = UMLRelation(type=UMLRelationType.AGGREGATION, source=self.source, destination=self.destination)
        relation2 = UMLRelation(type=UMLRelationType.AGGREGATION, source=self.source, destination=self.destination, s_multiplicity="1", d_multiplicity="0..*")
        self.assertNotEqual(relation1, relation2)

    def test_uml_relation_eq_reverse_direction_equals(self):
        relation1 = UMLRelation(type=UMLRelationType.ASSOCIATION, source=self.source, destination=self.destination, s_multiplicity="1", d_multiplicity="0..*")
        relation2 = UMLRelation(type=UMLRelationType.ASSOCIATION, source=self.destination, destination=self.source, s_multiplicity="0..*", d_multiplicity="1")
        self.assertEqual(relation1, relation2)

    def test_uml_relation_eq_reverse_direction_not_equals(self):
        relation1 = UMLRelation(type=UMLRelationType.ASSOCIATION, source=self.source, destination=self.destination, s_multiplicity="1", d_multiplicity="0..*")
        relation2 = UMLRelation(type=UMLRelationType.ASSOCIATION, source=self.destination, destination=self.source, s_multiplicity="1*", d_multiplicity="1")
        self.assertNotEqual(relation1, relation2)

    # NOTE: equals same functionality as __eq__ but without multiplicities
    def test_uml_relation_equals_same_direction_equals(self):
        relation1 = UMLRelation(type=UMLRelationType.AGGREGATION, source=self.source, destination=self.destination)
        relation2 = UMLRelation(type=UMLRelationType.AGGREGATION, source=self.source, destination=self.destination)
        self.assertTrue(relation1.equals(relation2))

    def test_uml_relation_equals_reverse_direction_equals(self):
        relation1 = UMLRelation(type=UMLRelationType.ASSOCIATION, source=self.source, destination=self.destination)
        relation2 = UMLRelation(type=UMLRelationType.ASSOCIATION, source=self.destination, destination=self.source)
        self.assertTrue(relation1.equals(relation2)) 
        
    def test_uml_relation_equals_same_direction_not_equal(self):
        relation1 = UMLRelation(type=UMLRelationType.ASSOCIATION, source=self.source, destination=self.destination)
        relation2 = UMLRelation(type=UMLRelationType.AGGREGATION, source=self.source, destination=self.destination)
        self.assertFalse(relation1.equals(relation2))   

    def test_uml_relation_equals_reverse_direction_not_equal(self):
        relation1 = UMLRelation(type=UMLRelationType.ASSOCIATION, source=self.source, destination=self.destination)
        relation2 = UMLRelation(type=UMLRelationType.ASSOCIATION, source=self.source, destination=self.source)
        self.assertFalse(relation1.equals(relation2))

    def test_uml_relation_hash(self):
        relation1 = UMLRelation(type=UMLRelationType.ASSOCIATION, source=self.source, destination=self.destination)
        relation2 = UMLRelation(type=UMLRelationType.ASSOCIATION, source=self.source, destination=self.destination)
        self.assertEqual(hash(relation1), hash(relation2))

    def test_uml_relation_swap_source_destination(self):
        relation = UMLRelation(type=UMLRelationType.ASSOCIATION, source=self.source, destination=self.destination, s_multiplicity="1", d_multiplicity="0..*")
        swapped = relation.swap_source_destination()
        self.assertEqual(swapped.source, self.destination)
        self.assertEqual(swapped.destination, self.source)
        self.assertEqual(swapped.type, UMLRelationType.ASSOCIATION)
        self.assertEqual(swapped.s_multiplicity, relation.d_multiplicity)
        self.assertEqual(swapped.d_multiplicity, relation.s_multiplicity)
        # NOTE: important: name stays the same
        self.assertEqual(relation.name, self.relation.name)

    def test_uml_relation_swap_source_destination_directed(self):
        relation = UMLRelation(type=UMLRelationType.AGGREGATION, source=self.source, destination=self.destination, s_multiplicity="1", d_multiplicity="0..*")
        # raises ValueError if directed
        with self.assertRaises(ValueError):
            relation.swap_source_destination()
        
