from UML_model.uml_class import UMLClass, UMLAttribute, UMLOperation
from UML_model.uml_enum import UMLEnum, UMLValue
from tools.semantic_check import SemanticCheck
from tools.syntactic_check import SyntacticCheck

from typing import Tuple, Dict
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
    def class_content_match(inst_class: UMLClass, stud_class: UMLClass, threshold: float = 0.5) -> Tuple[bool, float]:
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
    
    @staticmethod
    def classes_have_same_properties(inst_class: UMLClass, stud_class_1: UMLClass, stud_class_2: UMLClass, attr_match_map: Dict[UMLAttribute, UMLAttribute], misplaced_attr_map: Dict[UMLAttribute, UMLAttribute], oper_matched_map: Dict[UMLOperation, UMLOperation], misplaced_oper_map: Dict[UMLOperation, UMLOperation]) -> bool:
        """
        Check if the instructor class has the same properties as the two student classes.
        This means that the instructor class has attributes and operations that are mapped to the student classes.
        NOTE: This does only check for true equality, not for similarity.
        This could be extended later if needed.
        """

        logger.debug(f"Comparing instructor class {str(inst_class)} with student classes {str(stud_class_1)} and {str(stud_class_2)} for same properties")
        # all instructor attributes that are mapped to any student attribute
        inst_attributes = {att for att in inst_class.attributes if att in attr_match_map.keys() or att in misplaced_attr_map.keys()}
        inst_operations = {opr for opr in inst_class.operations if opr in oper_matched_map.keys() or opr in misplaced_oper_map.keys()}

        if not inst_attributes and not inst_operations:
            logger.debug(f"comparing instructor class {str(inst_class)} failed, because it has no mapped attributes and operations")
            return False

        # all student attributes that are mapped to any instructor attribute
        stud_attributes_1 = {att for att in stud_class_1.attributes if att in attr_match_map.values() or att in misplaced_attr_map.values()}
        stud_attributes_2 = {att for att in stud_class_2.attributes if att in attr_match_map.values() or att in misplaced_attr_map.values()}

        # all student operations that are mapped to any instructor operation
        stud_operations_1 = {opr for opr in stud_class_1.operations if opr in oper_matched_map.values() or opr in misplaced_oper_map.values()}
        stud_operations_2 = {opr for opr in stud_class_2.operations if opr in oper_matched_map.values() or opr in misplaced_oper_map.values()}

        if not stud_attributes_1 and not stud_operations_1 or not stud_attributes_2 and not stud_operations_2:
            logger.debug(f"comparing instructor class {str(inst_class)} failed, because at least one student class has no mapped attributes and operations")
            return False
        
        # all student attributes that are mapped to the instructor attributes
        mapped_stud_attributes_1 = {inst_att for inst_att, stud_att in attr_match_map.items() if stud_att in stud_attributes_1 and inst_att in inst_attributes} | {inst_att for inst_att, stud_att in misplaced_attr_map.items() if stud_att in stud_attributes_1 and inst_att in inst_attributes}
        mapped_stud_attributes_2 = {inst_att for inst_att, stud_att in attr_match_map.items() if stud_att in stud_attributes_2 and inst_att in inst_attributes} | {inst_att for inst_att, stud_att in misplaced_attr_map.items() if stud_att in stud_attributes_2 and inst_att in inst_attributes}

        # all student operations that are mapped to the instructor operations
        mapped_stud_operations_1 = {inst_opr for inst_opr, stud_opr in oper_matched_map.items() if stud_opr in stud_operations_1 and inst_opr in inst_operations} | {inst_opr for inst_opr, stud_opr in misplaced_oper_map.items() if stud_opr in stud_operations_1 and inst_opr in inst_operations}
        mapped_stud_operations_2 = {inst_opr for inst_opr, stud_opr in oper_matched_map.items() if stud_opr in stud_operations_2 and inst_opr in inst_operations} | {inst_opr for inst_opr, stud_opr in misplaced_oper_map.items() if stud_opr in stud_operations_2 and inst_opr in inst_operations}

        if not mapped_stud_attributes_1 and not mapped_stud_operations_1 or not mapped_stud_attributes_2 and not mapped_stud_operations_2:
            logger.debug(f"comparing instructor class {str(inst_class)} failed, because at least one student class has no mapped attributes and operations to the instructor class")
            return False
        
        # check if the mapped attributes and operations are the same
        if inst_attributes == (mapped_stud_attributes_1 | mapped_stud_attributes_2) and inst_operations == (mapped_stud_operations_1 | mapped_stud_operations_2):
            logger.debug(f"comparing instructor class {str(inst_class)} with student classes {str(stud_class_1)} and {str(stud_class_2)} succeeded")
            return True
        else:
            # should not happen, but just in case
            logger.debug(f"comparing instructor class {str(inst_class)} with student classes {str(stud_class_1)} and {str(stud_class_2)} failed, because the mapped attributes and operations are not the same")
            return False

    @staticmethod
    def class_contains_missplaced_properties(inst_class: UMLClass, stud_class: UMLClass, missplaced_attr_map: Dict[UMLAttribute, UMLAttribute], missplaced_oper_map: Dict[UMLOperation, UMLOperation]) -> bool:
        # Check if the instructor class contains any misplaced properties in the student class
        if any(missplaced_attr_map.get(inst_att) == stud_att for inst_att in inst_class.attributes for stud_att in stud_class.attributes) or any(missplaced_oper_map.get(inst_opr) == stud_opr for inst_opr in inst_class.operations for stud_opr in stud_class.operations):
            logger.debug(f"found misplaced properties between instructor class {str(inst_class)} and student class {str(stud_class)}")
            return True
        return False
    
    @staticmethod
    def enum_content_match(inst_enum: UMLEnum, stud_enum: UMLEnum, threshold: float = 0.5) -> Tuple[bool, float]:
        total = len(inst_enum.values)
        if total == 0:
            return (False, 0)

        match_count = 0

        for inst_value in inst_enum.values:
            for stud_value in stud_enum.values:
                if SyntacticCheck.syntactic_match(inst_value.name, stud_value.name)[0] or SemanticCheck.semantic_match(inst_value.name, stud_value.name)[0]:
                    match_count += 1
                    break

        similarity = match_count / total
        if similarity >= threshold:
            logger.debug(f"Enum content match: {str(inst_enum)} and {str(stud_enum)}: score = {similarity:.2f}")
        return (similarity >= threshold, similarity)
