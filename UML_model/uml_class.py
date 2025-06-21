from UML_model.uml_element import UMLElement
from UML_model.uml_relation import UMLRelation
from grading.grade_reference import GradeReference

from typing import List, Dict, Optional
from enum import Enum
import textwrap
import shutil

class UMLDataType(Enum):
    # TODO: wenn später gebraucht, ausbauen
    STR = "str"
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    VOID = "void"
    UNKNOWN = ""

    @staticmethod
    def from_string(type_str: str) -> 'UMLDataType':
        normalized = type_str.strip().lower()
        
        type_aliases = {
            "str": UMLDataType.STR,
            "string": UMLDataType.STR,
            "text": UMLDataType.STR,

            "int": UMLDataType.INT,
            "integer": UMLDataType.INT,

            "float": UMLDataType.FLOAT,
            "double": UMLDataType.FLOAT,

            "bool": UMLDataType.BOOL,
            "boolean": UMLDataType.BOOL,

            "void": UMLDataType.VOID,
            "none": UMLDataType.VOID,
        }

        return type_aliases.get(normalized, UMLDataType.UNKNOWN)

class UMLVisability(Enum):
    PUBLIC = "+"
    PRIVATE = "-"
    PROTECTED = "#"
    PACKAGE = "~"
    UNKNOWN = ""

class UMLAttribute(GradeReference):
    #TODO: add other specifications if needed (e.g. multiplicity constraints or modifier)
    def __init__(self, name: str, datatype: UMLDataType = UMLDataType.UNKNOWN, initial: str = "", visability: UMLVisability = UMLVisability.UNKNOWN, derived: bool = False):
        self.name: str = name
        self.datatype: UMLDataType = datatype
        self.initial: str = initial
        self.visability: UMLVisability = visability
        self.derived: bool = derived
        self.reference: Optional[UMLClass] = None
    
    def __repr__(self): 
        return f"UMLAttribute({('/' if self.derived else '') + self.name}): visability {self.visability.name},  datatype  {self.datatype.name}, initial {'= ' + self.initial if self.initial else 'None'}"

    def __str__(self):
        return f"UMLAttribute({self.name})"
    
    def to_plantuml(self) -> str:
        return f"{self.visability.value}{('/' if self.derived else '') + self.name}{': ' + self.datatype.value + (' = ' + self.initial if self.initial != '' else '') if self.datatype != UMLDataType.UNKNOWN else ''}"

    def __hash__(self):
        return hash(self.name) 
    
class UMLOperation(GradeReference):
    #TODO: add other specifications if needed (e.g. modifier)
    def __init__(self, name: str, params: Dict[str, UMLDataType] = {}, return_types: List[UMLDataType] = [UMLDataType.VOID], visability: UMLVisability = UMLVisability.UNKNOWN):
        self.name: str = name
        self.params: Dict[str, UMLDataType] = params
        self.return_types: List[UMLDataType] = return_types
        self.visability: UMLVisability = visability
        self.reference: Optional[UMLClass] = None

    def __repr__(self): 
        return f"UMLOperation({self.name}({', '.join(f'{k}: {v.name}' for k, v in self.params.items())})): visabilty {self.visability.name}, return type [{', '.join(t.name for t in self.return_types)}]"

    def __str__(self):
        return f"UMLOperation({self.name})"
    
    def to_plantuml(self) -> str: 
        return f"{self.visability.value}{self.name}({', '.join(f'{k}' if v == UMLDataType.UNKNOWN else f'{k}: {v.value}' for k, v in self.params.items())}): {', '.join(t.value for t in self.return_types)}"
    
    def __hash__(self):
        return hash(self.name) 
     
class UMLClass(UMLElement, GradeReference):
    def __init__(self, name: str, attributes: List[UMLAttribute] = [], operations: List[UMLOperation] = []):
        super().__init__(name)
        self.attributes: List[UMLAttribute] = attributes
        self.operations: List[UMLOperation] = operations
        self.relations: List[UMLRelation] = []
        #TODO fehlt noch vollständig in Implementation
        self.super_class: Optional[UMLClass] = None 
        for att in self.attributes:
            att.reference = self
        for opr in self.operations:
            opr.reference = self

    def __repr__(self): 
        return f"UMLClass({self.name}): \nattributes = [{', '.join(str(a) for a in self.attributes)}], \noperations = [{', '.join(str(o) for o in self.operations)}], \nrelations = [{', '.join(str(r) for r in self.relations)}]"
    
    def to_plantuml(self):
        lines = [a.to_plantuml() for a in self.attributes] + [o.to_plantuml() for o in self.operations]
        if not lines:
            return f"class {self.name}"
        body = '\n\t'.join(lines)
        return f"class {self.name} {{\n\t{body}\n}}"
    
    def __eq__(self, other):
        if not isinstance(other, UMLClass):
            return NotImplemented
        return (
            self.name == other.name and
            self.attributes == other.attributes and
            self.operations == other.operations and
            self.relations == other.relations and
            self.super_class == other.super_class
        )   
    
    def __hash__(self):
        return hash(self.name)
        
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
    
    def find_attribute(self, attribute_name: str) -> Optional[UMLAttribute]:
        for att in self.attributes:
            if att.name.lower().strip() == attribute_name.lower().strip():
                return att
        return None
    
    def find_operation(self, operation_name: str) -> Optional[UMLOperation]:
        for opr in self.operations:
            if opr.name.lower().strip() == operation_name.lower().strip():
                return opr
        return None
    
    def print_details(self):
        term_width = shutil.get_terminal_size((80, 20)).columns  - 10
        empty = "\t\tempty"
        print(f"**{self} Details:**")
        print("\t**Attribute list:**")
        if self.attributes:
            for att in self.attributes:
                prefix = f"{att}: "
                details = f"{prefix}{att.visability} {"/" + att.name if att.derived else att.name}: {att.datatype} = {att.initial}"
                indent = '\t\t' + ' ' * len(prefix)
                wrapped = textwrap.fill(
                    details,
                    width=term_width,
                    initial_indent='\t\t',
                    subsequent_indent=indent
                )
                print(wrapped)
        else: 
            print(empty)

        print("\t**Operation list:**")
        if self.operations:
            for opr in self.operations:
                prefix = f"{opr}: "
                details = f"{prefix}{opr.visability} {opr.name}({opr.params}): {opr.return_types}"
                indent = '\t\t' + ' ' * len(prefix)
                wrapped = textwrap.fill(
                    details,
                    width=term_width,
                    initial_indent='\t\t',
                    subsequent_indent=indent
                )
                print(wrapped)
        else: 
            print(empty)

        print("\t**Relation list:**")
        if self.relations:
            for rel in self.relations:
                prefix = f"{rel}: "
                details = f"{prefix}{rel.source} ({rel.s_multiplicity}) {str(rel.type) + " " + str(rel.directed)} ({rel.d_multiplicity}) {rel.destination}"
                indent = '\t\t' + ' ' * len(prefix)
                wrapped = textwrap.fill(
                    details,
                    width=term_width,
                    initial_indent='\t\t',
                    subsequent_indent=indent
                )
                print(wrapped)
        else: 
            print(empty)

        print("\n")

    

