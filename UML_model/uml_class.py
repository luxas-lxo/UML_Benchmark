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
    def from_string(type_str: str) -> Optional['UMLDataType']:
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
    def __init__(self, name: str, data_type: UMLDataType = UMLDataType.UNKNOWN, initial: str = "", visibility: UMLVisability = UMLVisability.UNKNOWN, derived: bool = False):
        self.name: str = name
        self.data_type: UMLDataType = data_type
        self.initial: str = initial
        self.visibility: UMLVisability = visibility
        self.derived: bool = derived
        self.reference: Optional[UMLClass] = None
    
    def __repr__(self): 
        return f"UMLAttribute({('/' if self.derived else '') + self.name}): visability {self.visibility.name}, datatype {self.data_type.name}, initial {'= ' + self.initial if self.initial else 'None'}"

    def __str__(self):
        return f"UMLAttribute({self.name})"
    
    def to_plantuml(self) -> str:
        name_part = ('/' if self.derived else '') + self.name
        if self.data_type != UMLDataType.UNKNOWN:
            type_part = ': ' + self.data_type.value
            if self.initial != '':
                type_part += ' = ' + self.initial
        else:
            type_part = ''
        return f"{self.visibility.value}{name_part}{type_part}"

    def __hash__(self):
        return hash((self.name, self.data_type, self.initial, self.visibility, self.derived))
    
    def __eq__(self, other):
        if not isinstance(other, UMLAttribute):
            return NotImplemented
        return (
            self.name == other.name and
            self.data_type == other.data_type and
            self.initial == other.initial and
            self.visibility == other.visibility and
            self.derived == other.derived
        )
    
class UMLOperation(GradeReference):
    #TODO: add other specifications if needed (e.g. modifier)
    def __init__(self, name: str, params: Optional[Dict[str, UMLDataType]] = None, return_types: Optional[List[UMLDataType]] = None, visibility: UMLVisability = UMLVisability.UNKNOWN):
        self.name: str = name
        self.params: Dict[str, UMLDataType] = params if params is not None else {}
        self.return_types: List[UMLDataType] = return_types if return_types is not None else [UMLDataType.VOID]
        self.visibility: UMLVisability = visibility 
        self.reference: Optional[UMLClass] = None  

    def __repr__(self): 
        return f"UMLOperation({self.name}({', '.join(f'{k}: {v.name}' for k, v in self.params.items())})): visability {self.visibility.name}, return type [{', '.join(t.name for t in self.return_types)}]"

    def __str__(self):
        return f"UMLOperation({self.name})"
    
    def to_plantuml(self) -> str: 
        return f"{self.visibility.value}{self.name}({', '.join(f'{k}' if v == UMLDataType.UNKNOWN else f'{k}: {v.value}' for k, v in self.params.items())}): {', '.join(t.value for t in self.return_types)}"
    
    def __hash__(self):
        return hash((self.name, tuple(self.params.items()), tuple(self.return_types), self.visibility))

    
    def __eq__(self, other):
        if not isinstance(other, UMLOperation):
            return NotImplemented
        return (
            self.name == other.name and
            self.params == other.params and
            self.return_types == other.return_types and
            self.visibility == other.visibility
        )
     
class UMLClass(UMLElement, GradeReference):
    def __init__(self, name: str, attributes: Optional[List[UMLAttribute]] = None, operations: Optional[List[UMLOperation]] = None):
        super().__init__(name)
        self.attributes: List[UMLAttribute] = attributes if attributes is not None else []
        self.operations: List[UMLOperation] = operations if operations is not None else []
        self.relations: List[UMLRelation] = []
        self.super_class: Optional[UMLClass] = None 
        UMLClass.assign_content_reference(self)


    def __repr__(self): 
        return f"UMLClass({self.name}): \nattributes [{', '.join(str(a) for a in self.attributes)}], \noperations [{', '.join(str(o) for o in self.operations)}], \nrelations [{', '.join(str(r) for r in self.relations)}]"
    
    def to_plantuml(self) -> str:
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
        return hash((self.name, tuple(self.attributes), tuple(self.operations), tuple(self.relations), self.super_class))


    def assign_content_reference(self):
        for att in self.attributes:
            att.reference = self
        for opr in self.operations:
            opr.reference = self
         
    def add_relation(self, relation: UMLRelation):
        if relation not in self.relations:
            self.relations.append(relation)
    
    def get_relation_ends(self) -> List['UMLClass']:
        ends: List[UMLClass] = []
        for rel in self.relations:
            ends.append(rel.destination)
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
                details = f"{prefix}{att.visibility} {"/" + att.name if att.derived else att.name}: {att.data_type} = {att.initial}"
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
                details = f"{prefix}{opr.visibility} {opr.name}({opr.params}): {opr.return_types}"
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

    

