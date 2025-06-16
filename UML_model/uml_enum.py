from UML_model.uml_element import UMLElement
from UML_model.uml_relation import UMLRelation
from typing import List

class UMLEnum(UMLElement):
    def __init__(self, name: str, values: List[str]):
        self.name = name
        self.values = values
        self.relations: List[UMLRelation] = []

    def __repr__(self):
        return f"UMLEnum({self.name})"
    
    def add_relation(self, relation: UMLRelation):
        if relation not in self.relations:
            self.relations.append(relation)
        return True