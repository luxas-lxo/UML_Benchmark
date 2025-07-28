from UML_model.uml_model import UMLModel
from UML_model.uml_class import UMLClass, UMLAttribute, UMLOperation
from UML_model.uml_enum import UMLEnum, UMLValue
from UML_model.uml_relation import UMLRelation, UMLRelationType
from plantuml_eval.eval_classes import ClassComperator
from plantuml_eval.eval_relations import RelationComperator
from plantuml_eval.eval_enums import EnumComperator
from grading.grade_metamodel import GradeModel

from typing import Optional, Dict, List, Tuple, Union
import logging

logger = logging.getLogger("eval_model")
logger.setLevel(logging.DEBUG)

if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(levelname)s] - %(name)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

class EvalModel:
    def __init__(self, inst_model: UMLModel, stud_model: UMLModel, grade_model: Optional[GradeModel] = None):
        self.instructor_model: UMLModel = inst_model
        self.student_model: UMLModel = stud_model
        self.grade_model: Optional[GradeModel] = grade_model

        # Algorithm 1: Compare classes in InstructorModel and StudentModel
        compare_classes = ClassComperator.compare_classes(self.instructor_model, self.student_model, self.grade_model)
        self.class_match_map: Dict[UMLClass, UMLClass] = compare_classes[0]
        self.class_match_map_str: Dict[str, str] = {str(k): str(v) for k, v in self.class_match_map.items()}
        self.missing_classes: List[UMLClass] = compare_classes[1]
        self.missing_classes_str: List[str] = [str(cls) for cls in self.missing_classes]

        # Algorithm 2: Compare class content in InstructorModel and StudentModel
        compare_class_content = ClassComperator.compare_class_content(self.instructor_model, self.student_model, self.class_match_map, self.grade_model)

        self.attr_match_map: Dict[UMLAttribute, UMLAttribute] = compare_class_content[0]
        self.attr_match_map_str: Dict[str, str] = {str(k): str(v) for k, v in self.attr_match_map.items()}
        self.inherited_attr_map: Dict[UMLAttribute, UMLAttribute] = compare_class_content[1]
        self.inherited_attr_map_str: Dict[str, str] = {str(k): str(v) for k, v in self.inherited_attr_map.items()}
        self.misplaced_attr_map: Dict[UMLAttribute, UMLAttribute] = compare_class_content[2]
        self.misplaced_attr_map_str: Dict[str, str] = {str(k): str(v) for k, v in self.misplaced_attr_map.items()}
        self.missed_attr_list: List[UMLAttribute] = compare_class_content[3]
        self.missed_attr_list_str: List[str] = [f"{str(attr)}" for attr in self.missed_attr_list]

        # **adeded additionally**
        self.temp_all_att_matches: Dict[UMLAttribute, UMLAttribute] = {**self.attr_match_map, **self.inherited_attr_map, **self.misplaced_attr_map}

        self.oper_matched_map: Dict[UMLOperation, UMLOperation] = compare_class_content[4]
        self.oper_matched_map_str: Dict[str, str] = {str(k): str(v) for k, v in self.oper_matched_map.items()}
        self.inherited_oper_map: Dict[UMLOperation, UMLOperation] = compare_class_content[5]
        self.inherited_oper_map_str: Dict[str, str] = {str(k): str(v) for k, v in self.inherited_oper_map.items()}
        self.misplaced_oper_map: Dict[UMLOperation, UMLOperation] = compare_class_content[6]
        self.misplaced_oper_map_str: Dict[str, str] = {str(k): str(v) for k, v in self.misplaced_oper_map.items()}
        self.missed_oper_list: List[UMLOperation] = compare_class_content[7]
        self.missed_oper_list_str: List[str] = [f"{str(op)}" for op in self.missed_oper_list]

        # **adeded additionally**
        self.temp_all_oper_matches: Dict[UMLOperation, UMLOperation] = {**self.oper_matched_map, **self.inherited_oper_map, **self.misplaced_oper_map}

        # Algorithm 3: Find split classes in InstructorModel and StudentModel
        self.split_class_map: Dict[UMLClass, Tuple[UMLClass, UMLClass]] = ClassComperator.class_split_match(self.instructor_model, self.student_model, self.attr_match_map ,self.inherited_attr_map, self.misplaced_attr_map, self.oper_matched_map, self.inherited_oper_map, self.misplaced_oper_map)
        self.split_class_map_str: Dict[str, str] = {str(k): str(v) for k, v in self.split_class_map.items()}

        # Algorithm 4: Find merged classes in InstructorModel and StudentModel
        self.merge_class_map: Dict[Tuple[UMLClass, UMLClass], UMLClass] = ClassComperator.class_merge_match(self.instructor_model, self.class_match_map, self.misplaced_attr_map, self.misplaced_oper_map)
        self.merge_class_map_str: Dict[Tuple[str, str], str] = {(str(k[0]), str(k[1])): str(v) for k, v in self.merge_class_map.items()}

        # **adeded additionally**
        # NOTE: maybe update the missing list in Algorithm 3 and 4
        self.temp_missing_classes: List[UMLClass] = [
            cls for cls in self.missing_classes
            if (
                cls not in self.split_class_map.keys() and
                not any(
                    cls == merge_cls_1 or cls == merge_cls_2
                    for merge_cls_1, merge_cls_2 in self.merge_class_map.keys()
                )
            )
        ]
        
        # Algorithm 6: Compare ENUM in InstructorModel and StudentModel
        compare_enums = EnumComperator.compare_enums(self.instructor_model, self.student_model, self.grade_model)
        self.enum_match_map: Dict[UMLEnum, UMLEnum] = compare_enums[0]
        self.enum_match_map_str: Dict[str, str] = {str(k): str(v) for k, v in self.enum_match_map.items()}
        self.missing_enums: List[UMLEnum] = compare_enums[1]
        self.missing_enums_str: List[str] = [str(enum) for enum in self.missing_enums]

        # NOTE: those are excluded from the evaluation
        self.possible_misplaced_values: Dict[UMLValue, Union[UMLAttribute, UMLClass]] = compare_enums[2]
        self.possible_misplaced_values_str: Dict[str, str] = {str(k): str(v) for k, v in self.possible_misplaced_values.items()}

        # NOTE: these are added additionally
        self.value_match_map: Dict[UMLValue, UMLValue] = compare_enums[3]
        self.value_match_map_str: Dict[str, str] = {str(k): str(v) for k, v in self.value_match_map.items()}
        self.misplaced_value_map: Dict[UMLValue, UMLValue] = compare_enums[4]
        self.misplaced_value_map_str: Dict[str, str] = {str(k): str(v) for k, v in self.misplaced_value_map.items()}
        self.missed_value_list: List[UMLValue] = compare_enums[5]
        self.missed_value_list_str: List[str] = [f"{str(value)} in {str(value.reference)}" for value in self.missed_value_list]

        # **adeded additionally**
        self.temp_all_value_matches: Dict[UMLValue, UMLValue] = {**self.value_match_map, **self.misplaced_value_map}

        # Algorithm 5: Compare association in InstructorModel and StudentModel
        compare_relations = RelationComperator.compare_relations(self.instructor_model, self.student_model, self.class_match_map, self.missing_classes, self.enum_match_map, self.missing_enums)
        self.relation_match_map: Dict[UMLRelation, UMLRelation] = compare_relations[0]
        self.relation_match_map_str: Dict[str, str] = {str(k): str(v) for k, v in self.relation_match_map.items()}
        self.inst_assoc_link_match_map: Dict[UMLRelation, Tuple[UMLRelation, UMLRelation]] = compare_relations[1]
        self.inst_assoc_link_match_map_str: Dict[str, Tuple[str, str]] = {str(k): (str(v[0]), str(v[1])) for k, v in self.inst_assoc_link_match_map.items()}
        self.stud_assoc_link_match_map: Dict[Tuple[UMLRelation, UMLRelation], UMLRelation] = compare_relations[2]
        self.stud_assoc_link_match_map_str: Dict[Tuple[str, str], str] = {(str(k[0]), str(k[1])): str(v) for k, v in self.stud_assoc_link_match_map.items()}
        self.sec_derivation_inst_map: Dict[Tuple[UMLRelation, UMLRelation], UMLRelation] = compare_relations[3]
        self.sec_derivation_inst_map_str: Dict[Tuple[str, str], str] = {(str(k[0]), str(k[1])): str(v) for k, v in self.sec_derivation_inst_map.items()}
        self.sec_derivation_stud_map: Dict[UMLRelation, Tuple[UMLRelation, UMLRelation]] = compare_relations[4]
        self.sec_derivation_stud_map_str: Dict[str, Tuple[str, str]] = {str(k): (str(v[0]), str(v[1])) for k, v in self.sec_derivation_stud_map.items()}
        self.miss_relation_list: List[UMLRelation] = compare_relations[5]
        self.miss_relation_list_str: List[str] = [str(rel) for rel in self.miss_relation_list]
        self.miss_relation_list_loose: List[UMLRelation] = compare_relations[6]
        self.miss_relation_list_loose_str: List[str] = [str(rel) for rel in self.miss_relation_list_loose]

        # build the student model based on the matches
        self.match_model: UMLModel = self.build_student_match_model()

    def print_grade_model(self):
        if self.grade_model:
            print("\nGrade Model:")
            for obj in self.grade_model.classes:
                print(f"Object({obj.element}, {obj.points}, {obj.st_features})")
            for obj in self.grade_model.enums:
                print(f"Enum({obj.element}, {obj.points}, {obj.st_features})")
        else:
            print("\nNo grade model provided.")

    def print_compare_classes(self):
        print("\nClass Matches:")
        for inst_class, stud_class in self.class_match_map.items():
            print(f"{str(inst_class)} -> {str(stud_class)}")
        print("\nMissing Classes:")
        for missing in self.missing_classes:
            print(f"Missing: {str(missing)}")

    def print_compare_class_content(self):
        print("\nAttribute Matches:")
        for inst_attr, stud_attr in self.attr_match_map.items():
            print(f"{str(inst_attr)} -> {str(stud_attr)}")
        print("\nMisplaced Attributes:")
        for inst_attr, stud_attr in self.misplaced_attr_map.items():
            print(f"{str(inst_attr)} -> {str(stud_attr)}")
        print("\nMissed Attributes:")
        for cls, attr in self.missed_attr_list:
            print(f"Missed: {str(attr)} in {str(cls)}")
        print("\nOperation Matches:")
        for inst_op, stud_op in self.oper_matched_map.items():
            print(f"{str(inst_op)} -> {str(stud_op)}")
        print("\nMisplaced Operations:")
        for inst_op, stud_op in self.misplaced_oper_map.items():
            print(f"{str(inst_op)} -> {str(stud_op)}")
        print("\nMissed Operations:")
        for cls, op in self.missed_oper_list:
            print(f"Missed: {str(op)} in {str(cls)}")

    def print_split_class_map(self):
        print("\nSplit Class Map:")
        for inst_class, stud_class in self.split_class_map.items():
            print(f"{str(inst_class)} -> {str(stud_class)}")
    
    def print_merge_class_map(self):
        print("\nMerge Class Map:")
        for inst_class, stud_class in self.merge_class_map.items():
            print(f"{str(inst_class)} -> {str(stud_class)}")

    def print_compare_enums(self):
        print("\nEnum Matches:")
        for inst_enum, stud_enum in self.enum_match_map.items():
            print(f"{str(inst_enum)} -> {str(stud_enum)}")
        print("\nMissing Enums:")
        for missing in self.missing_enums:
            print(f"Missing: {str(missing)}")
        print("\nPossible Misplaced Values:")
        for value, attr_or_class in self.possible_misplaced_values.items():
            print(f"{str(value)} -> {str(attr_or_class)}")

    def print_compare_relations(self):
        print("\nRelation Matches:")
        for inst_relation, stud_relation in self.relation_match_map.items():
            print(f"{str(inst_relation)} -> {str(stud_relation)}")
        print("\nAssociation Link Matches:")
        for inst_relation, (stud_cls_1, stud_cls_2) in self.inst_assoc_link_match_map.items():
            print(f"{str(inst_relation)} -> ({str(stud_cls_1)}, {str(stud_cls_2)})")
        for (stud_cls_1, stud_cls_2), inst_relation in self.stud_assoc_link_match_map.items():
            print(f"({str(stud_cls_1)}, {str(stud_cls_2)}) -> {str(inst_relation)}")
        print("\nDerivations:")
        for derivation, rel in self.sec_derivation_inst_map.items():
            print(f"({str(derivation[0])}, {str(derivation[1])}) -> {str(rel)}")
        for rel, derivation in self.sec_derivation_stud_map.items():
            print(f"{str(rel)} -> ({str(derivation[0])}, {str(derivation[1])})")
        print("\nMissing Relations:")
        for missing in self.miss_relation_list:
            print(f"Missing: {str(missing)}")

    def print_match_model(self):
        print("\nMatch Model:")
        print(self.match_model.to_plantuml())

    def __repr__(self):
        output = ["Evaluation Model Summary:"]
        output.append("\nInstructor Model:")
        output.append(self.instructor_model.to_plantuml())
        output.append("\nStudent Model:")
        output.append(self.student_model.to_plantuml())
        if self.grade_model:
            output.append("\nGrade Model:")
            output.append(repr(self.grade_model))

        output.append("\nAlgorithm 1: Compare Classes")
        output.append("\tClass Matches:")
        output.append(f"\t{self.class_match_map_str}")
        output.append("\tMissing Classes:")
        output.append(f"\t{self.missing_classes_str}")

        output.append("\nAlgorithm 2: Compare Class Content")
        output.append("\tAttribute Matches:")
        output.append(f"\t{self.attr_match_map_str}")
        output.append("\tInherited Attributes:")
        output.append(f"\t{self.inherited_attr_map_str}")
        output.append("\tMisplaced Attributes:")
        output.append(f"\t{self.misplaced_attr_map_str}")
        output.append("\tMissed Attributes:")
        output.append(f"\t{self.missed_attr_list_str}")
        output.append("\tOperation Matches:")
        output.append(f"\t{self.oper_matched_map_str}")
        output.append("\tInherited Operations:")
        output.append(f"\t{self.inherited_oper_map_str}")
        output.append("\tMisplaced Operations:")
        output.append(f"\t{self.misplaced_oper_map_str}")
        output.append("\tMissed Operations:")
        output.append(f"\t{self.missed_oper_list_str}")

        output.append("\nAlgorithm 3: Split Classes")
        output.append("\tSplit Class Map:")
        output.append(f"\t{self.split_class_map_str}")

        output.append("\nAlgorithm 4: Merge Classes")
        output.append("\tMerge Class Map:")
        output.append(f"\t{self.merge_class_map_str}")

        output.append("\nAlgorithm 6: Compare Enums")
        output.append("\tEnum Matches:")
        output.append(f"\t{self.enum_match_map_str}")
        output.append("\tMissing Enums:")
        output.append(f"\t{self.missing_enums_str}")
        output.append("\tValue Matches:")
        output.append(f"\t{self.value_match_map_str}")
        output.append("\tMisplaced Values:")
        output.append(f"\t{self.misplaced_value_map_str}")
        output.append("\tMissed Values:")
        output.append(f"\t{self.missed_value_list_str}")
        output.append("\tPossible Misplaced Values in classes:")
        output.append(f"\t{self.possible_misplaced_values_str}")

        output.append("\nAlgorithm 5: Compare Relations")
        output.append("\tRelation Matches:")
        output.append(f"\t{self.relation_match_map_str}")
        output.append("\tAssociation Link Matches:")
        output.append(f"\t{self.inst_assoc_link_match_map_str}")
        output.append(f"\t{self.stud_assoc_link_match_map_str}")
        output.append("\tRelation Derivations:")
        output.append(f"\t{self.sec_derivation_inst_map_str}")
        output.append(f"\t{self.sec_derivation_stud_map_str}")
        output.append("\tMissing Relations:")
        output.append(f"\t{self.miss_relation_list_str}")
        output.append("\tLoose Missing Relations:")
        output.append(f"\t{self.miss_relation_list_loose_str}")

        output.append("\nMatch Model:")
        output.append(self.match_model.to_plantuml())
        return "\n".join(output)
    
    def __str__(self):
        return "EvalModel"
    
    def build_student_match_model(self) -> UMLModel:
        student_model = self.student_model.copy()
        matched_value_set = (
            set(self.value_match_map.values())
            | set(self.misplaced_value_map.values())
        )
        matched_enum_set = (set(self.enum_match_map.values())
            | {val.reference for val in matched_value_set}
        )
        
        matched_attr_set = (
            set(self.attr_match_map.values())
            | set(self.inherited_attr_map.values())
            | set(self.misplaced_attr_map.values())
        )
        matched_oper_set = (
            set(self.oper_matched_map.values())
            | set(self.inherited_oper_map.values())
            | set(self.misplaced_oper_map.values())
        )

        matched_class_set = (
            set(self.class_match_map.values())
            | {cls for classes in self.split_class_map.values() for cls in classes}
            | set(self.merge_class_map.values())
            | {elm.reference for elm in matched_attr_set | matched_oper_set}
        )

        matched_relation_set = (
            set(self.relation_match_map.values())
            | {rel for relations in self.inst_assoc_link_match_map.values() for rel in relations}
            | set(self.stud_assoc_link_match_map.values())
            | set(self.sec_derivation_inst_map.values())
            | {rel for relations in self.sec_derivation_stud_map.values() for rel in relations}
        )
        '''
        used_relations_in_matches = {
            rel for cls in (matched_class_set | matched_enum_set) for rel in cls.relations
            if rel.destination in (matched_class_set | matched_enum_set | matched_relation_set) and rel.swap_source_destination() not in matched_relation_set
        }
        matched_relation_set.update(used_relations_in_matches)
        '''
        used_classes_in_relations = {
            cls for rel in matched_relation_set for cls in (rel.source, rel.destination)
            if isinstance(cls, UMLClass)
        }
        matched_class_set.update(used_classes_in_relations)

        used_enums_in_relations = {
            enum for rel in matched_relation_set for enum in (rel.source, rel.destination)
            if isinstance(enum, UMLEnum)
        }
        matched_enum_set.update(used_enums_in_relations)

        filtered_class_list = []
        for cls in student_model.class_list[:]:
            if cls in matched_class_set:
                cls.attributes = [attr for attr in cls.attributes if attr in matched_attr_set]
                cls.operations = [oper for oper in cls.operations if oper in matched_oper_set]
                cls.assign_content_reference()
                # NOTE: those will be reassigned later
                cls.relations = []
                cls.super_class = None
                cls.sub_classes = []
                filtered_class_list.append(cls)
        # Safely remove enums not in matched_enum_set by building a new list
        filtered_enum_list = []
        for enum in student_model.enum_list:
            if enum in matched_enum_set:
                enum.values = [value for value in enum.values if value in matched_value_set]
                enum.assign_content_reference()
                enum.relations = []
                filtered_enum_list.append(enum)
        filtered_relation_list = [rel for rel in student_model.relation_list if rel in matched_relation_set]
        return UMLModel(plantuml_str=None, class_list=filtered_class_list, enum_list=filtered_enum_list, relation_list=filtered_relation_list)

