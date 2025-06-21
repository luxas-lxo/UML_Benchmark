from UML_model.uml_class import UMLClass, UMLAttribute, UMLOperation, UMLVisability, UMLDataType
from UML_model.uml_relation import UMLRelation, RelationType
from UML_model.uml_enum import UMLEnum, UMLValue

import re
from typing import List

class UMLParser:
    
    @staticmethod
    def parse_attribute(line: str) -> UMLAttribute:
        attr_pattern = re.compile(r'^\s*(?P<visibility>[+#\-~])?\s*(?P<derived>/)?(?P<name>\w+)\s*(?:[:]\s*(?P<type>\w+))?\s*(?:=\s*(?P<initial>.+))?$')

        match = attr_pattern.match(line)
        if not match:
            raise ValueError(f"Invalid attribute format: '{line}'")

        vis_symbol = match.group("visibility") or ""
        vis_map = {
            '+': UMLVisability.PUBLIC,
            '-': UMLVisability.PRIVATE,
            '#': UMLVisability.PROTECTED,
            '~': UMLVisability.PACKAGE
        }
        visability = vis_map.get(vis_symbol.strip(), UMLVisability.UNKNOWN)

        name = match.group("name")
        derived = bool(match.group("derived"))
        datatype_str = match.group("type") or "unknown"
        datatype = UMLDataType.from_string(datatype_str)
        initial = match.group("initial") or ""

        attr = UMLAttribute(name=name, datatype=datatype, initial=initial.strip(), visability=visability, derived=derived)
        return attr

    @staticmethod
    def parse_operation(line: str) -> UMLOperation:
        operation_pattern = re.compile(r'^(?P<visibility>[+#\-~])?\s*(?P<name>\w+)\s*\((?P<params>[^)]*)\)\s*(?:[:]\s*(?P<return_type>[\w<>, ]+))?$')

        match = operation_pattern.match(line)
        if not match:
            raise ValueError(f"Invalid operation format: '{line}'")
        
        vis_symbol = match.group("visibility") or ""
        vis_map = {
            '+': UMLVisability.PUBLIC,
            '-': UMLVisability.PRIVATE,
            '#': UMLVisability.PROTECTED,
            '~': UMLVisability.PACKAGE
        }
        visability = vis_map.get(vis_symbol.strip(), UMLVisability.UNKNOWN)

        name = match.group("name")
        param_str = match.group("params").strip()
        return_type_str = (match.group("return_type") or "void").strip()

        # Parameter parsen
        params = {}
        if param_str:
            for param in param_str.split(","):
                param = param.strip()
                if ":" in param:
                    pname, ptype = map(str.strip, param.split(":", 1))
                    params[pname] = UMLDataType.from_string(ptype)
                else:
                    params[param] = UMLDataType.UNKNOWN

        # Rückgabetyp(en) parsen
        return_types = [UMLDataType.from_string(t.strip()) for t in return_type_str.split(",")]
        return UMLOperation(name=name, params=params, return_types=return_types, visability=visability)

    @staticmethod
    def parse_plantuml_classes(uml_text: str) -> List[UMLClass]:
        # TODO: falls später notwendig hier oder in UMLClass die datentypen/visability/parameter/rückgabetypen extrahieren

        class_pattern = re.compile(r'class\s+(\w+)(?:\s+as\s+"[^"]*")?\s*(?:\{\s*([^}]*)\})?', re.MULTILINE | re.DOTALL)
        classes = []

        for match in class_pattern.finditer(uml_text):
            name = match.group(1)
            body = match.group(2) or ""
            lines = [line.strip() for line in body.strip().splitlines() if line.strip()]
            attributes = [UMLParser.parse_attribute(line) for line in lines if "(" not in line and ")" not in line]
            operations = [UMLParser.parse_operation(line) for line in lines if "(" in line and ")" in line]
            classes.append(UMLClass(name, attributes, operations)) 

        return classes
    
    @staticmethod
    def parse_plantuml_enums(uml_text: str) -> List[UMLEnum]:
        class_pattern = re.compile(r'enum\s+(\w+)(?:\s+as\s+"[^"]*")?\s*\{\s*([^}]*)\}', re.MULTILINE | re.DOTALL)
        enums = []

        for match in class_pattern.finditer(uml_text):
            name = match.group(1)
            body = match.group(2) or ""
            lines = [line.strip() for line in body.strip().splitlines() if line.strip()]
            values = [UMLValue(line) for line in lines]
            enums.append(UMLEnum(name, values)) 

        return enums
    
    @staticmethod
    def parse_plantuml_relations(uml_text: str, classes: List[UMLClass], enums: List[UMLEnum]) -> List[UMLRelation]:
        relations: List[UMLRelation] = []
        class_lookup = {cls.name: cls for cls in classes}
        enum_lookup = {enu.name: enu for enu in enums}
        element_lookup = class_lookup | enum_lookup
        type_map = {
                '--': RelationType.ASSOCIATION,
                'o--': RelationType.AGGREGATION,
                '--o': RelationType.AGGREGATION,
                '*--': RelationType.COMPOSITION,
                '--*': RelationType.COMPOSITION
            }
        
        # 1) Binäre Relationen mit Typbestimmung (assoziation, aggregation, komposition)
        # 1aa) A m1 -> m2 B
        bin_pattern1 = re.compile(
            r'(\w+)\s+"([^"]*)"\s+(--|--\*|--o)\s+"([^"]*)"\s+(\w+)',
            re.MULTILINE
        )
        for match in bin_pattern1.finditer(uml_text):
            raw_a, raw_m1, raw_type, raw_m2, raw_b = match.groups()
            a = raw_a
            b = raw_b

            if a in element_lookup and b in element_lookup:
                rel_type = type_map.get(raw_type.strip(), RelationType.UNKNOWN)
                m1 = raw_m1.strip()
                m2 = raw_m2.strip()
                relation = UMLRelation(
                    type = rel_type, 
                    source = element_lookup[a], 
                    destination = element_lookup[b], 
                    s_multiplicity = m1, 
                    d_multiplicity = m2
                )
                relations.append(relation)
        
        # 1ab) Einfache Relationen ohne Multiplikitäten: A -> B
        bin_pattern_simple1 = re.compile(
            r'(\w+)\s+(--|--\*|--o)\s+(\w+)',
            re.MULTILINE
        )

        for match in bin_pattern_simple1.finditer(uml_text):
            raw_a, raw_type, raw_b = match.groups()
            a = raw_a
            b = raw_b

            if a in element_lookup and b in element_lookup:
                rel_type = type_map.get(raw_type.strip(), RelationType.UNKNOWN)
                relation = UMLRelation(
                    type=rel_type,
                    source=element_lookup[a],
                    destination=element_lookup[b]
                )
                if relation not in relations:
                    relations.append(relation)

        # 1ba) A <- B
        bin_pattern2 = re.compile(
            r'(\w+)\s+"([^"]*)"\s+(--|\*--|o--)\s+"([^"]*)"\s+(\w+)',
            re.MULTILINE
        )
        for match in bin_pattern2.finditer(uml_text):
            raw_a, raw_m1, raw_type, raw_m2, raw_b = match.groups()
            a = raw_a
            b = raw_b

            if a in element_lookup and b in element_lookup:
                rel_type = type_map.get(raw_type.strip(), RelationType.UNKNOWN)
                m1 = raw_m1.strip()
                m2 = raw_m2.strip()
                relation = UMLRelation(
                    type = rel_type, 
                    source = element_lookup[b], 
                    destination = element_lookup[a], 
                    s_multiplicity = m2, 
                    d_multiplicity = m1
                )                
                if relation not in relations:
                    relations.append(relation)

        # 1bb) Einfache Relationen ohne Multiplikitäten: A <- B
        bin_pattern_simple1 = re.compile(
            r'(\w+)\s+(--|\*--|--o)\s+(\w+)',
            re.MULTILINE
        )

        for match in bin_pattern_simple1.finditer(uml_text):
            raw_a, raw_type, raw_b = match.groups()
            a = raw_a
            b = raw_b

            if a in element_lookup and b in element_lookup:
                rel_type = type_map.get(raw_type.strip(), RelationType.UNKNOWN)
                relation = UMLRelation(
                    type=rel_type,
                    source=element_lookup[b],
                    destination=element_lookup[a]
                )
                if relation not in relations:
                    relations.append(relation)

        # 2a) Assoziationsklassen: (A, B) .. C
        assoc_pattern1 = re.compile(r'\(\s*(\w+)\s*,\s*(\w+)\s*\)\s*\.\.\s*(\w+)')
        for match in assoc_pattern1.finditer(uml_text):
            raw_a, raw_b, raw_c = match.groups()
            a = raw_a
            b = raw_b
            c = raw_c
            if all(x in element_lookup for x in (a, b, c)):
                rel = None
                for r in relations:
                    if r.equals(UMLRelation(RelationType.ASSOCIATION, element_lookup[a], element_lookup[b])):
                        rel = r
                        break
                relation = UMLRelation(type = RelationType.ASSOCIATION_LINK, source = element_lookup[c], destination = rel)
                if relation not in relations:
                    relations.append(relation)

        # 2b) Assoziationsklassen: C .. (A, B)
        assoc_pattern2 = re.compile(r'(\w+)\s*\.\.\s*\(\s*(\w+)\s*,\s*(\w+)\s*\)')
        for match in assoc_pattern2.finditer(uml_text):
            raw_c, raw_a, raw_b = match.groups()
            a = raw_a
            b = raw_b
            c = raw_c
            if all(x in element_lookup for x in (a, b, c)):
                rel = None
                for r in relations:
                    if r.equals(UMLRelation(RelationType.ASSOCIATION, element_lookup[a], element_lookup[b])):
                        rel = r
                        break
                relation = UMLRelation(type = RelationType.ASSOCIATION_LINK, source = element_lookup[c], destination = rel)
                if relation not in relations:
                    relations.append(relation)

        return relations