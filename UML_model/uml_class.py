from UML_model.uml_element import UMLElement
from UML_model.uml_relation import UMLRelation
from typing import List

class UMLClass(UMLElement):
    def __init__(self, name: str, attributes: List[str], operations: List[str]):
        self.name = name
        self.attributes = attributes
        self.operations = operations
        self.relations: List[UMLRelation] = []

    def __repr__(self):
        return f"UMLClass({self.name})"
    
    def add_relation(self, relation: UMLRelation):
        if relation not in self.relations:
            self.relations.append(relation)
        return True
    
    def get_relation_ends(self):
        ends: List[UMLClass] = []
        for rel in self.relations:
            ends.append(rel.destination)
            if not rel.directed:
                ends.append(rel.source)
        return ends
    

    

