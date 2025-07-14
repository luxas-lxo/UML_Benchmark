from UML_model.uml_class import UMLClass, UMLAttribute, UMLOperation, UMLVisibility, UMLDataType
from UML_model.uml_relation import UMLRelation, UMLRelationType
from UML_model.uml_enum import UMLEnum, UMLValue
from UML_model.uml_element import UMLElement
from tools.syntactic_check import SyntacticCheck

import re
import regex
from typing import List, Dict, Optional
import logging 

logger = logging.getLogger("uml.parser")
logger.setLevel(logging.INFO)

class UMLParser:
    
    @staticmethod
    def parse_attribute(line: str) -> Optional[UMLAttribute]:
        if not line or line.strip() == "":
            return None

        attr_pattern = regex.compile(
            r'^\s*(?P<visibility>[+#\-~])?\s*(?P<derived>/)?(?P<name>\w+)?\s*(?::\s*(?P<type>\w+))?\s*(?:=\s*(?P<initial>.+))?$'
        )

        try:
            match = attr_pattern.match(line, timeout = 10)  
        except regex.TimeoutError:
            raise ValueError(f"Regex timeout while parsing attribute line: '{line}'")

        if not match:
            logger.warning(f"Invalid attribute format in line: '{line}'")
            return None
        
        name = match.group("name") or ""
        if name.strip() == "":
            logger.warning("Attribute name not specified, setting to '--error--'.")
            name = "--error--"
        derived = bool(match.group("derived"))
        vis_symbol = match.group("visibility") or ""
        visibility = UMLVisibility.from_string(vis_symbol)

        if match.group("type") is not None and match.group("type").strip() == "":
            logger.warning(f"Data type not specified for attribute '{name}', setting data type to UMLDataType.ERROR due to syntax error.")
            datatype = UMLDataType.ERROR
        else:
            datatype_str = match.group("type") or ""
            datatype = UMLDataType.from_string(datatype_str)

        if match.group("initial") is not None and match.group("initial").strip() == "":
            logger.warning(f"Initial value not specified for attribute '{name}', syntax error.")    
            initial = "--error--"
        else:
            initial = match.group("initial").strip() if match.group("initial") else ""

        return UMLAttribute(name=name, data_type=datatype, initial=initial, visibility=visibility, derived=derived)

    #TODO: ()
    @staticmethod
    def parse_operation(line: str) -> UMLOperation:
        operation_pattern = regex.compile(
            r'^(?P<visibility>[+#\-~])?\s*(?P<name>\w+)?\s*\((?P<params>[^)]*)\)\s*(?::\s*(?P<return_type>[\w<>, ]+))?$'
        )

        try:
            match = operation_pattern.match(line, timeout = 10)
        except regex.TimeoutError:
            raise ValueError(f"Regex timeout while parsing operation line: '{line}'")

        if not match:
            raise ValueError(f"Invalid operation format: '{line}'")

        vis_symbol = match.group("visibility") or ""
        visibility = UMLVisibility.from_string(vis_symbol)

        name = match.group("name") or ""
        if name.strip() == "":
            logger.warning("Operation name not specified, setting to '--error--'.")
            name = "--error--"
        param_str = match.group("params").strip()
        return_type_str = (match.group("return_type") or "void").strip()

        params: Dict[str, UMLDataType] = {}
        if param_str:
            for param in param_str.split(","):
                param = param.strip()
                if ":" in param:
                    pname, ptype = map(str.strip, param.split(":", 1))
                    if ptype.strip() == "":
                        logger.warning(f"Data type not specified for parameter '{pname}', setting data type to UMLDataType.ERROR due to syntax error.")
                        params[pname] = UMLDataType.ERROR
                    else:
                        params[pname] = UMLDataType.from_string(ptype)
                else:
                    params[param] = UMLDataType.UNKNOWN

        if return_type_str is not None and return_type_str.strip() == "":
            logger.warning(f"Return type not specified for operation '{name}', setting return type to UMLDataType.ERROR due to syntax error.")
            return_types = [UMLDataType.ERROR]
        else:
            return_types = [UMLDataType.from_string(t.strip()) if t.strip() != "" else UMLDataType.ERROR for t in return_type_str.split(",")]
            if UMLDataType.ERROR in return_types:
                logger.warning(f"Invalid return type(s) for operation '{name}', setting to UMLDataType.ERROR due to syntax error.")

        return UMLOperation(name=name, params=params, return_types=return_types, visibility=visibility)

    @staticmethod
    def parse_plantuml_classes(uml_text: str) -> List[UMLClass]:
        class_pattern = re.compile(
            r'class\s+(?P<name>\w+)?(?:\s+[aA][sS]\s+"[^"]*")?\s*(?:\{\s*(?P<body>[^}]*)\})?',
            re.MULTILINE | re.DOTALL
        )
        classes = []

        for match in class_pattern.finditer(uml_text):
            name = match.group("name") or ""
            if name.strip() == "":
                logger.warning("Class name not specified, setting to '--error--'.")
                name = "--error--"
            body = match.group("body") or ""
            lines = [line.strip() for line in body.strip().splitlines() if line.strip()]
            attributes = []
            for line in lines:
                if "(" not in line and ")" not in line:
                    attr = UMLParser.parse_attribute(line)
                    if attr is not None:
                        attributes.append(attr)
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
    
    # TODO: parse role names
    @staticmethod
    def parse_relation_left_to_right(uml_text: str, type_map: Dict[str, UMLRelationType], element_lookup: Dict[str, UMLElement], relations: List[UMLRelation]):
        #1.1) A "m1" -> "m2" B : desc
        bin_pattern = re.compile(
            r'(?P<a>\w\w+)\s*(?:"(?P<m1>[^"]*)")?\s*(?P<type>-{1,2}[\w\*\|\<\>]{0,2})\s*(?:"(?P<m2>[^"]*)")?\s*(?P<b>\w+)(?:\s*:\s*(?P<desc>.*))?'
        )
        for match in bin_pattern.finditer(uml_text):
            a = match.group("a")
            b = match.group("b")
            m1 = match.group("m1") or ""
            m2 = match.group("m2") or ""
            description = match.group("desc").strip() if match.group("desc") else ""

            if a in element_lookup and b in element_lookup:
                rel_type = type_map.get(match.group("type"), UMLRelationType.UNKNOWN)
                if m1 != " " and not SyntacticCheck.is_valid_multiplicity(m1):
                    logger.warning(f"Multiplicity for source in relation '{a} {match.group('type')} {b}' is invalid, setting m1 to '--error--'.")
                    m1 = "--error--"
                if m2 != " " and not SyntacticCheck.is_valid_multiplicity(m2):
                    logger.warning(f"Multiplicity for destination in relation '{a} {match.group('type')} {b}' is invalid, setting m2 to '--error--'.")
                    m2 = "--error--"
                if match.group("desc") is not None and match.group("desc").strip() == "":
                    logger.warning(f"Description for relation '{a} {match.group('type')} {b}' is empty, setting to '--error--'.")
                    description = "--error--" 

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
                #NOTE: maybe later create classes if not found since this works in PlantUML
                logger.warning(f"relation between '{a}' and '{b}' could not be created, as one of the elements was not found.")

    @staticmethod
    def parse_relation_right_to_left(uml_text: str, type_map: Dict[str, UMLRelationType], element_lookup: Dict[str, UMLElement], relations: List[UMLRelation]):
        # 1.2) A "m1" <- "m2" B : desc
        bin_pattern = re.compile(
            r'(?P<a>\w+)\s*(?:"(?P<m1>[^"]*)")?\s*(?P<type>[\w\*\|\<\>]{1,2}-{1,2})\s*(?:"(?P<m2>[^"]*)")?\s*(?P<b>\w+)(?:\s*:\s*(?P<desc>.*))?'
        )
        for match in bin_pattern.finditer(uml_text):
            a = match.group("a")
            b = match.group("b")
            m1 = match.group("m1") or ""
            m2 = match.group("m2") or ""
            rel_type = type_map.get(match.group("type"), UMLRelationType.UNKNOWN)
            description = match.group("desc").strip() if match.group("desc") else ""

            if a in element_lookup and b in element_lookup:
                # Multiplicity validation
                if m1 != " " and not SyntacticCheck.is_valid_multiplicity(m1):
                    logger.warning(f"Multiplicity for source in relation '{a} {match.group('type')} {b}' is invalid, setting to m1 '--error--'.")
                    m1 = "--error--"
                if m2 != " " and not SyntacticCheck.is_valid_multiplicity(m2):
                    logger.warning(f"Multiplicity for destination in relation '{a} {match.group('type')} {b}' is invalid, setting m2 to '--error--'.")
                    m2 = "--error--"
                if match.group("desc") is not None and match.group("desc").strip() == "":
                    logger.warning(f"Description for relation '{a} {match.group('type')} {b}' is empty, setting to '--error--'.")
                    description = "--error--"

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

    @staticmethod 
    def parse_asso_class_left_to_right(uml_text: str, element_lookup: Dict[str, UMLElement], relations: List[UMLRelation]):
        # 2.1) C .. (A, B)
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