from UML_model.uml_element import UMLElement
from UML_model.uml_relation import UMLRelation
from grading.grade_reference import GradeReference

from typing import List, Dict
from enum import Enum
class UMLDataType(Enum):
    # TODO: wenn später gebraucht, ausbauen
    STR = "str"
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    VOID = "void"
    UNKNOWN = "unknown"
    # ...

class UMLVisability(Enum):
    # TODO: wenn später gebraucht, ausbauen
    PUBLIC = "public"
    PRIVATE = "private"
    PROTECTED = "protected"
    UNKNOWN = "unknown"

class UMLAttribute(GradeReference):
    def __init__(self, name: str, datatype: UMLDataType = UMLDataType.UNKNOWN, visability: UMLVisability = UMLVisability.UNKNOWN):
        self.name = name
        self.datatype = datatype
        self.visability = visability
        self.derived: bool = False
        if self.name.startswith("/"):
            self.name = self.name.removeprefix("/")
            self.derived = True
    
    def __repr__(self):
        return f"UMLAttribute({self.name})"
        
class UMLOperation(GradeReference):
    def __init__(self, name: str, params: Dict[str, UMLDataType] = {}, return_types: List[UMLDataType] = [UMLDataType.VOID]):
        self.name = name.removesuffix("()")
        self.params = params
        self.return_types = return_types
        # TODO: falls später notwendig hier oder im UMLParser die parameter/rückgabetypen extrahieren

    def __repr__(self):
        return f"UMLOperation({self.name})"

        
class UMLClass(UMLElement, GradeReference):
    def __init__(self, name: str, attributes: List[UMLAttribute], operations: List[UMLOperation]):
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
    

    

