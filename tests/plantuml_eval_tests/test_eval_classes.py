from plantuml_eval.eval_classes import ClassComperator
from UML_model.uml_model import UMLModel
from UML_model.uml_class import UMLClass
from grading.grade_metamodel import GradeModel
import unittest


class TestClassComperator(unittest.TestCase):
    def setUp(self):
        self.instructor_model = """
        @startuml
        class Apple {
            +color: String
            -taste: double
        }
        class Banana {
            +length: int
            ripeness
            +peel(percentage: int)
        }
        class Cherry
        class Date
        class Elderberry 

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
        }
        class Apple {
            +color: String
        }
        class BitterMelon 
        class Cherry {
            +size: int
        }
        class Date {
            +length: int
            ripeness
            +peel(percentage: int)
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
        self.grade_model = GradeModel(self.instructor_model)
        
        self.grade_model.add_class_grade_structure("apple", 1.0, 1.0)
        self.grade_model.add_class_grade_structure("banana", 1.0, 1.0, 1.0)
        self.grade_model.add_class_grade_structure("cherry", 1.0)
        self.grade_model.add_class_grade_structure("date", 1.0)
        self.grade_model.add_class_grade_structure("elderberry", 1.0)

        # initializing test classes
        self.apple = self.instructor_model.class_lookup["apple"]
        self.banana = self.instructor_model.class_lookup["banana"]
        self.cherry = self.instructor_model.class_lookup["cherry"]
        self.date = self.instructor_model.class_lookup["date"]
        self.elderberry = self.instructor_model.class_lookup["elderberry"]

        # setting up possible matches
        # NOTE: this has nothing to do with the actual mapping, its just an example for the test
        self.possible_matches = {self.apple: [self.apple, self.banana],
                                self.banana: [self.cherry, self.banana],
                                self.cherry: [self.cherry],
                                self.date: [self.date],
                                self.elderberry: []}
        
    def test_comperator_get_safe_matches(self):
        safe_matches = ClassComperator.get_safe_matches(self.possible_matches)
        self.assertIsInstance(safe_matches, dict)
        self.assertEqual(len(safe_matches), 1)
        self.assertEqual(self.date, list(safe_matches.keys())[0])

    # NOTE: does not need to be tested with empty possible matches, as it will not be called in that case

    def test_comperator_find_best_class_match_assignment_without_gm(self):
        # This test is for the case where no grade model is provided
        # it shows what problems can occur if no grade model is provided
        best_match = ClassComperator.find_best_class_match_assignment(self.possible_matches)

        self.assertIsInstance(best_match, dict)
        self.assertEqual(len(best_match), 4)
        self.assertEqual(best_match[self.apple], self.apple)
        self.assertEqual(best_match[self.banana], self.cherry)
        self.assertEqual(best_match[self.cherry], self.cherry)
        self.assertEqual(best_match[self.date], self.date)

    def test_comperator_find_best_class_match_assignment_with_gm(self):
        best_match = ClassComperator.find_best_class_match_assignment(self.possible_matches, self.grade_model)

        self.assertIsInstance(best_match, dict)
        self.assertEqual(len(best_match), 4)
        self.assertEqual(best_match[self.apple], self.apple)
        self.assertEqual(best_match[self.banana], self.banana)
        self.assertEqual(best_match[self.cherry], self.cherry)
        self.assertEqual(best_match[self.date], self.date)
    
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
