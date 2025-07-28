from UML_model.uml_element import UMLElement
from grading.grade_reference import GradeReference

from enum import Enum
from typing import Dict
import re

class UMLRelationType(Enum):
    ASSOCIATION = "association"
    AGGREGATION = "aggregation"
    COMPOSITION = "composition"
    GENERALIZATION = "generalization"
    ASSOCIATION_LINK = "association link"
    UNKNOWN = "unknown"

    @staticmethod
    def from_string(type_str: str) -> 'UMLRelationType':
        type_str = type_str.lower().strip()
        association = re.compile(r"-+")
        aggregation_1 = re.compile(r"-+o")
        aggregation_2 = re.compile(r"o-+")
        composition_1 = re.compile(r"-+\*")
        composition_2 = re.compile(r"\*-+")
        generalization_1 = re.compile(r"-+\|\>")
        generalization_2 = re.compile(r"\<\|-+")
        if association.match(type_str):
            return UMLRelationType.ASSOCIATION
        elif aggregation_1.match(type_str) or aggregation_2.match(type_str):
            return UMLRelationType.AGGREGATION
        elif composition_1.match(type_str) or composition_2.match(type_str):
            return UMLRelationType.COMPOSITION
        elif generalization_1.match(type_str) or generalization_2.match(type_str):
            return UMLRelationType.GENERALIZATION
        else:
            return UMLRelationType.UNKNOWN


class UMLRelation(UMLElement, GradeReference):
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
            UMLRelationType.ASSOCIATION: "-",
            UMLRelationType.ASSOCIATION_LINK: "..",
            UMLRelationType.AGGREGATION: "-o",
            UMLRelationType.COMPOSITION: "-*"
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
        # Remove all whitespaces
        multiplicity = multiplicity.replace(" ", "")
        # Remove enclosing [] or ()
        if (multiplicity.startswith("[") and multiplicity.endswith("]")) or (multiplicity.startswith("(") and multiplicity.endswith(")")):
            multiplicity = multiplicity[1:-1]
        # If multiplicity is in the form "x..x" or "*..*", normalize to "x" or "*"
        match = re.match(r'^([*\d]+)\.\.([*\d]+)$', multiplicity)
        if match:
            first, last = match.groups()
            if first == last:
                multiplicity = first
        # Normalize common forms not captured by regex
        if multiplicity == "0..*":
            multiplicity = "*"
        if multiplicity == "":
            multiplicity = "1"
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
    
    def copy(self) -> 'UMLRelation':
        return UMLRelation(
            type=self.type,
            source=self.source,
            destination=self.destination,
            s_multiplicity=self.s_multiplicity,
            d_multiplicity=self.d_multiplicity,
            description=self.description
        )
