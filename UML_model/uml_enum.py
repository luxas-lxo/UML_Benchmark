from UML_model.uml_element import UMLElement
from UML_model.uml_relation import UMLRelation
from grading.grade_reference import GradeReference

from typing import List

class UMLValue(GradeReference):
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"UMLValue({self.name})"

class UMLEnum(UMLElement, GradeReference):
    def __init__(self, name: str, values: List[UMLValue]):
        super().__init__(name)
        self.values: List[UMLValue] = values
        self.relations: List[UMLRelation] = []

    def __repr__(self): 
        return f"UMLEnum({self.name}): [{', '.join(v.name for v in self.values)}]"
    
    def to_plantuml(self) -> str:
        body = '\n\t'.join(v.name for v in self.values)
        return f"enum {self.name} {{\n\t{body}\n}}"
    
    def add_relation(self, relation: UMLRelation):
        if relation not in self.relations:
            self.relations.append(relation)
        return True