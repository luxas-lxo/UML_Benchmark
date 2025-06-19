from UML_model.uml_class import UMLClass
from UML_model.uml_enum import UMLEnum
from UML_model.uml_relation import UMLRelation, RelationType
from UML_model.uml_element import UMLElement
from tools.UML_parser import UMLParser
from typing import List

class UMLModel:
    def __init__(self, plantuml_str: str = None, class_list: List[UMLClass] = None,
                 enum_list: List[UMLEnum] = None, relation_list: List[UMLRelation] = None):
        
        if plantuml_str:
            self.class_list: List[UMLClass] = UMLParser.parse_plantuml_classes(plantuml_str)
            self.enum_list: List[UMLEnum] = UMLParser.parse_plantuml_enums(plantuml_str)
            self.relation_list: List[UMLRelation] = UMLParser.parse_plantuml_relations(plantuml_str, self.class_list, self.enum_list)
        else:
            self.class_list: List[UMLClass] = class_list or []
            self.enum_list: List[UMLEnum] = enum_list or []
            self.relation_list: List[UMLRelation] = relation_list or []

        self.class_lookup = {cls.name: cls for cls in self.class_list}
        self.enum_lookup = {enu.name: enu for enu in self.enum_list}
        self.element_lookup = self.class_lookup | self.enum_lookup
        if self.relation_list:
            self.assign_relations()

    def __repr__(self):
        return f"UMLModel(\nClasses: {self.class_list},\nEnums: {self.enum_list},\nRelations: {self.relation_list})"
    
    def assign_relations(self):
        for relation in self.relation_list:
            if isinstance(relation.source, UMLElement) and isinstance(relation.destination, UMLElement):
                self.element_lookup[relation.source.name].add_relation(relation)
                if not relation.directed:
                    self.element_lookup[relation.destination.name].add_relation(relation)
            
        return True
