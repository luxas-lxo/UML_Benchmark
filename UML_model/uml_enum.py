from UML_model.uml_element import UMLElement
from UML_model.uml_relation import UMLRelation
from grading.grade_reference import GradeReference

from typing import List, Optional

class UMLValue(GradeReference):
    def __init__(self, name: str):
        self.name = name
        self.reference: Optional[UMLEnum] = None  

    def __repr__(self):
        return f"UMLValue({self.name})"
    
    def __eq__(self, other):
        if not isinstance(other, UMLValue):
            return NotImplemented
        return self.name == other.name
    
    def __hash__(self):
        return hash(self.name)

class UMLEnum(UMLElement, GradeReference):
    def __init__(self, name: str, values: Optional[List[UMLValue]] = None):
        super().__init__(name)
        self.values: List[UMLValue] = values if values is not None else []
        self.relations: List[UMLRelation] = []
        self.asign_content_reference()

    def __repr__(self): 
        return f"UMLEnum({self.name}): values [{', '.join(v.name for v in self.values)}]"
    
    def to_plantuml(self) -> str:
        body = '\n\t'.join(v.name for v in self.values)
        return f"enum {self.name} {{\n\t{body}\n}}"
    
    def __eq__(self, other):
        if not isinstance(other, UMLEnum):
            return NotImplemented
        return self.name == other.name and self.values == other.values
    
    def __hash__(self):
        return hash(self.name)
        
    def add_relation(self, relation: UMLRelation):
        if relation not in self.relations:
            self.relations.append(relation)
    
    def asign_content_reference(self):
        for value in self.values:
            value.reference = self
        