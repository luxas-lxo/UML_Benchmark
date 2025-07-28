from UML_model.uml_class import UMLClass, UMLAttribute, UMLOperation
from UML_model.uml_enum import UMLEnum, UMLValue
from tools.semantic_check import SemanticCheck
from tools.syntactic_check import SyntacticCheck

from typing import Tuple, Dict, Union, List
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
    def classes_have_same_properties(inst_class: UMLClass, stud_class_1: UMLClass, stud_class_2: UMLClass, attr_match_map: Dict[UMLAttribute, UMLAttribute], inherited_attr_map: Dict[UMLAttribute, UMLAttribute], misplaced_attr_map: Dict[UMLAttribute, UMLAttribute], oper_matched_map: Dict[UMLOperation, UMLOperation], inherited_oper_map: Dict[UMLOperation, UMLOperation], misplaced_oper_map: Dict[UMLOperation, UMLOperation]) -> bool:
        """
        Check if the instructor class has the same properties as the two student classes.
        This means that the instructor class has attributes and operations that are mapped to the student classes.
        NOTE: This does only check for true equality, not for similarity.
        This could be extended later if needed.
        """

        logger.debug(f"Comparing instructor class {str(inst_class)} with student classes {str(stud_class_1)} and {str(stud_class_2)} for same properties")
        # all instructor attributes that are mapped to any student attribute
        mapped_inst_attributes = {att for att in inst_class.attributes if att in attr_match_map.keys() or att in inherited_attr_map or att in misplaced_attr_map.keys()}
        mapped_inst_operations = {opr for opr in inst_class.operations if opr in oper_matched_map.keys() or opr in inherited_oper_map or opr in misplaced_oper_map.keys()}

        if not inst_class.attributes and not inst_class.operations:
            logger.debug(f"comparing instructor class {str(inst_class)} failed, because it has no attributes and operations")
            return False
        elif not mapped_inst_attributes and not mapped_inst_operations:
            logger.debug(f"comparing instructor class {str(inst_class)} failed, because it has no mapped attributes and operations")
            return False

        # all student attributes that are mapped to any instructor attribute
        mapped_stud_attributes_1 = {
            att for att in stud_class_1.attributes 
            if att in attr_match_map.values() or att in misplaced_attr_map.values()
        } | {
            att for att in inherited_attr_map.values() 
            if stud_class_1.super_class and (att in stud_class_1.super_class.attributes or (stud_class_1.super_class.super_class and att in stud_class_1.super_class.super_class.attributes))
        }
        mapped_stud_attributes_2 = {
            att for att in stud_class_2.attributes 
            if att in attr_match_map.values() or att in misplaced_attr_map.values()
        } | {
            att for att in inherited_attr_map.values() 
            if stud_class_2.super_class and (att in stud_class_2.super_class.attributes or (stud_class_2.super_class.super_class and att in stud_class_2.super_class.super_class.attributes))
        }

        # all student operations that are mapped to any instructor operation
        mapped_stud_operations_1 = {
            opr for opr in stud_class_1.operations 
            if opr in oper_matched_map.values() or opr in misplaced_oper_map.values()
        } | {
            opr for opr in inherited_oper_map.values() 
            if stud_class_1.super_class and (opr in stud_class_1.super_class.operations or (stud_class_1.super_class.super_class and opr in stud_class_1.super_class.super_class.operations))
        }
        mapped_stud_operations_2 = {
                opr for opr in stud_class_2.operations 
                if opr in oper_matched_map.values() or opr in misplaced_oper_map.values()
            } | {
            opr for opr in inherited_oper_map.values() 
            if stud_class_2.super_class and (opr in stud_class_2.super_class.operations or (stud_class_2.super_class.super_class and opr in stud_class_2.super_class.super_class.operations))
        }

        if (not mapped_stud_attributes_1 and not mapped_stud_operations_1) or (not mapped_stud_attributes_2 and not mapped_stud_operations_2):
            logger.debug(f"comparing instructor class {str(inst_class)} failed, because at least one student class has no mapped attributes and operations")
            return False
        
        # all student attributes that are mapped to the instructor attributes
        mapped_to_inst_stud_attributes_1 = {inst_att for inst_att, stud_att in attr_match_map.items() if stud_att in mapped_stud_attributes_1 and inst_att in mapped_inst_attributes
        } | {inst_att for inst_att, stud_att in misplaced_attr_map.items() if stud_att in mapped_stud_attributes_1 and inst_att in mapped_inst_attributes
        } | {inst_att for inst_att, stud_att in inherited_attr_map.items() if stud_att in mapped_stud_attributes_1 and inst_att in mapped_inst_attributes}
        mapped_to_inst_stud_attributes_2 = {inst_att for inst_att, stud_att in attr_match_map.items() if stud_att in mapped_stud_attributes_2 and inst_att in mapped_inst_attributes
        } | {inst_att for inst_att, stud_att in misplaced_attr_map.items() if stud_att in mapped_stud_attributes_2 and inst_att in mapped_inst_attributes
        } | {inst_att for inst_att, stud_att in inherited_attr_map.items() if stud_att in mapped_stud_attributes_2 and inst_att in mapped_inst_attributes}

        # all student operations that are mapped to the instructor operations
        mapped_to_inst_stud_operations_1 = {inst_opr for inst_opr, stud_opr in oper_matched_map.items() if stud_opr in mapped_stud_operations_1 and inst_opr in mapped_inst_operations
        } | {inst_opr for inst_opr, stud_opr in misplaced_oper_map.items() if stud_opr in mapped_stud_operations_1 and inst_opr in mapped_inst_operations
        } | {inst_opr for inst_opr, stud_opr in inherited_oper_map.items() if stud_opr in mapped_stud_operations_1 and inst_opr in mapped_inst_operations}
        mapped_to_inst_stud_operations_2 = {inst_opr for inst_opr, stud_opr in oper_matched_map.items() if stud_opr in mapped_stud_operations_2 and inst_opr in mapped_inst_operations
        } | {inst_opr for inst_opr, stud_opr in misplaced_oper_map.items() if stud_opr in mapped_stud_operations_2 and inst_opr in mapped_inst_operations
        } | {inst_opr for inst_opr, stud_opr in inherited_oper_map.items() if stud_opr in mapped_stud_operations_2 and inst_opr in mapped_inst_operations}

        if (not mapped_to_inst_stud_attributes_1 and not mapped_to_inst_stud_operations_1) or (not mapped_to_inst_stud_attributes_2 and not mapped_to_inst_stud_operations_2):
            logger.debug(f"comparing instructor class {str(inst_class)} failed, because at least one student class has no mapped attributes and operations to the instructor class")
            return False
        
        # check if the mapped attributes and operations are the same
        if set(inst_class.attributes) == (mapped_to_inst_stud_attributes_1 | mapped_to_inst_stud_attributes_2) and set(inst_class.operations) == (mapped_stud_operations_1 | mapped_stud_operations_2):
            logger.debug(f"comparing instructor class {str(inst_class)} with student classes {str(stud_class_1)} and {str(stud_class_2)} succeeded")
            return True
        else:
            logger.debug(f"comparing instructor class {str(inst_class)} with student classes {str(stud_class_1)} and {str(stud_class_2)} failed, because the mapped attributes and operations are not the same")
            return False

    @staticmethod
    def class_contains_misplaced_properties(inst_class: UMLClass, stud_class: UMLClass, misplaced_attr_map: Dict[UMLAttribute, UMLAttribute], misplaced_oper_map: Dict[UMLOperation, UMLOperation]) -> bool:
        # checks if all misplaced attributes and operations of the instructor class are in the student class
        misplaced_attrs = [att for att in inst_class.attributes if att in misplaced_attr_map.keys()]
        misplaced_opers = [opr for opr in inst_class.operations if opr in misplaced_oper_map.keys()]
        possible_stud_attrs = [att for att in stud_class.attributes if att in misplaced_attr_map.values()]
        possible_stud_opers = [opr for opr in stud_class.operations if opr in misplaced_oper_map.values()]
        if not misplaced_attrs and not misplaced_opers:
            logger.debug(f"comparing instructor class {str(inst_class)} with student class {str(stud_class)} failed, because it has no misplaced properties")
            return False
        if misplaced_attrs:
            for inst_att in misplaced_attrs:
                if misplaced_attr_map.get(inst_att) not in possible_stud_attrs:
                    logger.debug(f"comparing instructor class {str(inst_class)} with student class {str(stud_class)} failed, because the misplaced attribute {str(inst_att)} is not in the student class")
                    return False
        if misplaced_opers:
            for inst_opr in misplaced_opers:
                if misplaced_oper_map.get(inst_opr) not in possible_stud_opers:
                    logger.debug(f"comparing instructor class {str(inst_class)} with student class {str(stud_class)} failed, because the misplaced operation {str(inst_opr)} is not in the student class")
                    return False
        logger.debug(f"comparing instructor class {str(inst_class)} with student class {str(stud_class)} succeeded")
        return True
                
    
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
