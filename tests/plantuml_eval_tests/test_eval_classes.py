from plantuml_eval.eval_classes import ClassComperator
from UML_model.uml_model import UMLModel
from UML_model.uml_class import UMLClass, UMLAttribute, UMLDataType, UMLVisability
from grading.grade_metamodel import GradeModel
import unittest
from typing import Dict


class TestClassComperator(unittest.TestCase):
    def setUp(self):
        self.instructor_model = """
        @startuml
        class Apple {
            +color: String
            -taste: double
            getFromTree(amount: int)
            #selectTree(): String
        }
        class Banana {
            +length: int
            ripeness
            +peel(percentage: int)
            eat()
        }
        class Cherry
        class Date
        class Elderberry {
            -age: int = 1
            +mix(): void
        }

        Apple --o Banana
        Apple -- Cherry
        Banana *-- Elderberry
        Banana -- Date
        @enduml
        """
        
        self.student_model = """
        @startuml
        class Apples {
            +color: String
            -aroma: double
            getFromTree(amount: int)
            #chooseTree(): String
        }
        class Apple {
            +color: String
            #chooseTree(): String
        }
        class BitterMelon 
        class Cherry {
            +size: int
            consume()
        }
        class Date {
            +length: int
            ripeness
            +peel(percentage: int)
            eat()
        }
        class Eggplant

        Apples --o Apple
        Apples -- Cherry
        Apple *-- Eggplant 
        Apple -- Date
        @enduml
        """

        self.instructor_model = UMLModel(self.instructor_model)
        self.student_model = UMLModel(self.student_model)

        # initializing test classes
        self.apple = self.instructor_model.class_lookup["apple"]
        self.banana = self.instructor_model.class_lookup["banana"]
        self.cherry = self.instructor_model.class_lookup["cherry"]
        self.date = self.instructor_model.class_lookup["date"]
        self.elderberry = self.instructor_model.class_lookup["elderberry"]

        # initializing test grade model
        self.grade_model = GradeModel(self.instructor_model)
        
        self.grade_model.add_class_grade_structure(cls=self.apple, exists_points=1.0, attribute_points=1.0, operation_points=1.0)
        self.grade_model.add_class_grade_structure(cls=self.banana, exists_points=1.0, attribute_points=1.0, operation_points=1.0)
        self.grade_model.add_class_grade_structure(cls=self.cherry, exists_points=1.0, attribute_points=1.0)
        self.grade_model.add_class_grade_structure(cls=self.date, exists_points=1.0, attribute_points=1.0)
        self.grade_model.add_class_grade_structure(cls=self.elderberry, exists_points=1.0, attribute_points=1.0, operation_points=1.0)

        # setting up possible class matches
        # NOTE: this has nothing to do with the actual mapping, its just an example for the test
        self.possible_class_matches = {self.apple: [self.apple, self.banana],
                                self.banana: [self.cherry, self.banana],
                                self.cherry: [self.cherry],
                                self.date: [self.date],
                                self.elderberry: []}
        
        self.match_map_id: Dict[UMLClass, UMLClass] = {
            self.apple: self.apple,
            self.banana: self.banana,
            self.cherry: self.cherry,
            self.date: self.date,
            self.elderberry: self.elderberry
        }
        
        self.true_class_matches = {
            self.apple: self.student_model.class_lookup["apples"],
            self.banana: self.student_model.class_lookup["apple"],
            self.cherry: self.student_model.class_lookup["cherry"],
            self.date: self.student_model.class_lookup["date"]
        }

        self.revered_true_class_matches = {
            self.student_model.class_lookup["apples"]: self.apple,
            self.student_model.class_lookup["apple"]: self.banana,
            self.student_model.class_lookup["cherry"]: self.cherry,
            self.student_model.class_lookup["date"]: self.date
        }

        # initializing test attributes
        self.apple_attr_1 = self.instructor_model.class_lookup["apple"].attributes[0]
        self.apple_attr_2 = self.instructor_model.class_lookup["apple"].attributes[1]
        self.banana_attr_1 = self.instructor_model.class_lookup["banana"].attributes[0]
        self.banana_attr_2 = self.instructor_model.class_lookup["banana"].attributes[1]
        self.elderberry_attr_1 = self.instructor_model.class_lookup["elderberry"].attributes[0]
        self.inst_attr_list = [self.apple_attr_1, self.apple_attr_2, self.banana_attr_1, self.banana_attr_2, self.elderberry_attr_1]
        
        self.apples_attr_1 = self.student_model.class_lookup["apples"].attributes[0]
        self.apples_attr_2 = self.student_model.class_lookup["apples"].attributes[1]
        self.apple_attr_1_1 = self.student_model.class_lookup["apple"].attributes[0]
        self.cherry_attr_1 = self.student_model.class_lookup["cherry"].attributes[0]
        self.date_attr_1 = self.student_model.class_lookup["date"].attributes[0]
        self.date_attr_2 = self.student_model.class_lookup["date"].attributes[1]
        self.student_attr_list = [self.apples_attr_1, self.apples_attr_2, self.apple_attr_1_1, self.cherry_attr_1, self.date_attr_1, self.date_attr_2]

        # setting up possible attribute matches
        # NOTE: this has nothing to do with the actual mapping, its just an example for the test
        self.possible_attr_matches = {
            self.apple_attr_1: [self.banana_attr_1, self.apple_attr_1],
            self.apple_attr_2: [self.apple_attr_2],
            self.banana_attr_1: [self.banana_attr_1, self.banana_attr_2],
            self.banana_attr_2: [self.banana_attr_2],
            self.elderberry_attr_1: []
        }
        self.safe_attr_matches: Dict[UMLAttribute, UMLAttribute] = {
            self.apple_attr_2: self.apple_attr_2,
            self.banana_attr_2: self.banana_attr_2
        }
        self.best_attr_matches: Dict[UMLAttribute, UMLAttribute] = {
            self.apple_attr_1: self.apple_attr_1,
            self.banana_attr_1: self.banana_attr_1
        }
        self.already_matched_attr: Dict[UMLAttribute, UMLAttribute] = {
            self.apple_attr_1: self.apple_attr_1,
            self.elderberry_attr_1: self.elderberry_attr_1
        }

        #initializing test operations
        self.apple_op_1 = self.apple.operations[0]
        self.apple_op_2 = self.apple.operations[1]
        self.banana_op_1 = self.banana.operations[0]
        self.banana_op_2 = self.banana.operations[1]
        self.elderberry_op_1 = self.elderberry.operations[0]
        self.inst_op_list = [self.apple_op_1, self.apple_op_2, self.banana_op_1, self.banana_op_2, self.elderberry_op_1]

        self.apples_op_1 = self.student_model.class_lookup["apples"].operations[0]
        self.apples_op_2 = self.student_model.class_lookup["apples"].operations[1]
        self.apple_op_1_1 = self.student_model.class_lookup["apple"].operations[0]
        self.cherry_op_1 = self.student_model.class_lookup["cherry"].operations[0]
        self.date_op_1 = self.student_model.class_lookup["date"].operations[0]
        self.date_op_2 = self.student_model.class_lookup["date"].operations[1]
        self.student_op_list = [self.apples_op_1, self.apples_op_2, self.apple_op_1_1, self.cherry_op_1, self.date_op_1, self.date_op_2]

        #setting up possible operation matches
        # NOTE: this has nothing to do with the actual mapping, its just an example for the test
        self.possible_op_matches = {
            self.apple_op_1: [self.banana_op_1, self.apple_op_1],
            self.apple_op_2: [self.apple_op_2],
            self.banana_op_1: [self.banana_op_1, self.banana_op_2],
            self.banana_op_2: [self.banana_op_2],
            self.elderberry_op_1: []
        }
        self.safe_op_matches: Dict[UMLAttribute, UMLAttribute] = {
            self.apple_op_2: self.apple_op_2,
            self.banana_op_2: self.banana_op_2
        }
        self.best_op_matches: Dict[UMLAttribute, UMLAttribute] = {
            self.apple_op_1: self.apple_op_1,
            self.banana_op_1: self.banana_op_1
        }
        self.already_matched_op: Dict[UMLAttribute, UMLAttribute] = {
            self.apple_op_1: self.apple_op_1,
            self.elderberry_op_1: self.elderberry_op_1
        }

    # tests for compare classes
    def test_comperator_get_safe_matches_classes(self):
        safe_matches = ClassComperator.get_safe_matches(self.possible_class_matches)
        self.assertIsInstance(safe_matches, dict)
        self.assertEqual(len(safe_matches), 1)
        self.assertEqual(self.date, list(safe_matches.keys())[0])

    def test_comperator_get_safe_matches_classes_empty(self):
        safe_matches = ClassComperator.get_safe_matches({})
        self.assertIsInstance(safe_matches, dict)
        self.assertEqual(len(safe_matches), 0)

    def test_comperator_find_best_class_match_assignment_without_gm(self):
        # This test is for the case where no grade model is provided
        # it shows what problems can occur if no grade model is provided
        best_match = ClassComperator.find_best_match_assignment(self.possible_class_matches)

        self.assertIsInstance(best_match, dict)
        self.assertEqual(len(best_match), 4)
        self.assertEqual(best_match[self.apple], self.apple)
        self.assertEqual(best_match[self.banana], self.cherry)
        self.assertEqual(best_match[self.cherry], self.cherry)
        self.assertEqual(best_match[self.date], self.date)

    def test_comperator_find_best_class_match_assignment_with_gm(self):
        best_match = ClassComperator.find_best_match_assignment(self.possible_class_matches, self.grade_model)

        self.assertIsInstance(best_match, dict)
        self.assertEqual(len(best_match), 4)
        self.assertEqual(best_match[self.apple], self.apple)
        self.assertEqual(best_match[self.banana], self.banana)
        self.assertEqual(best_match[self.cherry], self.cherry)
        self.assertEqual(best_match[self.date], self.date)

    def test_comperator_find_best_class_match_assignment_empty(self):
        # without grade model
        best_match = ClassComperator.find_best_match_assignment({})
        self.assertIsInstance(best_match, dict)
        self.assertEqual(len(best_match), 0)
        # with grade model
        best_match = ClassComperator.find_best_match_assignment({}, self.grade_model)
        self.assertIsInstance(best_match, dict)
        self.assertEqual(len(best_match), 0)

    def test_comperator_handle_possible_class_matches_without_gm(self):
        # combines safe and best matches
        # safe matches are excluded from best matches calculation
        safe_matches, best_matches = ClassComperator.handle_possible_matches(self.possible_class_matches)
        self.assertIsInstance(safe_matches, dict)
        self.assertEqual(len(safe_matches), 1)
        self.assertEqual(self.date, list(safe_matches.keys())[0])

        self.assertIsInstance(best_matches, dict)
        self.assertEqual(len(best_matches), 3)
        self.assertEqual(best_matches[self.apple], self.apple)
        self.assertEqual(best_matches[self.banana], self.cherry)
        self.assertEqual(best_matches[self.cherry], self.cherry)

    def test_comperator_handle_possible_class_matches_with_gm(self):
        # combines safe and best matches
        # safe matches are excluded from best matches calculation
        safe_matches, best_matches = ClassComperator.handle_possible_matches(self.possible_class_matches, self.grade_model)
        self.assertIsInstance(safe_matches, dict)
        self.assertEqual(len(safe_matches), 1)
        self.assertEqual(self.date, list(safe_matches.keys())[0])

        self.assertIsInstance(best_matches, dict)
        self.assertEqual(len(best_matches), 3)
        self.assertEqual(best_matches[self.apple], self.apple)
        self.assertEqual(best_matches[self.banana], self.banana)
        self.assertEqual(best_matches[self.cherry], self.cherry)

    def test_comperator_handle_possible_class_matches_empty(self):
        # combines safe and best matches
        # safe matches are excluded from best matches calculation
        # without grade model
        safe_matches, best_matches = ClassComperator.handle_possible_matches({})
        self.assertIsInstance(safe_matches, dict)
        self.assertEqual(len(safe_matches), 0)

        self.assertIsInstance(best_matches, dict)
        self.assertEqual(len(best_matches), 0)

        # with grade model
        safe_matches, best_matches = ClassComperator.handle_possible_matches({}, self.grade_model)
        self.assertIsInstance(safe_matches, dict)
        self.assertEqual(len(safe_matches), 0)

        self.assertIsInstance(best_matches, dict)
        self.assertEqual(len(best_matches), 0)

    def test_comperator_compare_classes_empty(self):
        instructor_model = UMLModel("@startuml\n@enduml")
        student_model = UMLModel("@startuml\n@enduml")
        grade_model = GradeModel(instructor_model)
        result = ClassComperator.compare_classes(instructor_model, student_model, grade_model)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertEqual(len(result[0]), 0)
        self.assertEqual(len(result[1]), 0)

    def test_comperator_compare_classes_instructor_empty(self):
        instructor_model = UMLModel("@startuml\n@enduml")
        result = ClassComperator.compare_classes(instructor_model, self.student_model)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertEqual(len(result[0]), 0)
        self.assertEqual(len(result[1]), 0)

    def test_comperator_compare_classes_student_empty(self):
        student_model = UMLModel("@startuml\n@enduml")
        result = ClassComperator.compare_classes(self.instructor_model, student_model)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertEqual(len(result[0]), 0)
        self.assertEqual(len(result[1]), 5)
        self.assertEqual(result[1][0].name, "Apple")
        self.assertEqual(result[1][1].name, "Banana")
        self.assertEqual(result[1][2].name, "Cherry")
        self.assertEqual(result[1][3].name, "Date")
        self.assertEqual(result[1][4].name, "Elderberry")

    def test_comperator_compare_classes_equal(self):
        result = ClassComperator.compare_classes(self.instructor_model, self.instructor_model, self.grade_model)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertEqual(len(result[0]), 5)
        self.assertEqual(len(result[1]), 0)
        self.assertEqual(result[0].get(self.instructor_model.class_lookup["apple"]), self.instructor_model.class_lookup["apple"])
        self.assertEqual(result[0].get(self.instructor_model.class_lookup["banana"]), self.instructor_model.class_lookup["banana"])
        self.assertEqual(result[0].get(self.instructor_model.class_lookup["cherry"]), self.instructor_model.class_lookup["cherry"])
        self.assertEqual(result[0].get(self.instructor_model.class_lookup["date"]), self.instructor_model.class_lookup["date"])
        self.assertEqual(result[0].get(self.instructor_model.class_lookup["elderberry"]), self.instructor_model.class_lookup["elderberry"])

    def test_comperator_compare_classes_different(self):
        result = ClassComperator.compare_classes(self.instructor_model, self.student_model, self.grade_model)
        """
        from student model expected possible matches would be:
            Apple -> Apples syntactic match, Apple syntactic match
            Banana -> Date content match
            Cherry -> Cherry syntactic match
            Date -> Date syntactic match
            Elderberry -> None

        expected safe matches:
            Cherry -> Cherry

        expected best matches:
            Apple -> Apples
            Date -> Date

        expected relation matches:
            Banana -> Apple

        result should contain:
            - 4 matches: Apple, Banana, Cherry, Date
            - 1 missing: Elderberry
        
        NOTE: may differ, when thresholds are changed in the tools.checker modules
        """

        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertEqual(len(result[0]), 4)
        self.assertEqual(len(result[1]), 1)
        self.assertEqual(result[0].get(self.instructor_model.class_lookup["apple"]), self.student_model.class_lookup["apples"])
        self.assertEqual(result[0].get(self.instructor_model.class_lookup["banana"]), self.student_model.class_lookup["apple"])
        self.assertEqual(result[0].get(self.instructor_model.class_lookup["cherry"]), self.student_model.class_lookup["cherry"])
        self.assertEqual(result[0].get(self.instructor_model.class_lookup["date"]), self.student_model.class_lookup["date"])
        self.assertEqual(result[1][0], self.instructor_model.class_lookup["elderberry"])

    # tests for compare attributes
    # NOTE: most empty method calls are not tested, for methods that were already tested in the class comperator tests, since the emptyness does not change for attributes
    def test_comperator_get_safe_matches_attributes(self):
        safe_matches = ClassComperator.get_safe_matches(self.possible_attr_matches)
        self.assertIsInstance(safe_matches, dict)
        self.assertEqual(len(safe_matches), 1)
        self.assertEqual(self.apple_attr_2, list(safe_matches.keys())[0])
        self.assertEqual(self.apple_attr_2, list(safe_matches.values())[0])

    def test_comperator_find_best_attr_match_assignment_without_gm(self):
        # This test is for the case where no grade model is provided
        # it shows what problems can occur if no grade model is provided
        best_match = ClassComperator.find_best_match_assignment(self.possible_attr_matches)

        self.assertIsInstance(best_match, dict)
        self.assertEqual(len(best_match), 4)
        self.assertEqual(best_match[self.apple_attr_1], self.banana_attr_1)
        self.assertEqual(best_match[self.apple_attr_2], self.apple_attr_2)
        self.assertEqual(best_match[self.banana_attr_1], self.banana_attr_1)
        self.assertEqual(best_match[self.banana_attr_2], self.banana_attr_2)
        self.assertIsNone(best_match.get(self.elderberry_attr_1))

    def test_comperator_find_best_attr_match_assignment_with_gm(self):
        best_match = ClassComperator.find_best_match_assignment(self.possible_attr_matches, self.grade_model)

        self.assertIsInstance(best_match, dict)
        self.assertEqual(len(best_match), 4)
        self.assertEqual(best_match[self.apple_attr_1], self.apple_attr_1)
        self.assertEqual(best_match[self.apple_attr_2], self.apple_attr_2)
        self.assertEqual(best_match[self.banana_attr_1], self.banana_attr_1)
        self.assertEqual(best_match[self.banana_attr_2], self.banana_attr_2)
        self.assertIsNone(best_match.get(self.elderberry_attr_1))

    def test_comperator_handle_possible_attr_matches_with_gm(self):
        # combines safe and best matches
        # safe matches are excluded from best matches calculation
        safe_matches, best_matches = ClassComperator.handle_possible_matches(self.possible_attr_matches, self.grade_model)
        self.assertIsInstance(safe_matches, dict)
        self.assertEqual(len(safe_matches), 1)
        self.assertEqual(self.apple_attr_2, list(safe_matches.keys())[0])
        self.assertEqual(self.apple_attr_2, list(safe_matches.values())[0])

        self.assertIsInstance(best_matches, dict)
        self.assertEqual(len(best_matches), 3)
        self.assertEqual(best_matches[self.apple_attr_1], self.apple_attr_1)
        self.assertEqual(best_matches[self.banana_attr_1], self.banana_attr_1)
        self.assertEqual(best_matches[self.banana_attr_2], self.banana_attr_2)
        self.assertIsNone(best_matches.get(self.elderberry_attr_1))

    def test_comperator_handle_safe_and_best_matches_empty_already_matched(self):
        match_map, unmatched = ClassComperator.handle_safe_and_best_matches(self.inst_attr_list, self.safe_attr_matches, self.best_attr_matches)
        self.assertIsInstance(match_map, dict)
        self.assertEqual(len(match_map), 4)
        self.assertEqual(match_map[self.apple_attr_1], self.apple_attr_1)
        self.assertEqual(match_map[self.apple_attr_2], self.apple_attr_2)
        self.assertEqual(match_map[self.banana_attr_1], self.banana_attr_1)
        self.assertEqual(match_map[self.banana_attr_2], self.banana_attr_2)
        self.assertIsInstance(unmatched, list)
        self.assertEqual(len(unmatched), 1)
        self.assertEqual(unmatched[0], self.elderberry_attr_1)

    def test_comperator_handle_safe_and_best_matches_empty_with_inst_atts(self):
        match_map, unmatched = ClassComperator.handle_safe_and_best_matches(self.inst_attr_list, {}, {})
        self.assertIsInstance(match_map, dict)
        self.assertEqual(len(match_map), 0)
        self.assertIsInstance(unmatched, list)
        self.assertEqual(len(unmatched), 5)
        self.assertEqual(unmatched[0], self.apple_attr_1)
        self.assertEqual(unmatched[1], self.apple_attr_2)
        self.assertEqual(unmatched[2], self.banana_attr_1)
        self.assertEqual(unmatched[3], self.banana_attr_2)
        self.assertEqual(unmatched[4], self.elderberry_attr_1)

    def test_comperator_handle_safe_and_best_matches_all_empty(self):
        match_map, unmatched = ClassComperator.handle_safe_and_best_matches([], {}, {})
        self.assertIsInstance(match_map, dict)
        self.assertEqual(len(match_map), 0)
        self.assertIsInstance(unmatched, list)
        self.assertEqual(len(unmatched), 0)

    def test_comperator_handle_safe_and_best_matches_safe_matches_empty(self):
        match_map, unmatched = ClassComperator.handle_safe_and_best_matches(self.inst_attr_list, {}, self.best_attr_matches)
        self.assertIsInstance(match_map, dict)
        self.assertEqual(len(match_map), 2)
        self.assertEqual(match_map[self.apple_attr_1], self.apple_attr_1)
        self.assertEqual(match_map[self.banana_attr_1], self.banana_attr_1)
        self.assertIsInstance(unmatched, list)
        self.assertEqual(len(unmatched), 3)
        self.assertEqual(unmatched[0], self.apple_attr_2)
        self.assertEqual(unmatched[1], self.banana_attr_2)
        self.assertEqual(unmatched[2], self.elderberry_attr_1)

    def test_comperator_handle_safe_and_best_matches_best_matches_empty(self):
        match_map, unmatched = ClassComperator.handle_safe_and_best_matches(self.inst_attr_list, self.safe_attr_matches, {})
        self.assertIsInstance(match_map, dict)
        self.assertEqual(len(match_map), 2)
        self.assertEqual(match_map[self.apple_attr_2], self.apple_attr_2)
        self.assertEqual(match_map[self.banana_attr_2], self.banana_attr_2)
        self.assertIsInstance(unmatched, list)
        self.assertEqual(len(unmatched), 3)
        self.assertEqual(unmatched[0], self.apple_attr_1)
        self.assertEqual(unmatched[1], self.banana_attr_1)
        self.assertEqual(unmatched[2], self.elderberry_attr_1)

    def test_comperator_handle_safe_and_best_matches_full(self):
        best_matches_contradiction: Dict[UMLAttribute, UMLAttribute] = {
            self.apple_attr_1: self.banana_attr_1,  # contradiction with already matched but should be ignored
            self.banana_attr_1: self.banana_attr_1
        }
        match_map, unmatched = ClassComperator.handle_safe_and_best_matches(self.inst_attr_list, self.safe_attr_matches, best_matches_contradiction, self.already_matched_attr)
        self.assertIsInstance(match_map, dict)
        self.assertEqual(len(match_map), 3)
        self.assertEqual(match_map[self.apple_attr_2], self.apple_attr_2)
        self.assertEqual(match_map[self.banana_attr_1], self.banana_attr_1)
        self.assertEqual(match_map[self.banana_attr_2], self.banana_attr_2)
        self.assertIsInstance(unmatched, list)
        self.assertEqual(len(unmatched), 0)

    def test_comperator_handle_safe_and_best_matches_empty_except_allready_matched(self):
        match_map, unmatched = ClassComperator.handle_safe_and_best_matches(self.inst_attr_list, {}, {}, self.already_matched_attr)
        self.assertIsInstance(match_map, dict)
        self.assertEqual(len(match_map), 0)
        self.assertIsInstance(unmatched, list)
        self.assertEqual(len(unmatched), 3)
        self.assertEqual(unmatched[0], self.apple_attr_2)
        self.assertEqual(unmatched[1], self.banana_attr_1)
        self.assertEqual(unmatched[2], self.banana_attr_2)

    def test_comperator_compare_attributes_empty(self):
        result = ClassComperator.compare_attributes([], [], {}, {})
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3)
        self.assertIsInstance(result[0], dict)
        self.assertEqual(len(result[0]), 0)
        self.assertIsInstance(result[1], dict)
        self.assertEqual(len(result[1]), 0)
        self.assertIsInstance(result[2], list)
        self.assertEqual(len(result[2]), 0)

    def test_comperator_compare_attributes_instructor_empty(self):
        result = ClassComperator.compare_attributes([], self.student_attr_list, self.true_class_matches, self.revered_true_class_matches)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3)
        self.assertIsInstance(result[0], dict)
        self.assertEqual(len(result[0]), 0)
        self.assertIsInstance(result[1], dict)
        self.assertEqual(len(result[1]), 0)
        self.assertIsInstance(result[2], list)
        self.assertEqual(len(result[2]), 0)

    def test_comperator_compare_attributes_student_empty(self):
        attr_match_map, misplaced_attr_map, miss_att_list = ClassComperator.compare_attributes(self.inst_attr_list, [], self.true_class_matches, self.revered_true_class_matches)
        self.assertIsInstance(attr_match_map, dict)
        self.assertEqual(len(attr_match_map), 0)
        self.assertIsInstance(misplaced_attr_map, dict)
        self.assertEqual(len(misplaced_attr_map), 0)
        self.assertIsInstance(miss_att_list, list)
        self.assertEqual(len(miss_att_list), 5)
        self.assertEqual(miss_att_list[0], self.inst_attr_list[0])
        self.assertEqual(miss_att_list[1], self.inst_attr_list[1])
        self.assertEqual(miss_att_list[2], self.inst_attr_list[2])
        self.assertEqual(miss_att_list[3], self.inst_attr_list[3])
        self.assertEqual(miss_att_list[4], self.inst_attr_list[4])

    def test_comperator_compare_attributes_match_map_empty_equal(self):
        attr_match_map, misplaced_attr_map, miss_att_list = ClassComperator.compare_attributes(self.inst_attr_list, self.inst_attr_list, {}, {}, self.grade_model)
        self.assertIsInstance(attr_match_map, dict)
        self.assertEqual(len(attr_match_map), 0)
        self.assertIsInstance(misplaced_attr_map, dict)
        self.assertEqual(len(misplaced_attr_map), 5)
        self.assertIsInstance(miss_att_list, list)
        self.assertEqual(len(miss_att_list), 0)
        self.assertEqual(misplaced_attr_map[self.apple_attr_1], self.apple_attr_1)
        self.assertEqual(misplaced_attr_map[self.apple_attr_2], self.apple_attr_2)
        self.assertEqual(misplaced_attr_map[self.banana_attr_1], self.banana_attr_1)
        self.assertEqual(misplaced_attr_map[self.banana_attr_2], self.banana_attr_2)
        self.assertEqual(misplaced_attr_map[self.elderberry_attr_1], self.elderberry_attr_1)

    def test_comperator_compare_attributes_match_map_empty_different(self):
        """
        for attributes in classes no matches should be found, since the classes are not matched
        ...
        expected possible matches:
        apple:
            +color: String -> syntactic apples: +color: String
                           -> syntactic apple: +color: String NOTE: this will be ignored see below
            -taste: double -> semnatic apples: -aroma: double
        banana:
            +length: int -> semantic cherry: +size: int
                         -> syntactic date: +length: int
            ripeness -> syntactic date: ripeness
        elderberry:
            -age: int = 1 -> None

        expected safe matches:
        apple: -taste: double -> apples: -aroma: double
        banana: ripeness -> date: ripeness

        expected best matches:
        apple: +color: String -> apples: +color: String == apples: +color: String
            NOTE: the attributes are equivalent through the eq method, so it will be mapped to the first one
            but shouldn't be a problem since both attributes would get the same points
            in this case only one of the attributes will be even evaluated
            this shouldnt be a problem since this shoul happen very rarely
            but could and probably should be overworked in the future
        banana: +length: int -> cherry: +size: int or date: +length: int
            NOTE: same here just with semantic equivalent names, but the attributes are not considered equivalent so it could be mapped either to cherry or date
        """
        attr_match_map, misplaced_attr_map, miss_att_list = ClassComperator.compare_attributes(self.inst_attr_list, self.student_attr_list, {}, {}, self.grade_model)
        self.assertIsInstance(attr_match_map, dict)
        self.assertEqual(len(attr_match_map), 0)

        self.assertIsInstance(misplaced_attr_map, dict)
        self.assertEqual(len(misplaced_attr_map), 4)

        self.assertEqual(misplaced_attr_map[self.apple_attr_1], self.apples_attr_1)
        self.assertEqual(misplaced_attr_map[self.apple_attr_2], self.apples_attr_2)
        self.assertIn(misplaced_attr_map[self.banana_attr_1], (self.cherry_attr_1, self.date_attr_1))  # either cherry or date, since both have a match and the content is identical
        self.assertEqual(misplaced_attr_map[self.banana_attr_2], self.date_attr_2)
        
        self.assertIsInstance(miss_att_list, list)
        self.assertEqual(len(miss_att_list), 1)
        self.assertEqual(miss_att_list[0], self.elderberry_attr_1)

        #TODO: expand this test to check for inheritance 

    def test_comperator_compare_attributes_equal(self):
        attr_match_map, misplaced_attr_map, miss_att_list = ClassComperator.compare_attributes(self.inst_attr_list, self.inst_attr_list, self.match_map_id, self.match_map_id, self.grade_model)
        self.assertIsInstance(attr_match_map, dict)
        self.assertEqual(len(attr_match_map), 5)
        self.assertEqual(attr_match_map[self.apple_attr_1], self.apple_attr_1)
        self.assertEqual(attr_match_map[self.apple_attr_2], self.apple_attr_2)
        self.assertEqual(attr_match_map[self.banana_attr_1], self.banana_attr_1)
        self.assertEqual(attr_match_map[self.banana_attr_2], self.banana_attr_2)
        self.assertEqual(attr_match_map[self.elderberry_attr_1], self.elderberry_attr_1)

        self.assertIsInstance(misplaced_attr_map, dict)
        self.assertEqual(len(misplaced_attr_map), 0)

        self.assertIsInstance(miss_att_list, list)
        self.assertEqual(len(miss_att_list), 0)

    def test_comperator_compare_attributes_different(self):
        attr_match_map, misplaced_attr_map, miss_att_list = ClassComperator.compare_attributes(self.inst_attr_list, self.student_attr_list, self.true_class_matches, self.revered_true_class_matches, self.grade_model)
        self.assertIsInstance(attr_match_map, dict)
        self.assertEqual(len(attr_match_map), 2)
        self.assertEqual(attr_match_map[self.apple_attr_1], self.apples_attr_1)
        self.assertEqual(attr_match_map[self.apple_attr_2], self.apples_attr_2)

        self.assertIsInstance(misplaced_attr_map, dict)
        self.assertEqual(len(misplaced_attr_map), 2)
        self.assertIn(misplaced_attr_map[self.banana_attr_1], (self.cherry_attr_1, self.date_attr_1))  # either cherry or date, since both have a match and the content is identical
        self.assertEqual(misplaced_attr_map[self.banana_attr_2], self.date_attr_2)

        self.assertIsInstance(miss_att_list, list)
        self.assertEqual(len(miss_att_list), 1)
        self.assertEqual(miss_att_list[0], self.elderberry_attr_1)

        #TODO: expand this test to check for inheritance 

    # tests for compare operations
    # NOTE: here only methods are tested that differ in implementation from the attribute tests and the general test if the method call works
    def test_comperator_get_safe_matches_operations(self):
        safe_matches = ClassComperator.get_safe_matches(self.possible_op_matches)
        self.assertIsInstance(safe_matches, dict)
        self.assertEqual(len(safe_matches), 1)
        self.assertEqual(self.apple_op_2, list(safe_matches.keys())[0])
        self.assertEqual(self.apple_op_2, list(safe_matches.values())[0])

    def test_comperator_find_best_op_match_assignment_with_gm(self):
        best_match = ClassComperator.find_best_match_assignment(self.possible_op_matches, self.grade_model)

        self.assertIsInstance(best_match, dict)
        self.assertEqual(len(best_match), 4)
        self.assertEqual(best_match[self.apple_op_1], self.apple_op_1)
        self.assertEqual(best_match[self.apple_op_2], self.apple_op_2)
        self.assertEqual(best_match[self.banana_op_1], self.banana_op_1)
        self.assertEqual(best_match[self.banana_op_2], self.banana_op_2)
        self.assertIsNone(best_match.get(self.elderberry_op_1))

    def test_comperator_handle_possible_op_matches_with_gm(self):
        # combines safe and best matches
        # safe matches are excluded from best matches calculation
        safe_matches, best_matches = ClassComperator.handle_possible_matches(self.possible_op_matches, self.grade_model)
        self.assertIsInstance(safe_matches, dict)
        self.assertEqual(len(safe_matches), 1)
        self.assertEqual(self.apple_op_2, list(safe_matches.keys())[0])
        self.assertEqual(self.apple_op_2, list(safe_matches.values())[0])

        self.assertIsInstance(best_matches, dict)
        self.assertEqual(len(best_matches), 3)
        self.assertEqual(best_matches[self.apple_op_1], self.apple_op_1)
        self.assertEqual(best_matches[self.banana_op_1], self.banana_op_1)
        self.assertEqual(best_matches[self.banana_op_2], self.banana_op_2)
        self.assertIsNone(best_matches.get(self.elderberry_op_1))

    def test_comperator_handle_safe_and_best_op_matches_full(self):
        best_matches_contradiction: Dict[UMLAttribute, UMLAttribute] = {
            self.apple_op_1: self.banana_op_1,  # contradiction with already matched but should be ignored
            self.banana_op_1: self.banana_op_1
        }
        match_map, unmatched = ClassComperator.handle_safe_and_best_matches(self.inst_op_list, self.safe_op_matches, best_matches_contradiction, self.already_matched_op)
        self.assertIsInstance(match_map, dict)
        self.assertEqual(len(match_map), 3)
        self.assertEqual(match_map[self.apple_op_2], self.apple_op_2)
        self.assertEqual(match_map[self.banana_op_1], self.banana_op_1)
        self.assertEqual(match_map[self.banana_op_2], self.banana_op_2)
        self.assertIsInstance(unmatched, list)
        self.assertEqual(len(unmatched), 0)

    def test_comperator_compare_operations_empty(self):
        result = ClassComperator.compare_operations([], [], {}, {})
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3)
        self.assertIsInstance(result[0], dict)
        self.assertEqual(len(result[0]), 0)
        self.assertIsInstance(result[1], dict)
        self.assertEqual(len(result[1]), 0)
        self.assertIsInstance(result[2], list)
        self.assertEqual(len(result[2]), 0)

    def test_comparator_compare_operations_instructor_empty(self):
        result = ClassComperator.compare_operations([], self.student_op_list, self.true_class_matches, self.revered_true_class_matches)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3)
        self.assertIsInstance(result[0], dict)
        self.assertEqual(len(result[0]), 0)
        self.assertIsInstance(result[1], dict)
        self.assertEqual(len(result[1]), 0)
        self.assertIsInstance(result[2], list)
        self.assertEqual(len(result[2]), 0)

    def test_comparator_compare_operations_student_empty(self):
        op_match_map, misplaced_op_map, miss_op_list = ClassComperator.compare_operations(self.inst_op_list, [], self.true_class_matches, self.revered_true_class_matches)
        self.assertIsInstance(op_match_map, dict)
        self.assertEqual(len(op_match_map), 0)
        self.assertIsInstance(misplaced_op_map, dict)
        self.assertEqual(len(misplaced_op_map), 0)
        self.assertIsInstance(miss_op_list, list)
        self.assertEqual(len(miss_op_list), 5)
        self.assertEqual(miss_op_list[0], self.apple_op_1)
        self.assertEqual(miss_op_list[1], self.apple_op_2)
        self.assertEqual(miss_op_list[2], self.banana_op_1)
        self.assertEqual(miss_op_list[3], self.banana_op_2)
        self.assertEqual(miss_op_list[4], self.elderberry_op_1)

    def test_comparator_compare_operations_match_map_empty_equal(self):
        op_match_map, misplaced_op_map, miss_op_list = ClassComperator.compare_operations(self.inst_op_list, self.inst_op_list, {}, {}, self.grade_model)
        self.assertIsInstance(op_match_map, dict)
        self.assertEqual(len(op_match_map), 0)
        self.assertIsInstance(misplaced_op_map, dict)
        self.assertEqual(len(misplaced_op_map), 5)
        self.assertIsInstance(miss_op_list, list)
        self.assertEqual(len(miss_op_list), 0)
        self.assertEqual(misplaced_op_map[self.apple_op_1], self.apple_op_1)
        self.assertEqual(misplaced_op_map[self.apple_op_2], self.apple_op_2)
        self.assertEqual(misplaced_op_map[self.banana_op_1], self.banana_op_1)
        self.assertEqual(misplaced_op_map[self.banana_op_2], self.banana_op_2)
        self.assertEqual(misplaced_op_map[self.elderberry_op_1], self.elderberry_op_1)

    def test_comparator_compare_operations_match_map_empty_different(self):
        """
        for operations in classes no matches should be found, since the classes are not matched
        ...
        expected possible matches:
        apple:
            getFromTree(amount: int) -> syntactic apples: getFromTree(amount: int)
                                     -> semantic apples: #chooseTree(): String
                                     -> semantic apple: #chooseTree(): String NOTE: same problem here as with attributes (eq)
            #selectTree(): String -> semantic apples: getFromTree(amount: int)
                                  -> semantic apples: #chooseTree(): String
                                  -> semantic apple: #chooseTree(): String NOTE: same problem here
        banana:
            +peel(percentage: int) -> syntactic date: +peel(percentage: int)
            eat() -> semantic cherry: consume()
                  -> syntactic date: eat()
        elderberry:
            +mix(): void -> None

        expected safe matches:
        banana: +peel(percentage: int) -> date: +peel(percentage: int)

        expected best matches:
        apple: getFromTree(amount: int) -> apples: getFromTree(amount: int)
               #selectTree(): String -> apples: #chooseTree(): String
        banana: eat() -> cherry: consume() or date: eat() NOTE: same as attribute with semantics
        """
        op_match_map, misplaced_op_map, miss_op_list = ClassComperator.compare_operations(self.inst_op_list, self.student_op_list, {}, {}, self.grade_model)
        self.assertIsInstance(op_match_map, dict)
        self.assertEqual(len(op_match_map), 0)

        self.assertIsInstance(misplaced_op_map, dict)
        self.assertEqual(len(misplaced_op_map), 4)

        self.assertEqual(misplaced_op_map[self.apple_op_1], self.apples_op_1)
        self.assertEqual(misplaced_op_map[self.apple_op_2], self.apples_op_2)
        self.assertEqual(misplaced_op_map[self.banana_op_1], self.date_op_1)
        self.assertIn(misplaced_op_map[self.banana_op_2], (self.cherry_op_1, self.date_op_2))  # either cherry or date, since both have a match and the content is identical

        self.assertIsInstance(miss_op_list, list)
        self.assertEqual(len(miss_op_list), 1)
        self.assertEqual(miss_op_list[0], self.elderberry_op_1)
        
    def test_comparator_compare_operations_equal(self):
        op_match_map, misplaced_op_map, miss_op_list = ClassComperator.compare_operations(self.inst_op_list, self.inst_op_list, self.match_map_id, self.match_map_id, self.grade_model)
        self.assertIsInstance(op_match_map, dict)
        self.assertEqual(len(op_match_map), 5)
        self.assertIsInstance(misplaced_op_map, dict)
        self.assertEqual(len(misplaced_op_map), 0)
        self.assertIsInstance(miss_op_list, list)
        self.assertEqual(len(miss_op_list), 0)
        self.assertEqual(op_match_map[self.apple_op_1], self.apple_op_1)
        self.assertEqual(op_match_map[self.apple_op_2], self.apple_op_2)
        self.assertEqual(op_match_map[self.banana_op_1], self.banana_op_1)
        self.assertEqual(op_match_map[self.banana_op_2], self.banana_op_2)
        self.assertEqual(op_match_map[self.elderberry_op_1], self.elderberry_op_1)

    def test_comparator_compare_operations_different(self):
        op_match_map, misplaced_op_map, miss_op_list = ClassComperator.compare_operations(self.inst_op_list, self.student_op_list, self.true_class_matches, self.revered_true_class_matches, self.grade_model)
        self.assertIsInstance(op_match_map, dict)
        self.assertEqual(len(op_match_map), 2)
        self.assertEqual(op_match_map[self.apple_op_1], self.apples_op_1)
        self.assertEqual(op_match_map[self.apple_op_2], self.apples_op_2)

        self.assertIsInstance(misplaced_op_map, dict)
        self.assertEqual(len(misplaced_op_map), 2)
        self.assertIn(misplaced_op_map[self.banana_op_1], (self.date_op_1, self.cherry_op_1))  # either date or cherry, since both have a match and the content is identical
        self.assertEqual(misplaced_op_map[self.banana_op_2], self.date_op_2)

        self.assertIsInstance(miss_op_list, list)
        self.assertEqual(len(miss_op_list), 1)
        self.assertEqual(miss_op_list[0], self.elderberry_op_1)

    # tests for compare content (combines attributes and operations)
    def test_comparator_compare_content_empty(self):
        student_model = UMLModel("@startuml\n@enduml")
        instructor_model = UMLModel("@startuml\n@enduml")
        result = ClassComperator.compare_content(instructor_model, student_model, {}, self.grade_model)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 6)
        self.assertIsInstance(result[0], dict)
        self.assertEqual(len(result[0]), 0)
        self.assertIsInstance(result[1], dict)
        self.assertEqual(len(result[1]), 0)
        self.assertIsInstance(result[2], list)
        self.assertEqual(len(result[2]), 0)
        self.assertIsInstance(result[3], dict)
        self.assertEqual(len(result[3]), 0)
        self.assertIsInstance(result[4], dict)
        self.assertEqual(len(result[4]), 0)
        self.assertIsInstance(result[5], list)
        self.assertEqual(len(result[5]), 0)

    def test_comparator_compare_content_instructor_empty(self):
        instructor_model = UMLModel("@startuml\n@enduml")
        result = ClassComperator.compare_content(instructor_model, self.student_model, self.true_class_matches, self.grade_model)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 6)
        self.assertIsInstance(result[0], dict)
        self.assertEqual(len(result[0]), 0)
        self.assertIsInstance(result[1], dict)
        self.assertEqual(len(result[1]), 0)
        self.assertIsInstance(result[2], list)
        self.assertEqual(len(result[2]), 0)
        self.assertIsInstance(result[3], dict)
        self.assertEqual(len(result[3]), 0)
        self.assertIsInstance(result[4], dict)
        self.assertEqual(len(result[4]), 0)
        self.assertIsInstance(result[5], list)
        self.assertEqual(len(result[5]), 0)

    def test_comparator_compare_content_student_empty(self):
        student_model = UMLModel("@startuml\n@enduml")
        attr_match_map, misplaced_attr_map, miss_attr_list, oper_matched_map, misplaced_oper_map, miss_oper_list = ClassComperator.compare_content(self.instructor_model, student_model, self.true_class_matches, self.grade_model)
        self.assertIsInstance(attr_match_map, dict)
        self.assertEqual(len(attr_match_map), 0)
        self.assertIsInstance(misplaced_attr_map, dict)
        self.assertEqual(len(misplaced_attr_map), 0)
        self.assertIsInstance(miss_attr_list, list)
        self.assertEqual(len(miss_attr_list), 5)
        self.assertEqual(miss_attr_list[0], self.apple_attr_1)
        self.assertEqual(miss_attr_list[1], self.apple_attr_2)
        self.assertEqual(miss_attr_list[2], self.banana_attr_1)
        self.assertEqual(miss_attr_list[3], self.banana_attr_2)
        self.assertEqual(miss_attr_list[4], self.elderberry_attr_1)

        self.assertIsInstance(oper_matched_map, dict)
        self.assertEqual(len(oper_matched_map), 0)
        self.assertIsInstance(misplaced_oper_map, dict)
        self.assertEqual(len(misplaced_oper_map), 0)
        self.assertIsInstance(miss_oper_list, list)
        self.assertEqual(len(miss_oper_list), 5)
        self.assertEqual(miss_oper_list[0], self.apple_op_1)
        self.assertEqual(miss_oper_list[1], self.apple_op_2)
        self.assertEqual(miss_oper_list[2], self.banana_op_1)
        self.assertEqual(miss_oper_list[3], self.banana_op_2)
        self.assertEqual(miss_oper_list[4], self.elderberry_op_1)

    def test_comparator_compare_content_equal(self):
        attr_match_map, misplaced_attr_map, miss_attr_list, oper_matched_map, misplaced_oper_map, miss_oper_list = ClassComperator.compare_content(self.instructor_model, self.instructor_model, self.match_map_id, self.grade_model)
        self.assertIsInstance(attr_match_map, dict)
        self.assertEqual(len(attr_match_map), 5)
        self.assertEqual(attr_match_map[self.apple_attr_1], self.apple_attr_1)
        self.assertEqual(attr_match_map[self.apple_attr_2], self.apple_attr_2)
        self.assertEqual(attr_match_map[self.banana_attr_1], self.banana_attr_1)
        self.assertEqual(attr_match_map[self.banana_attr_2], self.banana_attr_2)
        self.assertEqual(attr_match_map[self.elderberry_attr_1], self.elderberry_attr_1)

        self.assertIsInstance(misplaced_attr_map, dict)
        self.assertEqual(len(misplaced_attr_map), 0)

        self.assertIsInstance(miss_attr_list, list)
        self.assertEqual(len(miss_attr_list), 0)

        self.assertIsInstance(oper_matched_map, dict)
        self.assertEqual(len(oper_matched_map), 5)
        self.assertEqual(oper_matched_map[self.apple_op_1], self.apple_op_1)
        self.assertEqual(oper_matched_map[self.apple_op_2], self.apple_op_2)
        self.assertEqual(oper_matched_map[self.banana_op_1], self.banana_op_1)
        self.assertEqual(oper_matched_map[self.banana_op_2], self.banana_op_2)
        self.assertEqual(oper_matched_map[self.elderberry_op_1], self.elderberry_op_1)

        self.assertIsInstance(misplaced_oper_map, dict)
        self.assertEqual(len(misplaced_oper_map), 0)

        self.assertIsInstance(miss_oper_list, list)
        self.assertEqual(len(miss_oper_list), 0)

    def test_comparator_compare_content_different(self):
        attr_match_map, misplaced_attr_map, miss_attr_list, oper_matched_map, misplaced_oper_map, miss_oper_list = ClassComperator.compare_content(self.instructor_model, self.student_model, self.true_class_matches, self.grade_model)
        self.assertIsInstance(attr_match_map, dict)
        self.assertEqual(len(attr_match_map), 2)
        self.assertEqual(attr_match_map[self.apple_attr_1], self.apples_attr_1)
        self.assertEqual(attr_match_map[self.apple_attr_2], self.apples_attr_2)

        self.assertIsInstance(misplaced_attr_map, dict)
        self.assertEqual(len(misplaced_attr_map), 2)
        self.assertIn(misplaced_attr_map[self.banana_attr_1], (self.cherry_attr_1, self.date_attr_1))
        self.assertEqual(misplaced_attr_map[self.banana_attr_2], self.date_attr_2)

        self.assertIsInstance(miss_attr_list, list)
        self.assertEqual(len(miss_attr_list), 1)
        self.assertEqual(miss_attr_list[0], self.elderberry_attr_1)

        self.assertIsInstance(oper_matched_map, dict)
        self.assertEqual(len(oper_matched_map), 2)
        self.assertEqual(oper_matched_map[self.apple_op_1], self.apples_op_1)
        self.assertEqual(oper_matched_map[self.apple_op_2], self.apples_op_2)

        self.assertIsInstance(misplaced_oper_map, dict)
        self.assertEqual(len(misplaced_oper_map), 2)
        self.assertIn(misplaced_oper_map[self.banana_op_1], (self.cherry_op_1, self.date_op_1))
        self.assertEqual(misplaced_oper_map[self.banana_op_2], self.date_op_2)

        self.assertIsInstance(miss_oper_list, list)
        self.assertEqual(len(miss_oper_list), 1)
        self.assertEqual(miss_oper_list[0], self.elderberry_op_1)
