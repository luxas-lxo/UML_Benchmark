from UML_model.uml_element import UMLElement
from grading.grade_reference import GradeReference

from enum import Enum
from typing import Dict

class UMLRelationType(Enum):
    ASSOCIATION = "association"
    AGGREGATION = "aggregation"
    COMPOSITION = "composition"
    ASSOCIATION_LINK = "association link"
    UNKNOWN = "unknown"

class UMLRelation(UMLElement, GradeReference):
    #TODO: Rollen entnehmen und verarbeiten -> repr, plantuml, equals, hash, eq
    # aktuell bei gleicher verbindung trotzdem eingetragen???
    def __init__(self, type: UMLRelationType, source: UMLElement, destination: UMLElement, s_multiplicity: str = "", d_multiplicity: str = "", description: str = ""):
        self.type: UMLRelationType = type
        self.source: UMLElement = source
        self.destination: UMLElement = destination
        # NOTE: multiplicity as enum class?
        self.s_multiplicity: str = UMLRelation.normalize_multiplicity(s_multiplicity)
        self.d_multiplicity: str = UMLRelation.normalize_multiplicity(d_multiplicity)
        self.description: str = description
        self.directed: bool = self.type != UMLRelationType.ASSOCIATION
        super().__init__(f"({self.source.name}, {self.destination.name})")

    def __repr__(self):
        return f"UMLRelation({self.source}, {self.destination}): source multiplicity {self.s_multiplicity} -{self.type.name}- destination multiplicity {self.d_multiplicity if self.d_multiplicity != '' else '_'}: {self.description if self.description else 'empty'}"
    
    def to_plantuml(self) -> str:
        type_map = {
            UMLRelationType.ASSOCIATION: "--",
            UMLRelationType.ASSOCIATION_LINK: "..",
            UMLRelationType.AGGREGATION: "--o",
            UMLRelationType.COMPOSITION: "--*"
        }
        symbol = type_map.get(self.type, "--")
        return f"{self.source.name} {'\"' + self.s_multiplicity + '\"' if symbol != '..' else ''} {symbol} {'\"' + self.d_multiplicity + '\"' if symbol != '..' else ''} {self.destination.name}{' : ' + self.description if self.description else ''}"

    def __eq__(self, other):
        if not isinstance(other, UMLRelation):
            return NotImplemented

        same_direction = (
            self.type == other.type and
            self.source == other.source and
            self.s_multiplicity == other.s_multiplicity and
            self.destination == other.destination and
            self.d_multiplicity == other.d_multiplicity and 
            self.description == other.description
        )

        if same_direction:
            return True

        if not self.directed and not other.directed:
            reverse_direction = (
                self.type == other.type and
                self.source == other.destination and
                self.s_multiplicity == other.d_multiplicity and
                self.destination == other.source and
                self.d_multiplicity == other.s_multiplicity and
                self.description == other.description
            )
            return reverse_direction

        return False
  
    # NOTE: this is not the same as __eq__, this is used to compare the relation without considering the multiplicities
    def equals(self, other: 'UMLRelation') -> bool:
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

    def classes_equal(self, other: 'UMLRelation') -> bool:
        if not isinstance(other, UMLRelation):
            return NotImplemented

        return (self.source == other.source and self.destination == other.destination) or (not self.directed and self.destination == other.source and self.source == other.destination)

    def __hash__(self):
        if self.directed:
            return hash((self.type, (self.source.name, self.destination.name), self.s_multiplicity, self.d_multiplicity, self.description))
        else:
            return hash((self.type, frozenset([self.source.name, self.destination.name]), self.s_multiplicity, self.d_multiplicity, self.description))

    def swap_source_destination(self) -> 'UMLRelation':
        if self.directed:
            raise ValueError("Cannot swap source and destination for directed relations.")
        else:
            return UMLRelation(type=self.type, source=self.destination, destination=self.source, s_multiplicity=self.d_multiplicity, d_multiplicity=self.s_multiplicity)

    @staticmethod
    def normalize_multiplicity(multiplicity: str) -> str:
        # Normalize multiplicity values to standard forms
        if multiplicity in {"*", "0..*"}:
            multiplicity = "*"
        elif multiplicity in {"1", "1..1", ""}:
            multiplicity = "1"
        elif multiplicity in {"0", "0..0"}:
            multiplicity = "0"
        return multiplicity

    def compare_content_to_student(self, stud_relation: 'UMLRelation', element_match_map: Dict[UMLElement, UMLElement]) -> Dict[str, bool]:
        matches = {
            "type": False,
            "direction": False,
            "s_multiplicity": False,
            "d_multiplicity": False
        }
        if self.type == stud_relation.type:
            matches["type"] = True
        if (self.source, stud_relation.source) in element_match_map.items() and (self.destination, stud_relation.destination) in element_match_map.items():
            matches["direction"] = True
            if self.s_multiplicity == stud_relation.s_multiplicity:
                matches["s_multiplicity"] = True
            if self.d_multiplicity == stud_relation.d_multiplicity:
                matches["d_multiplicity"] = True
        elif (self.source, stud_relation.destination) in element_match_map.items() and (self.destination, stud_relation.source) in element_match_map.items():
            if not self.directed and not stud_relation.directed:
                matches["direction"] = True
            if self.s_multiplicity == stud_relation.d_multiplicity:
                matches["s_multiplicity"] = True
            if self.d_multiplicity == stud_relation.s_multiplicity:
                matches["d_multiplicity"] = True
        return matches
