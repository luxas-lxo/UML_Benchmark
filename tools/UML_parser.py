from UML_model.uml_class import UMLClass, UMLAttribute, UMLOperation, UMLVisability, UMLDataType
from UML_model.uml_relation import UMLRelation, UMLRelationType
from UML_model.uml_enum import UMLEnum, UMLValue
from UML_model.uml_element import UMLElement

import re
import regex
from typing import List, Dict
import logging 

logger = logging.getLogger("uml.parser")
logger.setLevel(logging.INFO)

class UMLParser:
    
    @staticmethod
    def parse_attribute(line: str) -> UMLAttribute:

        attr_pattern = regex.compile(
            r'^\s*(?P<visibility>[+#\-~])?\s*(?P<derived>/)?(?P<name>\w+)\s*(?::\s*(?P<type>\w+))?\s*(?:=\s*(?P<initial>.+))?$'
        )

        try:
            match = attr_pattern.match(line, timeout = 10)  
        except regex.TimeoutError:
            raise ValueError(f"Regex timeout beim Parsen der Attribut-Zeile: '{line}'")

        if not match:
            raise ValueError(f"Ungültiges Attribut-Format: '{line}'")

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

        return UMLAttribute(
            name=name,
            data_type=datatype,
            initial=initial.strip(),
            visibility=visability,
            derived=derived
        )

    @staticmethod
    def parse_operation(line: str) -> UMLOperation:
        import regex

        operation_pattern = regex.compile(
            r'^(?P<visibility>[+#\-~])?\s*(?P<name>\w+)\s*\((?P<params>[^)]*)\)\s*(?::\s*(?P<return_type>[\w<>, ]+))?$'
        )

        try:
            match = operation_pattern.match(line, timeout = 10)
        except regex.TimeoutError:
            raise ValueError(f"Regex timeout beim Parsen der Operation-Zeile: '{line}'")

        if not match:
            raise ValueError(f"Ungültiges Operation-Format: '{line}'")

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

        params = {}
        if param_str:
            for param in param_str.split(","):
                param = param.strip()
                if ":" in param:
                    pname, ptype = map(str.strip, param.split(":", 1))
                    params[pname] = UMLDataType.from_string(ptype)
                else:
                    params[param] = UMLDataType.UNKNOWN

        return_types = [UMLDataType.from_string(t.strip()) for t in return_type_str.split(",")]
        return UMLOperation(name=name, params=params, return_types=return_types, visibility=visability)

    @staticmethod
    def parse_plantuml_classes(uml_text: str) -> List[UMLClass]:

        class_pattern = re.compile(r'class\s+(\w+)(?:\s+[aA][sS]\s+"[^"]*")?\s*(?:\{\s*([^}]*)\})?', re.MULTILINE | re.DOTALL)
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
        enum_pattern = re.compile(r'enum\s+(\w+)(?:\s+[aA][sS]\s+"[^"]*")?\s*(?:\{\s*([^}]*)\})?', re.MULTILINE | re.DOTALL)
        enums = []

        for match in enum_pattern.finditer(uml_text):
            name = match.group(1)
            body = match.group(2) or ""
            lines = [line.strip() for line in body.strip().splitlines() if line.strip()]
            values = [UMLValue(line) for line in lines]
            enums.append(UMLEnum(name, values)) 

        return enums
    
    @staticmethod
    def parse_relation_left_to_right(uml_text: str, type_map: Dict[str, UMLRelationType], element_lookup: Dict[str, UMLElement], relations: List[UMLRelation]):
        # 1.1.1) A m1 -> m2 B : desc
        bin_pattern_1 = re.compile(
            r'(\w+)\s+"([^"]*)"\s+(--|--\*|--o)\s+"([^"]*)"\s+(\w+)(?:\s*:\s*(.*))?',
            re.MULTILINE
        )
        for match in bin_pattern_1.finditer(uml_text):
            raw_a, raw_m1, raw_type, raw_m2, raw_b, desc = match.groups()
            a = raw_a
            b = raw_b

            if a in element_lookup and b in element_lookup:
                rel_type = type_map.get(raw_type.strip(), UMLRelationType.UNKNOWN)
                m1 = raw_m1.strip()
                m2 = raw_m2.strip()
                description = desc.strip() if desc else ""
                relation = UMLRelation(
                    type=rel_type,
                    source=element_lookup[a],
                    destination=element_lookup[b],
                    s_multiplicity=m1,
                    d_multiplicity=m2,
                    description=description
                )
                if relation not in relations:
                    relations.append(relation)
            else:
                logger.warning(f"relation between '{a}' and '{b}' could not be created, as one of the elements was not found.")

        # 1.1.2) A -> B : desc
        bin_pattern_2 = re.compile(
            r'(\w+)\s+(--|--\*|--o)\s+(\w+)(?:\s*:\s*(.*))?',
            re.MULTILINE
        )

        for match in bin_pattern_2.finditer(uml_text):
            raw_a, raw_type, raw_b, desc = match.groups()
            a = raw_a
            b = raw_b

            if a in element_lookup and b in element_lookup:
                rel_type = type_map.get(raw_type.strip(), UMLRelationType.UNKNOWN)
                description = desc.strip() if desc else ""
                relation = UMLRelation(
                    type=rel_type,
                    source=element_lookup[a],
                    destination=element_lookup[b],
                    description=description
                )
                if relation not in relations:
                    relations.append(relation)
            else:
                logger.warning(f"relation between '{a}' and '{b}' could not be created, as one of the elements was not found.")

    @staticmethod
    def parse_relation_right_to_left(uml_text: str, type_map: Dict[str, UMLRelationType], element_lookup: Dict[str, UMLElement], relations: List[UMLRelation]):
        # 1.2.1) A m1 <- m2 B : desc
        bin_pattern_3 = re.compile(
            r'(\w+)\s+"([^"]*)"\s+(\*--|o--)\s+"([^"]*)"\s+(\w+)(?:\s*:\s*(.*))?',
            re.MULTILINE
        )
        for match in bin_pattern_3.finditer(uml_text):
            raw_a, raw_m1, raw_type, raw_m2, raw_b, desc = match.groups()
            a = raw_a
            b = raw_b

            if a in element_lookup and b in element_lookup:
                rel_type = type_map.get(raw_type.strip(), UMLRelationType.UNKNOWN)
                m1 = raw_m1.strip()
                m2 = raw_m2.strip()
                description = desc.strip() if desc else ""
                relation = UMLRelation(
                    type=rel_type,
                    source=element_lookup[b],
                    destination=element_lookup[a],
                    s_multiplicity=m2,
                    d_multiplicity=m1,
                    description=description
                )
                if relation not in relations:
                    relations.append(relation)
            else:
                logger.warning(f"relation between '{a}' and '{b}' could not be created, as one of the elements was not found.")

        # 1.2.2) A <- B : desc
        bin_pattern_4 = re.compile(
            r'(\w+)\s+(\*--|o--)\s+(\w+)(?:\s*:\s*(.*))?',
            re.MULTILINE
        )

        for match in bin_pattern_4.finditer(uml_text):
            raw_a, raw_type, raw_b, desc = match.groups()
            a = raw_a
            b = raw_b

            if a in element_lookup and b in element_lookup:
                rel_type = type_map.get(raw_type.strip(), UMLRelationType.UNKNOWN)
                description = desc.strip() if desc else ""
                relation = UMLRelation(
                    type=rel_type,
                    source=element_lookup[b],
                    destination=element_lookup[a],
                    description=description
                )
                if relation not in relations:
                    relations.append(relation)
            else:
                logger.warning(f"relation between '{a}' and '{b}' could not be created, as one of the elements was not found.")

    @staticmethod 
    def parse_asso_class_left_to_right(uml_text: str, element_lookup: Dict[str, UMLElement], relations: List[UMLRelation]):
        
        assoc_pattern_1 = re.compile(r'(\w+)\s*\.\.\s*\(\s*(\w+)\s*,\s*(\w+)\s*\)')
        for match in assoc_pattern_1.finditer(uml_text):
            raw_c, raw_a, raw_b = match.groups()
            a = raw_a
            b = raw_b
            c = raw_c
            if all(x in element_lookup for x in (a, b, c)):
                rel = None
                for r in relations:
                    if r.equals(UMLRelation(UMLRelationType.ASSOCIATION, element_lookup[a], element_lookup[b])):
                        rel = r
                        break
                relation = UMLRelation(type = UMLRelationType.ASSOCIATION_LINK, source = element_lookup[c], destination = rel)
                if relation not in relations:
                    relations.append(relation)
            else:
                # NOTE: maybe later create classes if not found
                logger.warning(f"relation between '{a}', '{b}' and '{c}' could not be created, as one of the elements was not found.")

    @staticmethod
    def parse_asso_class_right_to_left(uml_text: str, element_lookup: Dict[str, UMLElement], relations: List[UMLRelation]):
        # 2.2) (A, B) .. C
        assoc_pattern_2 = re.compile(r'\(\s*(\w+)\s*,\s*(\w+)\s*\)\s*\.\.\s*(\w+)')
        for match in assoc_pattern_2.finditer(uml_text):
            raw_a, raw_b, raw_c = match.groups()
            a = raw_a
            b = raw_b
            c = raw_c
            if all(x in element_lookup for x in (a, b, c)):
                rel = None
                for r in relations:
                    if r.equals(UMLRelation(UMLRelationType.ASSOCIATION, element_lookup[a], element_lookup[b])):
                        rel = r
                        break
                relation = UMLRelation(type = UMLRelationType.ASSOCIATION_LINK, source = element_lookup[c], destination = rel)
                if relation not in relations:
                    relations.append(relation)
            else:
                # NOTE: maybe later create classes if not found
                logger.warning(f"relation between '{a}', '{b}' and '{c}' could not be created, as one of the elements was not found.")

    @staticmethod
    def parse_plantuml_relations(uml_text: str, classes: List[UMLClass], enums: List[UMLEnum]) -> List[UMLRelation]:
        relations: List[UMLRelation] = []
        class_lookup: Dict[str, UMLClass] = {cls.name: cls for cls in classes}
        enum_lookup: Dict[str, UMLEnum] = {enu.name: enu for enu in enums}
        element_lookup = class_lookup | enum_lookup
        type_map = {
                '--': UMLRelationType.ASSOCIATION,
                'o--': UMLRelationType.AGGREGATION,
                '--o': UMLRelationType.AGGREGATION,
                '*--': UMLRelationType.COMPOSITION,
                '--*': UMLRelationType.COMPOSITION
            }
        
        # 1) binary relation with type matching (assoziation, aggregation, komposition)
        # 1.1) ->
        # 1.1.1) A m1 -> m2 B
        # 1.1.2) A -> B
        UMLParser.parse_relation_left_to_right(uml_text, type_map, element_lookup, relations)
        
        # 1.2) <-
        # 1.2.1) A m1 <- m2 B
        # 1.2.2) A <- B
        UMLParser.parse_relation_right_to_left(uml_text, type_map, element_lookup, relations)
        
        # 2.) association class
        # 2.1) C .. (A, B)
        UMLParser.parse_asso_class_left_to_right(uml_text, element_lookup, relations)
        # 2.2) (A, B) .. C
        UMLParser.parse_asso_class_right_to_left(uml_text, element_lookup, relations)
        return relations