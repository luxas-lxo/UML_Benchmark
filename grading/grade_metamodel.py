from UML_model.uml_model import UMLModel
from UML_model.uml_element import UMLElement
from UML_model.uml_class import UMLClass, UMLAttribute, UMLOperation
from UML_model.uml_enum import UMLEnum, UMLValue
from UML_model.uml_relation import UMLRelation
from grading.grade_reference import GradeReference
from tools.syntactic_check import SyntacticCheck
from tools.semantic_check import SemanticCheck

from typing import List, Dict, Tuple, Optional, Union
from enum import Enum
import logging

logger = logging.getLogger("grade_metamodel")
logger.setLevel(logging.DEBUG)

if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(levelname)s] - %(name)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

class FeatureType(Enum):
    # NOTE: add more types as needed
    CLASS = "class"
    ATTRIBUTE = "attribute"
    OPERATION = "operation"

    ENUM = "enum"
    VALUE = "value"

    RELATION = "relation"
    RELATION_STRUCTURE = "relation structure"

    UNKNOWN = "unknown"

class StructuralFeature:
    def __init__(self, description: str, reference: GradeReference, points: float, type: Optional[FeatureType] = None):
        self.description = description
        self.points = points
        if type is None:
            reference_type_map = {
                UMLClass: FeatureType.CLASS,
                UMLAttribute: FeatureType.ATTRIBUTE,
                UMLOperation: FeatureType.OPERATION,
                UMLEnum: FeatureType.ENUM,
                UMLValue: FeatureType.VALUE,
                UMLRelation: FeatureType.RELATION,
            }

            for ref_type, feature_type in reference_type_map.items():
                if isinstance(reference, ref_type):
                    self.type = feature_type
                    self.reference = reference
                    break
            else:
                self.type = FeatureType.UNKNOWN
                self.reference = reference
        else:
            self.type = type
            self.reference = reference


    def __repr__(self):
        return f"StructuralFeature(desc: {self.description}, {self.points} point/s)"
    
    def __str__(self):
        return f"StructuralFeature({self.description})"

class GradeObject:
    def __init__(self, element: UMLElement):
        self.element = element
        self.points: float = 0
        self.st_features: List[StructuralFeature] = []

    def __repr__(self):
        return f"GradeObject({str(self.element)}): {self.points} point/s, features -> {self.st_features}"

    def __str__(self):
        return f"GradeObject({str(self.element)})"

    def set_grade(self, points: float):
        self.points = points

    def set_st_features(self, st_features: List[StructuralFeature]):
        self.st_features = st_features

