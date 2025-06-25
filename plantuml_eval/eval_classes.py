from tools.syntactic_check import SyntacticCheck
from tools.semantic_check import SemanticCheck
from tools.content_check import ContentCheck
from tools.relation_check import RelationCheck
from UML_model.uml_class import UMLClass, UMLAttribute, UMLOperation, UMLVisability
from UML_model.uml_element import UMLElement
from UML_model.uml_model import UMLModel
from grading.grade_metamodel import GradeModel

from enum import Enum
from typing import List, Dict, Optional, Tuple
import logging
from collections import Counter
from scipy.optimize import linear_sum_assignment
import numpy as np


logger = logging.getLogger("class_eval")
logger.setLevel(logging.DEBUG)

if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(levelname)s] - %(name)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

class ClassComperator:
    @staticmethod
    def get_safe_matches(possible_matches: Dict[UMLClass, List[UMLClass]]) -> Dict[UMLClass, UMLClass]:
        # gets the matches that are safe to use, i.e. those that have only one match and that match is not matched by any other class
        logger.info("Finding safe matches...")
        all_matched = [m for matches in possible_matches.values() for m in matches]
        matched_counter = Counter(all_matched)

        inst_classes = [
            cls for cls, matches in possible_matches.items()
            if len(matches) == 1 and matched_counter[matches[0]] == 1
        ]

        safe_matches: Dict[UMLClass, UMLClass] = {
            cls: possible_matches[cls][0] for cls in inst_classes
        }
        logger.info(f"Safe matches found: {len(safe_matches)}")
        if safe_matches:
            logger.debug(f"Safe class match map: { {str(k): str(v) for k, v in safe_matches.items()} }")
        else:
            logger.debug("No safe matches found.")
        return safe_matches

    @staticmethod
    def find_best_class_match_assignment(filtered_possible_matches: Dict[UMLClass, List[UMLClass]], grade_model: Optional[GradeModel] = None) -> Dict[UMLClass, UMLClass]:
        # finds the best class match using the Hungarian algorithm
        logger.info("Finding best class match assignments...")

        if grade_model is None:
            logger.warning("Grade model is None, using default matching without grading.\nThis may lead to double matches or suboptimal matches.")
            # If no grade model is provided, we can still return the first match for each class
            # NOTE: can be adapted to use a different matching strategy if needed
            return {cls: matches[0] for cls, matches in filtered_possible_matches.items() if matches}
        
        inst_classes = list(filtered_possible_matches.keys())
        all_targets = list({m for matches in filtered_possible_matches.values() for m in matches})
        cost_matrix = np.full((len(inst_classes), len(all_targets)), fill_value=1.0) 

        for i, cls in enumerate(inst_classes):
            for match in filtered_possible_matches[cls]:
                j = all_targets.index(match)
                score = grade_model.temp_grade_class(match, cls)[0]  # Score ∈ [0, 1]
                cost_matrix[i][j] = 1.0 - score  # Convert score to cost (1 - score) so lower scores mean better matches

        row_ind, col_ind = linear_sum_assignment(cost_matrix)

        class_match_map: Dict[UMLClass, UMLClass] = {}
        for i, j in zip(row_ind, col_ind):
            cost = cost_matrix[i][j]
            if cost < 1.0:  # if the cost is less than 1, it means there was a match
                class_match_map[inst_classes[i]] = all_targets[j]
        logger.info(f"Best matches found: {len(class_match_map)}")
        if class_match_map:
            logger.debug(f"Best class match map: { {str(k): str(v) for k, v in class_match_map.items()} }")
        return class_match_map

    @staticmethod
    def find_best_content_match(inst_att: UMLAttribute, possible_matches: List[UMLAttribute]) -> Optional[UMLAttribute]:
        #TODO später vllt noch mit wirklicher bewertung?
        pass

    #Algorithm 1 Compare Classes
    #1: procedure COMPARECLASS(InstructorModel,StudentModel)
    @staticmethod
    def compare_classes(instructor_model: UMLModel, student_model: UMLModel, grade_model: Optional[GradeModel] = None) -> Tuple[Dict[UMLClass, UMLClass], List[UMLClass]]:
        logger.info("starting compare classes method")
        
        possible_matches: Dict[UMLClass, List[UMLClass]] = {}  
        filtered_possible_matches: Dict[UMLClass, List[UMLClass]] = {}
        safe_matches: Dict[UMLClass, UMLClass] = {}
        best_match_map: Dict[UMLClass, UMLClass] = {}
        unmatched_instructor_classes: List[UMLClass] = []
        unmatched_stud_classes: List[UMLClass] = []
        miss_class_list: List[UMLClass] = []
        class_match_map: Dict[UMLClass, UMLClass] = {}

        #2: instList← InstructorModel.getClass()
        instructor_classes: List[UMLClass] = instructor_model.class_list
        #3: studList← StudentModel.getClass()
        student_classes: List[UMLClass] = student_model.class_list
        logger.info(f"starting syntactic, semantic and content matching for {len(instructor_classes)} instructor classes and {len(student_classes)} student classes")
        
        #4: for all Class Ci in instList, Cs in studList do
        for ci in instructor_classes:
            possible_matches[ci] = []
            for cs in student_classes:
                #5: if syntacticMatch(Cs.name, Ci.name) or
                if (SyntacticCheck.syntactic_match(ci.name, cs.name)[0]) or (
                    #6: semanticMatch(Cs.name, Ci.name) ) or
                    SemanticCheck.semantic_match(ci.name, cs.name)[0]) or (
                    #7: contentMatch(Cs.content, Ci.content) then
                    ContentCheck.content_match(ci, cs)[0]):
                    #8: storePossibleMatch(Ci, Cs)
                    possible_matches[ci].append(cs)
        logger.info(f"found {len(possible_matches)} possible matches")
        # NOTE: **added additionally**
        if possible_matches:
            logger.debug(f"possible matches: { {str(k): [str(v) for v in vs] for k, vs in possible_matches.items()} }")
            # find safe matches first
            safe_matches = ClassComperator.get_safe_matches(possible_matches)
            # remove safe matches from possible matches
            filtered_possible_matches = {
                cls: matches for cls, matches in possible_matches.items() if cls not in safe_matches and matches
            }
        # find best matches among the remaining possible matches
        if filtered_possible_matches and grade_model is not None:
            best_match_map = ClassComperator.find_best_class_match_assignment(filtered_possible_matches, grade_model)
       
        #9: for all Class Ci in instList do
        for ci in instructor_classes:
            #10: if ∃ matched classes for Ci then
            #11: find among the matches of Ci the Cbest
            #12: that obtains the highest mark among the matches
            if ci in safe_matches: 
                # NOTE: best match is the only match here
                best_match = safe_matches[ci]
                #13: classMatchMap.put(Ci, Cbest)
                class_match_map[ci] = best_match
            elif ci in best_match_map:
                # NOTE: best match is the one with the highest score in an optimal assignment
                best_match = best_match_map[ci]
                #13: classMatchMap.put(Ci, Cbest)
                class_match_map[ci] = best_match
            else:
                # NOTE: not explicitly mentioned in the algorithm, but we assume that if no match is found, we add it to the miss class list
                unmatched_instructor_classes.append(ci)

        
        # NOTE: **added additionally**
        # find unmatched student classes
        # contains #16 from the algorithm
        unmatched_stud_classes = [cls for cls in student_classes if cls not in class_match_map.values()]
        # clears the possible, filtered, safe and best matches for further processing
        possible_matches = {}
        filtered_possible_matches = {}
        safe_matches = {}
        best_match_map = {}
        if  unmatched_instructor_classes: 
            logger.info(f"starting relation matching for {len(unmatched_instructor_classes)} unmatched instructor classes and {len(unmatched_stud_classes)} unmatched student classes")
            logger.debug(f"unmatched instructor classes: {[str(cls) for cls in unmatched_instructor_classes]}")
            logger.debug(f"unmatched student classes: {[str(cls) for cls in unmatched_stud_classes]}")
        #14: for all Class Ci in missClassList do 
        for ci in unmatched_instructor_classes:
            possible_matches[ci] = []
            #15: for all Class Cs in studList do 
            #16:if no match exists for Cs then 
            for cs in unmatched_stud_classes:
                #17: ListI← Ci.getAssociationEnds()
                list_i = ci.get_relation_ends()
                #18: ListS← Cs.getAssociationEnds()
                list_s = cs.get_relation_ends()
                logger.debug(f"relation ends for {ci}: {[str(li) for li in list_i]}")
                logger.debug(f"relation ends for {cs}: {[str(ls) for ls in list_s]}")
                #19: if assocMatch(ListS,ListI) then
                if RelationCheck.relation_match(list_s, list_i, class_match_map)[0]:
                    #20: classMatchMap.put(Ci, Cs)
                    possible_matches[ci].append(cs)
        if unmatched_instructor_classes:
            logger.info(f"found {len(possible_matches)} possible matches for unmatched classes")
        # NOTE: **added additionally**
        # the algorithm does not mention it, but we search for the best assignment again
        # same procedure as before, but for the new  matched classes
        if possible_matches:
            logger.debug(f"possible matches: { {str(k): [str(v) for v in vs] for k, vs in possible_matches.items()} }")
            safe_matches = ClassComperator.get_safe_matches(possible_matches)
            filtered_possible_matches = {
                cls: matches for cls, matches in possible_matches.items() if cls not in safe_matches and matches
            }
        if filtered_possible_matches and grade_model is not None:
            best_match_map = ClassComperator.find_best_class_match_assignment(filtered_possible_matches, grade_model)

        for ci in instructor_classes:
            if ci not in class_match_map:
                if ci in safe_matches:
                    best_match = safe_matches[ci]
                    class_match_map[ci] = best_match
                elif ci in best_match_map:
                    best_match = best_match_map[ci]
                    class_match_map[ci] = best_match
                #21: if no match exists for Ci then
                else:
                    #22: missClassList.add(Ci)
                    miss_class_list.append(ci)
        logger.info(f"found {len(class_match_map)} out of {len(instructor_classes)} class matches and {len(miss_class_list)} missing classes")
        logger.info("finished compare classes method")
        #23: return classMatchMap, missClassList
        return class_match_map, miss_class_list   

    #Algorithm 2 Compare attributes and operations in InstructorModel with StudentModel 
    #1: procedure COMPARECONTENT(InstructorModel, StudentModel, classMatchMap) 
    @staticmethod
    def compare_content(instructor_model: UMLModel, student_model: UMLModel, class_match_map: Dict[UMLClass, UMLClass]):
        logger.info("starting compare content method")
        possible_attr_matches: Dict[UMLAttribute, List[UMLAttribute]] = {}
        attr_match_map: Dict[UMLAttribute, UMLAttribute] = {}
        possible_missplaced_attr_matches: Dict[UMLAttribute, List[UMLAttribute]] = {}
        misplaced_attr_map: Dict[UMLAttribute, UMLAttribute] = {}

        possible_oper_matches: Dict[UMLOperation, List[UMLOperation]] = {}
        oper_matched_map: Dict[UMLOperation, UMLOperation] = {}
        possible_missplaced_oper_matches: Dict[UMLOperation, List[UMLOperation]] = {}
        misplaced_oper_map: Dict[UMLOperation, UMLOperation] = {}

        #WARNING: if stud_class mapped to multiple inst_classes -> problem
        reversed_class_match_map: Dict[UMLClass, UMLClass] = {v: k for k, v in class_match_map.items()}

        #2: instList← InstructorModel.getAttribute() 
        inst_att_list: List[UMLAttribute] = []
        for inst_cls in instructor_model.class_list:
            for att in inst_cls.attributes:
                inst_att_list.append(att)

        #3: studList← StudentModel.getAttribute() 
        stud_att_list: List[UMLAttribute] = []
        for stud_cls in student_model.class_list:
            for att in stud_cls.attributes:
                stud_att_list.append(att)

        #4: for all Attribute Ai in instList, As in studList do   
        for a_i in inst_att_list:
            #5:Ci ← Ai.eContainer()
            c_i: UMLClass = a_i.reference
            possible_attr_matches[a_i] = []
            for a_s in stud_att_list:
                #6:Cs ← As.eContainer()
                c_s: UMLClass = a_s.reference
                #7:if Ai is synatax or semtantic match for As then 
                if (res := SyntacticCheck.syntactic_match(a_i.name, a_s.name))[0]:
                    #8:if classMatchMap.get(Cs).equals(Ci) then 
                    if class_match_map.get(c_i) == c_s:
                        #9:matchedAttrMap.put(As, Ai) 
                        possible_attr_matches[a_i].append(a_s)
                    #10:else if Ci is superClass of classMatchMap.get(Cs) and Ai is not private then 
                    elif c_i == reversed_class_match_map.get(c_s).super_class and a_i.visibility != UMLVisability.PRIVATE:
                        #11:matchedAttrMap.put(As, Ai)
                        possible_attr_matches[a_i].append(a_s)
                #7:if Ai is synatax or semtantic match for As then 
                if (res := SemanticCheck.semantic_match(a_i.name, a_s.name))[0]:
                    #8:if classMatchMap.get(Cs).equals(Ci) then 
                    if class_match_map.get(c_i) == c_s:
                        #9:matchedAttrMap.put(As, Ai) 
                        possible_attr_matches[a_i].append(a_s)
                    #10:else if Ci is superClass of classMatchMap.get(Cs) and Ai is not private then
                    elif c_i == reversed_class_match_map.get(c_s).super_class and a_i.visibility != UMLVisability.PRIVATE:
                        #11:matchedAttrMap.put(As, Ai)
                        possible_attr_matches[a_i].append(a_s)
            #**added additionally**
            if possible_attr_matches.get(a_i):
                best_match = ClassComperator.find_best_content_match(a_i, possible_attr_matches[a_i])
                attr_match_map[a_i] = best_match
        
        #12: for all Attribute Ai in instAttrList, As in studAttrList do 
        unmatched_stud_attrs = [att for att in stud_att_list if att not in attr_match_map.values()]
        for a_i in inst_att_list:
            possible_missplaced_attr_matches[a_i] = []
            #13:if As not matched And Ai is synatax or semtantic match for As then 
            for a_s in unmatched_stud_attrs:
                if (res := SyntacticCheck.syntactic_match(a_i.name, a_s.name))[0]:
                    #14:misplaceAttrMap.put(As, Ai)
                    possible_missplaced_attr_matches[a_i].append(a_s)
                if (res := SemanticCheck.semantic_match(a_i.name, a_s.name))[0]:
                    #14:misplaceAttrMap.put(As, Ai)
                    possible_missplaced_attr_matches[a_i].append(a_s)
            #**added additionally**
            if possible_missplaced_attr_matches.get(a_i):
                best_match = ClassComperator.find_best_content_match(a_i, possible_missplaced_attr_matches[a_i])
                misplaced_attr_map[a_i] = best_match

        #15: instList← InstructorModel.getOperation()
        inst_opr_list: List[UMLOperation] = []
        for inst_cls in instructor_model.class_list:
            for opr in inst_cls.operations:
                inst_opr_list.append(opr)

        #16: studList← StudentModel.getOperation() 
        stud_opr_list: List[UMLOperation] = []
        for stud_cls in student_model.class_list:
            for opr in stud_cls.operations:
                stud_opr_list.append(opr)

        #17: for all Operation Oi in instList, Os in studList do 
        for oi in inst_opr_list:
            #18:Ci ← Oi.eContainer() 
            ci: UMLClass = oi.reference
            possible_oper_matches[oi] = []
            for os in stud_opr_list:
                #19:Cs ← Os.eContainer()
                cs: UMLClass = os.reference
                #20:if Oi.synMatch(Os) or Oi.semanticMatch(Os) then 
                if (res := SyntacticCheck.syntactic_match(oi.name, os.name))[0]:
                    #21:if classMatchMap.get(Cs) equals Ci then  
                    if class_match_map.get(ci) == cs:
                        #22:matchedOperMap.put(Os, Oi) 
                        possible_oper_matches[oi].append(os)
                    #23:else if Ci is superClass of classMatchMap.get(Cs) and Oi is not private then 
                    elif ci == reversed_class_match_map.get(cs).super_class and oi.visibility != UMLVisability.PRIVATE:
                        #24:matchedOperMap.put(Os, Oi) 
                        possible_oper_matches[oi].append(os)
                #20:if Oi.synMatch(Os) or Oi.semanticMatch(Os) then
                if (res := SemanticCheck.semantic_match(oi.name, os.name))[0]:
                    #21:if classMatchMap.get(Cs) equals Ci then 
                    if class_match_map.get(ci) == cs:
                        #22:matchedOperMap.put(Os, Oi)
                        possible_oper_matches[oi].append(os)
                    #23:else if Ci is superClass of classMatchMap.get(Cs) and Oi is not private then
                    elif ci == reversed_class_match_map.get(cs).super_class and oi.visibility != UMLVisability.PRIVATE:
                        #24:matchedOperMap.put(Os, Oi)
                        possible_oper_matches[oi].append(os)
            #**added additionally**
            if possible_oper_matches.get(oi):
                best_match = ClassComperator.find_best_content_match(oi, possible_oper_matches[oi])
                oper_matched_map[oi] = best_match

        #25: for all Operation Oi in instOperList, Os in studOperList do
        unmatched_stud_opers = [opr for opr in stud_opr_list if opr not in oper_matched_map.values()]
        for oi in inst_opr_list:
            possible_missplaced_oper_matches[oi] = []
            #26:if Os is not matched And Oi.synlMatch(Os) or Oi.semanticMatch(Os) then 
            for os in unmatched_stud_opers:
                if (res := SyntacticCheck.syntactic_match(oi.name, os.name))[0]:
                    #27:misplaceOperMap.put(Os, Oi) 
                    possible_missplaced_oper_matches[oi].append(os)
                    #28:instOperList.put(Oi, true) 
                    #**skipped**
                if (res := SemanticCheck.semantic_match(oi.name, os.name))[0]:
                    #27:misplaceOperMap.put(Os, Oi)
                    possible_missplaced_oper_matches[oi].append(os)
                    #28:instOperList.put(Oi, true) 
                    #**skipped**
            #**added additionally**
            if possible_missplaced_oper_matches.get(oi):
                best_match = ClassComperator.find_best_content_match(oi, possible_missplaced_oper_matches[oi])
                misplaced_oper_map[oi] = best_match.matched

        logger.info("finished compare content method")
        #29: return matchedAttrMap, misplaceAttrMap, matchedOperMap, misplaceOperMap
        return attr_match_map, misplaced_attr_map, oper_matched_map, misplaced_oper_map

