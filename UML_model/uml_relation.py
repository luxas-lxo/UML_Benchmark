from UML_model.uml_element import UMLElement
from grading.grade_reference import GradeReference

from enum import Enum
import textwrap
import shutil

class RelationType(Enum):
    ASSOCIATION = "association"
    AGGREGATION = "aggregation"
    COMPOSITION = "composition"
    ASSOCIATION_LINK = "association link"
    UNKNOWN = "unknown"

class UMLRelation(UMLElement, GradeReference):
    #TODO: Rollen entnehmen und verarbeiten -> repr, plantuml, equals, hash, eq
    # aktuell bei gleicher verbindung trotzdem eingetragen???
    def __init__(self, type: RelationType, source: UMLElement, destination: UMLElement, s_multiplicity: str = "", d_multiplicity: str = ""):
        self.type: RelationType = type
        self.source: UMLElement = source
        self.destination: UMLElement = destination
        #TODO: multiplicity as enum class
        self.s_multiplicity: str = s_multiplicity
        self.d_multiplicity: str = d_multiplicity
        self.directed: bool = self.type != RelationType.ASSOCIATION
        super().__init__(f"({self.source.name}, {self.destination.name})")

    def __repr__(self):
        return f"UMLRelation({self.source}, {self.destination}): source multiplicity {self.s_multiplicity} -{self.type.name}- destination multiplicity {self.d_multiplicity if self.d_multiplicity != '' else '_'}"
    
    def to_plantuml(self):
        type_map = {
            RelationType.ASSOCIATION: "--",
            RelationType.ASSOCIATION_LINK: "..",
            RelationType.AGGREGATION: "--o",
            RelationType.COMPOSITION: "--*"
        }
        symbol = type_map.get(self.type, "--")
        return f"{self.source.name} {'\"' + self.s_multiplicity + '\"' if symbol != '..' else ''} {symbol} {'\"' + self.d_multiplicity + '\"' if symbol != '..' else ''} {self.destination.name}"

    
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
      
    def __hash__(self):
        if self.directed:
            return hash((self.type, self.source, self.destination))
        else:
            return hash((self.type, frozenset([self.source, self.destination])))
               
    