class GradeModel:
    def __init__(self, name: str, uml_model: UMLModel):
        self.name = name
        self.classes: List[GradeObject] = []
        self.enums: List[GradeObject] = []
        self.relations: List[GradeObject] = []
        self.total_points: float = 0.0

        for cls in uml_model.class_list:
            self.classes.append(GradeObject(cls))
        for enm in uml_model.enum_list:
            self.enums.append(GradeObject(enm))
        for rel in uml_model.relation_list:
            self.relations.append(GradeObject(rel))
        
        # mostly for access in add-structure methods
        self.class_lookup: Dict[str, GradeObject] = {cls.element: cls for cls in self.classes}
        self.enum_lookup: Dict[str, GradeObject] = {enm.element: enm for enm in self.enums}
        self.relation_lookup: Dict[str, GradeObject] = {rel.element: rel for rel in self.relations}


    def __repr__(self):
        return (
            f"GradeModel({self.name})\n"
            f"Class-GradeObjects: {[str(cls) for cls in self.classes]}: {[f'{cls.points:.1f}' for cls in self.classes]}\n"
            f"Enum-GradeObjects: {[str(enm) for enm in self.enums]}: {[f'{enm.points:.1f}' for enm in self.enums]}\n"
            f"Relation-GradeObjects: {[str(rel) for rel in self.relations]}: {[f'{rel.points:.1f}' for rel in self.relations]}\n"
            f"Total Points: {self.total_points:.1f}"
        )

    def __str__(self):
        return f"GradeModel({self.name})"

    def add_class_grade_structure(self, cls: UMLClass, exists_points: float = 0.0, attribute_points: float = 0.0, operation_points: float = 0.0):
        grade_class = self.class_lookup.get(cls)
        if not grade_class:
            raise ValueError(f"Class '{cls.name}' not found in model.")
        
        grade_class.st_features.append(StructuralFeature(f"class \"{cls.name}\"", grade_class.element, exists_points))
        grade_class.points += exists_points
        self.total_points += exists_points

        for att in grade_class.element.attributes:
            grade_class.st_features.append(StructuralFeature(f"attribute \"{att.name}\"", att, attribute_points))
            grade_class.points += attribute_points
            self.total_points += attribute_points

        for opr in grade_class.element.operations:
            grade_class.st_features.append(StructuralFeature(f"operation \"{opr.name}\"", opr, operation_points))
            grade_class.points += operation_points
            self.total_points += operation_points

    def add_enum_grade_structure(self, enm: UMLEnum, exists_points: float = 0.0, all_value_points: float = 0.0):
        grade_enum = self.enum_lookup.get(enm)
        if not grade_enum:
            raise ValueError(f"Enum '{enm.name}' not found in model.")
        
        grade_enum.st_features.append(StructuralFeature(f"enum \"{enm.name}\"", grade_enum.element, exists_points))
        grade_enum.points += exists_points
        self.total_points += exists_points
        value_points: float = all_value_points / len(grade_enum.element.values) if grade_enum.element.values else 0.0

        for val in grade_enum.element.values:
            grade_enum.st_features.append(StructuralFeature(f"value \"{val.name}\"", val, value_points))
            grade_enum.points += value_points
            self.total_points += value_points

    def add_relation_grade_structure(self, rel: UMLRelation, exists_points: float = 0.0, relation_structure_points: float = 0.0):
        grade_relation = self.relation_lookup.get(rel)
        if not grade_relation:
            raise ValueError(f"Relation '{rel.name}' not found in model.")
        
        grade_relation.st_features.append(StructuralFeature(f"relation \"{rel.name}\"", grade_relation.element, exists_points))
        grade_relation.points += exists_points
        self.total_points += exists_points

        grade_relation.st_features.append(StructuralFeature(f"relation structure {rel.to_plantuml()}", rel, relation_structure_points, FeatureType.RELATION_STRUCTURE))
        grade_relation.points += relation_structure_points
        self.total_points += relation_structure_points

    def grade_attribute(self, st_feature: StructuralFeature, att: UMLAttribute, class_match_map: Optional[Dict[UMLClass, UMLClass]] = None) -> float:
        # attribute found -> 1/2 points
        temp_grade: float = st_feature.points / 2
        temp_content_grade: float = 0.0
        content_check: Dict[str, bool] = st_feature.reference.compare_content_to_student(att)
        for _, checked in content_check.items():
            if checked:
                # structural match for e.g data type == data type
                temp_content_grade += 1
        # structural match normalized -> 1/2 points
        if class_match_map:
            # checks for the class of the attribute in addition to the attribute itself
            # this is expressed throug the +1, +1/2, +1/4 in the grade calculation
            if class_match_map.get(st_feature.reference.reference) == att.reference:
                temp_grade += (temp_content_grade + 1 / (len(content_check) + 1)) * (st_feature.points / 2)
            elif att.reference.sub_classes and class_match_map.get(st_feature.reference.reference) in att.reference.sub_classes:
                temp_grade += ((temp_content_grade + 1/2) / (len(content_check) + 1)) * (st_feature.points / 2)
            elif att.reference.sub_classes:
                for sub_cls in att.reference.sub_classes:
                    if sub_cls.sub_classes and class_match_map.get(st_feature.reference.reference) in sub_cls.sub_classes:
                        temp_grade += ((temp_content_grade + 1/4) / (len(content_check) + 1)) * (st_feature.points / 2)
                        break
            else:
                temp_grade += (temp_content_grade / (len(content_check) + 1)) * (st_feature.points / 2)
        else:
            temp_grade += (temp_content_grade / len(content_check)) * (st_feature.points / 2)
        logger.debug(f"Grade for attribute '{att.name}': {temp_grade} (content match: {temp_content_grade} / {len(content_check)})")
        return temp_grade
    
    def grade_operation(self, st_feature: StructuralFeature, opr: UMLOperation, class_match_map: Optional[Dict[UMLClass, UMLClass]] = None) -> float:
        # operation found -> 1/2 points
        temp_grade: float = st_feature.points / 2
        temp_content_grade: float = 0.0
        content_check: Dict[str, bool] = st_feature.reference.compare_content_to_student(opr)
        for _, checked in content_check.items():
            if checked:
                # structural match for e.g parameter == parameter
                temp_content_grade += 1
        # structural match normalized -> 1/2 points
        if class_match_map:
            if class_match_map.get(st_feature.reference.reference) == opr.reference:
                temp_grade += (temp_content_grade + 1 / (len(content_check) + 1)) * (st_feature.points / 2)
            elif opr.reference.sub_classes and class_match_map.get(st_feature.reference.reference) in opr.reference.sub_classes:
                temp_grade += ((temp_content_grade + 1/2) / (len(content_check) + 1)) * (st_feature.points / 2)
            elif opr.reference.sub_classes:
                for sub_cls in opr.reference.sub_classes:
                    if sub_cls.sub_classes and class_match_map.get(st_feature.reference.reference) in sub_cls.sub_classes:
                        temp_grade += ((temp_content_grade + 1/4) / (len(content_check) + 1)) * (st_feature.points / 2)
                        break
            else:
                temp_grade += ((temp_content_grade) / (len(content_check) + 1)) * (st_feature.points / 2)
        else:
            temp_grade += (temp_content_grade / len(content_check)) * (st_feature.points / 2)
        logger.debug(f"Grade for operation '{opr.name}': {temp_grade} (content match: {temp_content_grade} / {len(content_check)})")
        return temp_grade

    def grade_relation(self, st_feature: StructuralFeature, rel: UMLRelation, element_match_map: Dict[Union[UMLClass, UMLEnum], Union[UMLClass, UMLEnum]]) -> float:
        # relation found -> points
        temp_content_grade: float = 0.0
        content_check: Dict[str, bool] = st_feature.reference.compare_content_to_student(rel)
        for _, checked in content_check.items():
            if checked:
                # structural match for e.g source == source and destination == destination
                temp_content_grade += 1
        # structural match normalized -> points
        temp_grade += (temp_content_grade / len(content_check)) * st_feature.points
        logger.debug(f"Grade for relation '{rel.name}': {temp_grade} (content match: {temp_content_grade} / {len(content_check)})")
        return temp_grade

    def temp_grade_st_element(self, st_feature: StructuralFeature, stud_class_element_list: Optional[List[GradeReference]] = None, stud_element: Optional[UMLElement] = None, class_match_map: Optional[Dict[UMLClass, UMLClass]] = None) -> float:
        temp_grade: float = 0.0
        if stud_class_element_list:
            all_temp_grades: List[float] = []
            for element in stud_class_element_list:
                if st_feature.reference.name == element.name or SyntacticCheck.syntactic_match(element.name, st_feature.reference.name)[0] or SemanticCheck.semantic_match(element.name, st_feature.reference.name)[0]:
                    if isinstance(element, UMLAttribute):
                        all_temp_grades.append(self.grade_attribute(st_feature, element))
                    elif isinstance(element, UMLOperation):
                        all_temp_grades.append(self.grade_operation(st_feature, element))
                    else:
                        logger.warning(f"Unsupported element type for grading: {type(element)}")
            temp_grade = max(all_temp_grades) if all_temp_grades else 0.0
        elif stud_element:
            if isinstance(stud_element, UMLAttribute):
                temp_grade += self.grade_attribute(st_feature, stud_element, class_match_map)
            elif isinstance(stud_element, UMLOperation):
                temp_grade += self.grade_operation(st_feature, stud_element, class_match_map)
            else:
                logger.warning(f"Unsupported element type for grading: {type(stud_element)}")
        return temp_grade

    def temp_grade_class(self, stud_class: UMLClass, mapped_inst_class: UMLClass) -> Tuple[float, float]:
        temp_grade: float = 0.0
        grade_class: GradeObject = next((cls for cls in self.classes if cls.element == mapped_inst_class), None)
        if not grade_class:
            raise ValueError(f"Class '{mapped_inst_class.name}' not found in model.")
        for st_feature in grade_class.st_features:
            if st_feature.type == FeatureType.CLASS:
                # class exists -> points
                temp_grade += st_feature.points / 2
                if st_feature.reference.name == stud_class.name or SyntacticCheck.syntactic_match(stud_class.name, st_feature.reference.name)[0] or SemanticCheck.semantic_match(stud_class.name, st_feature.reference.name)[0]:
                    # name match -> 1/2 points
                    temp_grade += st_feature.points / 2
            elif st_feature.type == FeatureType.ATTRIBUTE:
                temp_grade += self.temp_grade_st_element(st_feature, stud_class.attributes)
            elif st_feature.type == FeatureType.OPERATION:
                temp_grade += self.temp_grade_st_element(st_feature, stud_class.operations)
            else:
                return NotImplemented
        return (temp_grade / grade_class.points if grade_class.points > 0 else 0.0, temp_grade)
    
    def temp_grade_class_content(self, stud_content: GradeReference, mapped_inst_content: GradeReference, class_match_map: Optional[Dict[UMLClass, UMLClass]] = None) -> Tuple[float, float]:
        temp_grade: float = 0.0
        grade_class: GradeObject = next((cls for cls in self.classes if cls.element == mapped_inst_content.reference), None)
        if not grade_class:
            raise ValueError(f"Class '{mapped_inst_content.reference.name}' of {str(mapped_inst_content)} not found in model.")
        if isinstance(mapped_inst_content, UMLAttribute):
            # attribute content grading
            for st_feature in grade_class.st_features:
                if st_feature.type == FeatureType.ATTRIBUTE and st_feature.reference == mapped_inst_content:
                    temp_grade += self.temp_grade_st_element(st_feature=st_feature, stud_element=stud_content, class_match_map=class_match_map)
                    break
        elif isinstance(mapped_inst_content, UMLOperation):
            # operation content grading
            for st_feature in grade_class.st_features:
                if st_feature.type == FeatureType.OPERATION and st_feature.reference == mapped_inst_content:
                    temp_grade += self.temp_grade_st_element(st_feature=st_feature, stud_element=stud_content, class_match_map=class_match_map)
                    break
        return (temp_grade / st_feature.points if st_feature.points > 0 else 0.0, temp_grade)
    
    def temp_grade_enum(self, stud_enum: UMLEnum, mapped_inst_enum: UMLEnum) -> Tuple[float, float]:
        temp_grade: float = 0.0
        grade_enum: GradeObject = next((enm for enm in self.enums if enm.element == mapped_inst_enum), None)
        if not grade_enum:
            raise ValueError(f"Enum '{mapped_inst_enum.name}' not found in model.")
        for st_feature in grade_enum.st_features:
            if st_feature.type == FeatureType.ENUM:
                # enum exists -> points
                temp_grade += st_feature.points / 2
                if st_feature.reference.name == stud_enum.name or SyntacticCheck.syntactic_match(stud_enum.name, st_feature.reference.name)[0] or SemanticCheck.semantic_match(stud_enum.name, st_feature.reference.name)[0]:
                    # name match -> 1/2 points
                    temp_grade += st_feature.points / 2
            elif st_feature.type == FeatureType.VALUE:
                if any(v == st_feature.reference.name for v in stud_enum.values) or any(SyntacticCheck.syntactic_match(v.name, st_feature.reference.name)[0] for v in stud_enum.values) or any(SemanticCheck.semantic_match(v.name, st_feature.reference.name)[0] for v in stud_enum.values):
                    # name match -> points
                    temp_grade += st_feature.points 
        return temp_grade / grade_enum.points if grade_enum.points > 0 else 0.0, temp_grade

    def temp_grade_relation(self, stud_relation: UMLRelation, mapped_inst_relation: UMLRelation, element_match_map: Dict[Union[UMLClass, UMLEnum], Union[UMLClass, UMLEnum]]) -> Tuple[float, float]:
        temp_grade: float = 0.0
        grade_relation: GradeObject = next((rel for rel in self.relations if rel.element == mapped_inst_relation), None)
        if not grade_relation:
            raise ValueError(f"Relation '{mapped_inst_relation.name}' not found in model.")
        for st_feature in grade_relation.st_features:
            if st_feature.type == FeatureType.RELATION:
                # relation exists -> points 
                temp_grade += st_feature.points 
            elif st_feature.type == FeatureType.RELATION_STRUCTURE:
                # relation structure match -> points
                temp_grade += GradeModel.grade_relation(st_feature, stud_relation, element_match_map)
        return temp_grade / grade_relation.points if grade_relation.points > 0 else 0.0, temp_grade
    
    def temp_grade_value(self, stud_value: UMLValue, mapped_inst_value: UMLValue) -> Tuple[float, float]:
        temp_grade: float = 0.0
        grade_enum: GradeObject = next((enm for enm in self.enums if enm.element == mapped_inst_value.reference), None)
        if not grade_enum:
            raise ValueError(f"Enum '{mapped_inst_value.reference.name}' not found in model.")
        for st_feature in grade_enum.st_features:
            if st_feature.type == FeatureType.VALUE and st_feature.reference == mapped_inst_value:
                # NOTE: here only the name can be checked, as the value itself is not a complex object
                # so we decided to give syntactic matches more weight than semantic matches
                syn_res = SyntacticCheck.syntactic_match(stud_value.name, st_feature.reference.name)
                sem_res = SemanticCheck.semantic_match(stud_value.name, st_feature.reference.name)
                if syn_res[0]:
                    temp_grade += st_feature.points * syn_res[1] * 3/5
                if sem_res[0]:
                    temp_grade += st_feature.points * sem_res[1] * 2/5
                break
        return temp_grade / st_feature.points if grade_enum.points > 0 else 0.0, temp_grade