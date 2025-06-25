from UML_model.uml_model import UMLModel
from UML_model.uml_element import UMLElement
from UML_model.uml_class import UMLClass, UMLAttribute, UMLOperation
from UML_model.uml_enum import UMLEnum, UMLValue
from UML_model.uml_relation import UMLRelation
from grading.grade_reference import GradeReference
from tools.syntactic_check import SyntacticCheck
from tools.semantic_check import SemanticCheck

from typing import List, Dict, Tuple
from enum import Enum

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
        
        self.class_lookup: Dict[str, GradeObject] = {cls.element.name.lower().strip(): cls for cls in self.classes}
        self.enum_lookup: Dict[str, GradeObject] = {enm.element.name.lower().strip(): enm for enm in self.enums}
        self.relation_lookup: Dict[str, GradeObject] = {rel.element.name.lower().strip(): rel for rel in self.relations}


    def __repr__(self):
        return f"GradeModel(\nclasses: {self.classes},\nenums: {self.enums},\nrelations: {self.relations}\n)"
        
    def add_class_grade_structure(self, class_name: str, exists_points: float = 0.0, attribute_points: float = 0.0, operation_points: float = 0.0):
        grade_class = self.class_lookup.get(class_name.lower().strip())
        if not grade_class:
            raise ValueError(f"Class '{class_name}' not found in model.")
        grade_class.st_features.append(StructuralFeature("exists", grade_class.element, exists_points))
        grade_class.points += exists_points
        for att in grade_class.element.attributes:
            grade_class.st_features.append(StructuralFeature(f"attribute \"{att.name}\"", att, attribute_points))
            grade_class.points += attribute_points
        for opr in grade_class.element.operations:
            grade_class.st_features.append(StructuralFeature(f"operation \"{opr.name}\"", opr, operation_points))
            grade_class.points += operation_points

    def temp_grade_st_attribute(self, st_feature: StructuralFeature, stud_class: UMLClass):
        temp_grade: float = 0.0
        for att in stud_class.attributes:
            if st_feature.reference.name == att.name or SyntacticCheck.syntactic_match(att.name, st_feature.reference.name)[0] or SemanticCheck.semantic_match(att.name, st_feature.reference.name)[0]:
                # Attribute found -> 1/2 points
                temp_grade += st_feature.points / 2
                if st_feature.reference.compare_content_to_student(att):
                    # structural match -> 1/2 points
                    temp_grade += st_feature.points / 2
                break
        return temp_grade
    
    def temp_grade_st_operation(self, st_feature: StructuralFeature, stud_class: UMLClass):
        temp_grade: float = 0.0
        for opr in stud_class.operations:
            if st_feature.reference.name == opr.name or SyntacticCheck.syntactic_match(opr.name, st_feature.reference.name)[0] or SemanticCheck.semantic_match(opr.name, st_feature.reference.name)[0]:
                # Operation found -> 1/2 points
                temp_grade += st_feature.points / 2
                if st_feature.reference.compare_content_to_student(opr):
                    # structural match -> 1/2 points
                    temp_grade += st_feature.points / 2
                break
        return temp_grade

    def temp_grade_class(self, stud_class: UMLClass, mapped_inst_class: UMLClass) -> Tuple[float, float]:
        temp_grade: float = 0.0
        grade_class: GradeObject = self.class_lookup.get(mapped_inst_class.name.lower().strip())
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
                temp_grade += self.temp_grade_st_attribute(st_feature, stud_class)
            elif st_feature.type == FeatureType.OPERATION:
                temp_grade += self.temp_grade_st_operation(st_feature, stud_class)
            else:
                return NotImplemented
        return (temp_grade / grade_class.points if grade_class.points > 0 else 0.0, temp_grade)

    