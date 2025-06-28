from UML_model.uml_model import UMLModel
from UML_model.uml_element import UMLElement
from UML_model.uml_class import UMLClass, UMLAttribute, UMLOperation
from UML_model.uml_enum import UMLEnum, UMLValue
from UML_model.uml_relation import UMLRelation
from grading.grade_reference import GradeReference
from tools.syntactic_check import SyntacticCheck
from tools.semantic_check import SemanticCheck

from typing import List, Dict, Tuple, Optional
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
    RELATION_ELEMENTS = "relation elements"

    UNKNOWN = "unknown"

class StructuralFeature:
    def __init__(self, description: str, reference: GradeReference, points: float):
        self.description = description
        self.points = points
        
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


    def __repr__(self):
        return f"StructuralFeature(desc: {self.description}, {self.points} point/s)"

class GradeObject:
    def __init__(self, element: UMLElement):
        self.element = element
        self.points: float = 0
        self.st_features: List[StructuralFeature] = []

    def __repr__(self):
        return f"GradeObject({self.element}"

    def set_grade(self, points: float):
        self.points = points

    def set_st_features(self, st_features: List[StructuralFeature]):
        self.st_features = st_features

class GradeModel:
    def __init__(self, uml_model : UMLModel):
        self.classes: List[GradeObject] = []
        self.enums: List[GradeObject] = []
        self.relations: List[GradeObject] = []

        for cls in uml_model.class_list:
            self.classes.append(GradeObject(cls))
        for enm in uml_model.enum_list:
            self.enums.append(GradeObject(enm))
        for rel in uml_model.relation_list:
            self.relations.append(GradeObject(rel))
        
        self.class_lookup: Dict[str, GradeObject] = {cls.element: cls for cls in self.classes}
        self.enum_lookup: Dict[str, GradeObject] = {enm.element: enm for enm in self.enums}
        self.relation_lookup: Dict[str, GradeObject] = {rel.element: rel for rel in self.relations}


    def __repr__(self):
        return f"GradeModel(\nclasses: {self.classes},\nenums: {self.enums},\nrelations: {self.relations}\n)"

    def add_class_grade_structure(self, cls: UMLClass, exists_points: float = 0.0, attribute_points: float = 0.0, operation_points: float = 0.0):
        grade_class = self.class_lookup.get(cls)
        if not grade_class:
            raise ValueError(f"Class '{cls.name}' not found in model.")
        grade_class.st_features.append(StructuralFeature("exists", grade_class.element, exists_points))
        grade_class.points += exists_points
        for att in grade_class.element.attributes:
            grade_class.st_features.append(StructuralFeature(f"attribute \"{att.name}\"", att, attribute_points))
            grade_class.points += attribute_points
        for opr in grade_class.element.operations:
            grade_class.st_features.append(StructuralFeature(f"operation \"{opr.name}\"", opr, operation_points))
            grade_class.points += operation_points

    def grade_attribute(self, st_feature: StructuralFeature, att: UMLAttribute) -> float:
        # attribute found -> 1/2 points
        temp_grade: float = st_feature.points / 2
        temp_content_grade: float = 0.0
        content_check: Dict[str, bool] = st_feature.reference.compare_content_to_student(att)
        for _, checked in content_check.items():
            if checked:
                # structural match for e.g data type == data type
                temp_content_grade += 1
        # structural match normalized -> 1/2 points
        temp_grade += (temp_content_grade / len(content_check)) * (st_feature.points / 2)
        logger.debug(f"Grade for attribute '{att.name}': {temp_grade} (content match: {temp_content_grade} / {len(content_check)})")
        return temp_grade
    
    def grade_operation(self, st_feature: StructuralFeature, opr: UMLOperation) -> float:
        # operation found -> 1/2 points
        temp_grade: float = st_feature.points / 2
        temp_content_grade: float = 0.0
        content_check: Dict[str, bool] = st_feature.reference.compare_content_to_student(opr)
        for _, checked in content_check.items():
            if checked:
                # structural match for e.g parameter == parameter
                temp_content_grade += 1
        # structural match normalized -> 1/2 points
        temp_grade += (temp_content_grade / len(content_check)) * (st_feature.points / 2)
        logger.debug(f"Grade for operation '{opr.name}': {temp_grade} (content match: {temp_content_grade} / {len(content_check)})")
        return temp_grade

    def temp_grade_st_element(self, st_feature: StructuralFeature, stud_class_element_list: Optional[List[GradeReference]] = None, stud_element: Optional[UMLElement] = None) -> float:
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
                temp_grade += self.grade_attribute(st_feature, stud_element)
            elif isinstance(stud_element, UMLOperation):
                temp_grade += self.grade_operation(st_feature, stud_element)
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
    
    def temp_grade_class_content(self, stud_content: GradeReference, mapped_inst_content: GradeReference) -> Tuple[float, float]:
        temp_grade: float = 0.0
        grade_class: GradeObject = next((cls for cls in self.classes if cls.element == mapped_inst_content.reference), None)
        if not grade_class:
            raise ValueError(f"Class '{mapped_inst_content.reference.name}' of {str(mapped_inst_content)} not found in model.")
        if isinstance(mapped_inst_content, UMLAttribute):
            # attribute content grading
            for st_feature in grade_class.st_features:
                if st_feature.type == FeatureType.ATTRIBUTE and st_feature.reference == mapped_inst_content:
                    temp_grade += self.temp_grade_st_element(st_feature=st_feature, stud_element=stud_content)
                    break
        elif isinstance(mapped_inst_content, UMLOperation):
            # operation content grading
            for st_feature in grade_class.st_features:
                if st_feature.type == FeatureType.OPERATION and st_feature.reference == mapped_inst_content:
                    temp_grade += self.temp_grade_st_element(st_feature=st_feature, stud_element=stud_content)
                    break
        return (temp_grade / st_feature.points if st_feature.points > 0 else 0.0, temp_grade)
