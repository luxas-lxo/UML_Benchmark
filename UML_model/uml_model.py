from UML_model.uml_class import UMLClass
from UML_model.uml_enum import UMLEnum
from UML_model.uml_relation import UMLRelation
from UML_model.uml_element import UMLElement
from tools.UML_parser import UMLParser

from typing import List, Dict, Optional, Set
import textwrap
import shutil

class UMLModel:
    def __init__(self, plantuml_str: str = None, class_list: List[UMLClass] = None,
                 enum_list: List[UMLEnum] = None, relation_list: List[UMLRelation] = None):
        
        if plantuml_str:
            self.class_list: List[UMLClass] = UMLParser.parse_plantuml_classes(plantuml_str)
            self.enum_list: List[UMLEnum] = UMLParser.parse_plantuml_enums(plantuml_str)
            self.relation_list: List[UMLRelation] = UMLParser.parse_plantuml_relations(plantuml_str, self.class_list, self.enum_list)
        else:
            self.class_list: List[UMLClass] = class_list or []
            self.enum_list: List[UMLEnum] = enum_list or []
            self.relation_list: List[UMLRelation] = relation_list or []

        self.class_lookup: Dict[str, UMLClass] = {cls.name.lower().strip(): cls for cls in self.class_list}
        self.enum_lookup: Dict[str, UMLEnum] = {enu.name.lower().strip(): enu for enu in self.enum_list}
        self.relation_lookup: Dict[str, UMLRelation] = {rel.name.lower().strip(): rel for rel in self.relation_list}
        self.element_list: List[UMLElement] = self.class_list + self.enum_list + self.relation_list
        self.element_lookup: Dict[str, UMLElement] = self.class_lookup | self.enum_lookup | self.relation_lookup

        if self.relation_list:
            self.assign_relations()

    def __repr__(self): 
        return f"UMLModel(\nClasses = [{', '.join(cls.name for cls in self.class_list)}], \nEnums = [{', '.join(e.name for e in self.enum_list)}], \nRelations = [{', '.join(str(r) for r in self.relation_list)}])"

    def __str__(self):
        return f"UMLModel(Classes: {len(self.class_list)}, Enums: {len(self.enum_list)}, Relations: {len(self.relation_list)})"
    
    def to_plantuml(self) -> str:
        lines = ["@startuml", "skinparam Linetype ortho", "skinparam nodesep 100", "skinparam ranksep 100", "hide empty attributes", "hide empty methods"]

        for cls in self.class_list:
            lines.append(cls.to_plantuml())

        for enm in self.enum_list:
            lines.append(enm.to_plantuml())

        for rel in self.relation_list:
            lines.append(rel.to_plantuml())

        lines.append("@enduml")
        return '\n'.join(lines)
    
    def assign_relations(self):
        for relation in self.relation_list:
            if isinstance(relation.source, UMLElement) and isinstance(relation.destination, UMLElement):
                UMLModel.find_element(self, relation.source.name).add_relation(relation)
                if not relation.directed:
                    UMLModel.find_element(self, relation.destination.name).add_relation(relation.swap_source_destination())

    def find_element(self, element_name: str) -> Optional[UMLElement]:
        return self.element_lookup.get(element_name.lower().strip())
    
    def find_class(self, class_name: str) -> Optional[UMLClass]:
        return self.class_lookup.get(class_name.lower().strip())
    
    def find_enum(self, enum_name: str) -> Optional[UMLEnum]:
        return self.enum_lookup.get(enum_name.lower().strip())
    
    def find_relation(self, relation_name: str) -> Optional[UMLRelation]:
        return self.relation_lookup.get(relation_name.lower().strip())

    def build_reachability_map(self) -> Dict[UMLElement, List[UMLElement]]:
        cls_enum_list = self.class_list + self.enum_list
        adjacency_reach_map: Dict[UMLElement, List[UMLElement]] = {elem: [] for elem in cls_enum_list}
        elem_relations: List[UMLRelation] = [relation for relation in self.relation_list if isinstance(relation.source, (UMLClass, UMLEnum)) and isinstance(relation.destination, (UMLClass, UMLEnum))]
        for relation in elem_relations:
            adjacency_reach_map[relation.source].append(relation.destination)
            if not relation.directed:
                adjacency_reach_map[relation.destination].append(relation.source)
        
        def dfs(elm: UMLElement, visited: Set[UMLElement]):
            for neighbor in adjacency_reach_map.get(elm, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    dfs(neighbor, visited)

        reach_map: Dict[UMLElement, List[UMLElement]] = {}
        for elm in cls_enum_list:
            visited: Set[UMLElement] = set()
            visited.add(elm)
            dfs(elm, visited)
            reachable = list(visited - {elm})
            has_self_relation = any(
                rel.source == elm and rel.destination == elm
                for rel in self.relation_list
            )
            if has_self_relation:
                reachable.append(elm)
            reach_map[elm] = reachable

        return reach_map

    def print_details(self):
        term_width = shutil.get_terminal_size((80, 20)).columns  - 10
        print("**UMLModel Details:**")
        print("\t**Class list:**")
        for cls in self.class_list:
            prefix = f"{cls}: "
            details = f"{prefix}{cls.attributes}, {cls.operations}, {cls.relations}"
            indent = '\t\t' + ' ' * len(prefix)
            wrapped = textwrap.fill(
                details,
                width=term_width,
                initial_indent='\t\t',
                subsequent_indent=indent
            )
            print(wrapped)

        print("\t**Enum list:**")
        for enm in self.enum_list:
            prefix = f"{enm}: "
            details = f"{prefix}{enm.values}"
            indent = '\t\t' + ' ' * len(prefix)
            wrapped = textwrap.fill(
                details,
                width=term_width,
                initial_indent='\t\t',
                subsequent_indent=indent
            )
            print(wrapped)

        print("\t**Relation list:**")
        for rel in self.relation_list:
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

        print("\n")


