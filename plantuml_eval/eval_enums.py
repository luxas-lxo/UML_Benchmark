from UML_model.uml_model import UMLModel
from UML_model.uml_class import UMLClass, UMLAttribute
from UML_model.uml_enum import UMLEnum, UMLValue
from tools.syntactic_check import SyntacticCheck
from tools.semantic_check import SemanticCheck
from tools.content_check import ContentCheck
from grading.grade_metamodel import GradeModel
from plantuml_eval.eval_helper_functions import EvalHelper

from typing import Dict, List, Tuple, Union, Optional
import logging

logger = logging.getLogger("enum_eval")
logger.setLevel(logging.DEBUG)

if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(levelname)s] - %(name)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

class EnumComperator:
    #Algorithm 6 Compare ENUM in InstructorModel and StudentModel
    #1: procedure COMPAREENUM(InstructorModel, StudentModel)
    @staticmethod
    def compare_enums(instructor_model: UMLModel, student_model: UMLModel, grade_model: Optional[GradeModel] = None) -> Tuple[Dict[UMLEnum, UMLEnum], List[UMLEnum], Dict[UMLValue, Union[UMLAttribute, UMLClass]]]:
        logger.debug("Starting enum comparison")
        enum_match_map: Dict[UMLEnum, UMLEnum] = {}
        miss_enum_list: List[UMLEnum] = []
        possible_misplaced_values: Dict[UMLValue, Union[UMLAttribute, UMLClass]] = {}
        possible_enum_match: Dict[UMLEnum, List[UMLEnum]] = {}
        #2: instENUMList ← InstructorModel.getENUM()
        inst_enum_list: List[UMLEnum] = instructor_model.enum_list
        #3: studENUMList ← StudentModel.getENUM()
        stud_enum_list: List[UMLEnum] = student_model.enum_list

        #4: for all ENUM Ei in instENUMList, Es in studENUMList do 
        for ei in inst_enum_list:
            possible_enum_match[ei] = []
            for es in stud_enum_list:
                #5: if syntacticMatch(Es.name, Ei.name) or 
                #6:semanticMatch(Es.name, Ei.name) then  
                if SyntacticCheck.syntactic_match(es.name, ei.name)[0] or SemanticCheck.semantic_match(es.name, ei.name)[0]:
                    possible_enum_match[ei].append(es)
                    #7: enumMatchMap.put(Es, Ei)
                    logger.debug(f"Enum match found: {ei.name} with {es.name}")
                #8: else if Es and Ei have similar literal values then 
                elif ContentCheck.enum_content_match(ei, es):
                    #9:enumMatchMap.put(Es, Ei) 
                    possible_enum_match[ei].append(es)
                    logger.debug(f"Enum match found: {ei.name} with {es.name}")
        
        #**added additionally**
        safe_enum_matches, best_enum_match_map = EvalHelper.handle_possible_matches(possible_enum_match, grade_model)
        new_matched_enums, new_miss_inst_enums = EvalHelper.handle_safe_and_best_matches(inst_enum_list, safe_enum_matches, best_enum_match_map, enum_match_map)
        enum_match_map.update(new_matched_enums)
        miss_enum_list.extend(new_miss_inst_enums)

        #10: studClassList ← StudentModel.getClass()
        stud_class_list = student_model.class_list
        #11: studAttrList ← StudentModel.getAttribute()
        stud_att_list: List[UMLAttribute] = []
        for stud_cls in stud_class_list:
            for att in stud_cls.attributes:
                stud_att_list.append(att)
        #12: for all ENUM Ei in instENUMList do
        for ei in inst_enum_list:
            #13: for all literal L in Ei.literal do 
            for value in ei.values:
                #14:for all Attribute As in studClassList do
                for a_s in stud_att_list:
                    #15:if As.Name.syntacticMatch(L.Name) or As.Name.semanticMatch(L.Name) then
                   if SyntacticCheck.syntactic_match(a_s.name, value.name)[0] or SemanticCheck.semantic_match(a_s.name, value.name)[0]:
                       #16:consider As represent L
                       possible_misplaced_values[value] = a_s
                       logger.debug(f"Enum literal match with attribute found: {str(value)} with {str(a_s)}")
                #17:for all class Cs in studClassList do
                for cs in stud_class_list:
                    #18:if Cs.Name.syntacticMatch(L.Name) or Cs.Name.semanticMatch(L.Name) then
                    if SyntacticCheck.syntactic_match(cs.name, value.name)[0] or SemanticCheck.semantic_match(cs.name, value.name)[0]:
                        #19:consider Cs represent L
                        possible_misplaced_values[value] = cs
                        logger.debug(f"Enum literal match with class found: {str(value)} with {str(cs)}")

        logger.info("finished compare enums method\n")
        #20: return enumMatchMap
        return enum_match_map, miss_enum_list, possible_misplaced_values