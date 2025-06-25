from UML_model.uml_class import UMLClass
from tools.semantic_check import SemanticCheck
from tools.syntactic_check import SyntacticCheck

from typing import Tuple
import logging

logger = logging.getLogger("content_check")
logger.setLevel(logging.DEBUG)

if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(levelname)s] - %(name)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

class ContentCheck:
    @staticmethod
    def class_attribute_match(inst_class: UMLClass, stud_class: UMLClass) -> int:
        total = len(inst_class.attributes)
        if total == 0:
            return 0

        match_count = 0

        for inst_att in inst_class.attributes:
            for stud_att in stud_class.attributes:
                if SyntacticCheck.syntactic_match(inst_att.name, stud_att.name)[0] or SemanticCheck.semantic_match(inst_att.name, stud_att.name)[0]:
                    match_count += 1
                    break

        return match_count 
    
    @staticmethod
    def class_operation_match(inst_class: UMLClass, stud_class: UMLClass) -> int:
        total = len(inst_class.operations)
        if total == 0:
            return 0

        match_count = 0

        for inst_opr in inst_class.operations:
            for stud_opr in stud_class.operations:
                if SyntacticCheck.syntactic_match(inst_opr.name, stud_opr.name)[0] or SemanticCheck.semantic_match(inst_opr.name, stud_opr.name)[0]:
                    match_count += 1
                    break
        return match_count

    @staticmethod
    def content_match(inst_class: UMLClass, stud_class: UMLClass, threshold: float = 0.5) -> Tuple[bool, float]:
        total = len(inst_class.attributes) + len(inst_class.operations)
        if total == 0:
            return (False, 0)
        
        match_count = 0

        match_count += ContentCheck.class_attribute_match(inst_class, stud_class)
        match_count += ContentCheck.class_operation_match(inst_class, stud_class)

        similarity = match_count / total
        if similarity >= threshold:
            logger.debug(f"Content match: {str(inst_class)} and {str(stud_class)}: score = {similarity:.2f}")
        return (similarity >= threshold, similarity)
    