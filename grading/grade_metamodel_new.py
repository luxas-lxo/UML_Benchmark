from UML_model.uml_model import UMLModel
from UML_model.uml_element import UMLElement
from UML_model.uml_class import UMLClass, UMLAttribute, UMLOperation
from UML_model.uml_enum import UMLEnum, UMLValue
from UML_model.uml_relation import UMLRelation
from grading.grade_reference import GradeReference

from typing import List, Dict
from enum import Enum

class FeatureType(Enum):
    # TODO mehr hinzufügen wenn benötigt
    CLASS = "class"
    ATTRIBUTE = "attribute"
    OPERATION = "operation"

    ENUM = "enum"
    VALUE = "value"

    RELATION = "relation"
    RELATION_ELEMENTS = "relation elements"

    UNKNOWN = "unknown"

class StructuralFeature:
    def __init__(self, description: str, reference: GradeReference ,points: float):
        self.description = description
        self.type: FeatureType
        self.reference = reference
        self.points = points
        if isinstance(reference, UMLClass):
            self.type = FeatureType.CLASS
        elif isinstance(reference, UMLAttribute):
            self.type = FeatureType.ATTRIBUTE
        elif isinstance(reference, UMLOperation):
            self.type = FeatureType.OPERATION
        elif isinstance(reference, UMLEnum):
            self.type = FeatureType.ENUM
        elif isinstance(reference, UMLValue):
            self.type = FeatureType.VALUE
        elif isinstance(reference, UMLRelation):
            self.type = FeatureType.RELATION
        else:
            self.type = FeatureType.UNKNOWN

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
        self.elements: Dict[str, List[GradeObject]] = {}

        for cls in uml_model.class_list:
            self.classes.append(GradeObject(cls))
        for enm in uml_model.enum_list:
            self.enums.append(GradeObject(enm))
        for rel in uml_model.relation_list:
            self.relations.append(GradeObject(rel))
        
        self.class_lookup: Dict[str, GradeObject] = {cls.element.name: cls for cls in self.classes}
        self.enum_lookup: Dict[str, GradeObject] = {enm.element.name: enm for enm in self.enums}
        self.relation_lookup: Dict[str, GradeObject] = {rel.element.name: rel for rel in self.relations}

        self.elements["classes"] = self.classes
        self.elements["enums"] = self.enums
        self.elements["relations"] = self.relations

    def __repr__(self):
        return f"GradeModel(\nclasses: {self.classes},\nenums: {self.enums},\nrelations: {self.relations}\n)"
        
    def add_class_grade_structure(self, class_name: str, exists_points: float = 0.0, attribute_points: float = 0.0, operation_points: float = 0.0):
        grade_class = self.class_lookup.get(class_name)
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

    def grade_class(self, stud_class: UMLClass, mapped_inst_class: UMLClass):
        grade: float = 0.0
        grade_class = self.class_lookup.get(mapped_inst_class.name)
        if not grade_class:
            raise ValueError(f"Class '{mapped_inst_class.name}' not found in model.")
        for st_feauture in grade_class.st_features:
            if st_feauture.type == FeatureType.CLASS:
                # klasse wurde gemappt -> sie existiert -> gibt punkte
                grade += st_feauture.points
            elif st_feauture.type == FeatureType.ATTRIBUTE:
                #TODO: Attribute match
                pass
            elif st_feauture.type == FeatureType.OPERATION:
                #TODO: Operation match
                pass
            else:
                return NotImplemented
                

        

    