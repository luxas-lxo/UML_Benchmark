from UML_model.uml_element import UMLElement
from grading.grade_reference import GradeReference

from enum import Enum

class RelationType(Enum):
    ASSOCIATION = "association"
    AGGREGATION = "aggregation"
    COMPOSITION = "composition"
    ASSOCIATION_LINK = "association link"
    UNKNOWN = "unknown"

class UMLRelation(UMLElement, GradeReference):
    def __init__(self, type: RelationType, source: UMLElement, destination: UMLElement, s_multiplicity: str = "", d_multiplicity: str = ""):
        self.type = type
        self.source = source
        self.destination = destination
        self.s_multiplicity = s_multiplicity
        self.d_multiplicity = d_multiplicity
        self.directed = self.type != RelationType.ASSOCIATION
        self.name = f"({source.name}, {destination.name})"
        

    def __repr__(self):
        #return f"UMLRelation({self.source} [{self.s_multiplicity}] -{self.type.name}- [{self.d_multiplicity}] {self.destination})"
        return f"UMLRelation({self.source}, {self.destination})"
    
    def __eq__(self, other):
        if not isinstance(other, UMLRelation):
            return NotImplemented

        same_direction = (
            self.type == other.type and
            self.source == other.source and
            self.s_multiplicity == other.s_multiplicity and
            self.destination == other.destination and
            self.d_multiplicity == other.d_multiplicity
        )

        if same_direction:
            return True

        if not self.directed and not other.directed:
            reverse_direction = (
                self.type == other.type and
                self.source == other.destination and
                self.s_multiplicity == other.d_multiplicity and
                self.destination == other.source and
                self.d_multiplicity == other.s_multiplicity
            )
            return reverse_direction

        return False
  
    def __hash__(self):
        if self.directed:
            return hash((self.type, self.source, self.destination))
        else:
            return hash((self.type, frozenset([self.source, self.destination])))
        
    #Im Unterschied zu eq ohne Multiplizitäten
    def equals(self, other):
        if not isinstance(other, UMLRelation):
            return NotImplemented
        
        same_direction = (
            self.type == other.type and
            self.source == other.source and
            self.destination == other.destination
        )

        if same_direction:
            return True

        if not self.directed and not other.directed:
            reverse_direction = (
                self.type == other.type and
                self.source == other.destination and
                self.destination == other.source
            )
            return reverse_direction

        return False
    