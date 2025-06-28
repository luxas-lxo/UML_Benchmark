from tools.syntactic_check import SyntacticCheck
from tools.semantic_check import SemanticCheck
from tools.content_check import ContentCheck
from tools.relation_check import RelationCheck
from UML_model.uml_class import UMLClass, UMLAttribute, UMLOperation, UMLVisability
from UML_model.uml_element import UMLElement
from UML_model.uml_model import UMLModel
from grading.grade_metamodel import GradeModel
from grading.grade_reference import GradeReference

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
    # helper function for algorithm 1, 2
    @staticmethod
    def get_safe_matches(possible_matches: Dict[GradeReference, List[GradeReference]]) -> Dict[GradeReference, GradeReference]:
        # gets the matches that are safe to use, i.e. those that have only one match and that match is not matched by any other class
        logger.info("Finding safe matches...")
        all_matched = [m for matches in possible_matches.values() for m in matches]
        matched_counter = Counter(all_matched)

        inst_elements = [
            elem for elem, matches in possible_matches.items()
            if len(matches) == 1 and matched_counter[matches[0]] == 1
        ]

        safe_matches: Dict[GradeReference, GradeReference] = {
            elem: possible_matches[elem][0] for elem in inst_elements
        }
        logger.info(f"Safe matches found: {len(safe_matches)}")
        if safe_matches:
            logger.debug(f"Safe match map: { {str(k): str(v) for k, v in safe_matches.items()} }")
        else:
            logger.debug("No safe matches found.")
        return safe_matches

    # helper function for algorithm 1, 2 
    @staticmethod
    def find_best_match_assignment(filtered_possible_matches: Dict[GradeReference, List[GradeReference]], grade_model: Optional[GradeModel] = None) -> Dict[GradeReference, GradeReference]:
        # finds the best class match using a modified Jonker-Volgenant algorithm provided by scipy.optimize.linear_sum_assignment
        # NOTE: this is a linear assignment problem, where we want to minimize the cost of matching classes based on their grades
        # the Jonker-Volgenant algorithm is a refinement of the Hungarian algorithm, which is used to solve the assignment problem in polynomial time
        logger.info("Finding best match assignments...")

        if grade_model is None:
            logger.warning("Grade model is None, using default matching without grading.\nThis may lead to double matches or suboptimal matches.")
            # If no grade model is provided, we can still return the first match for each class
            # NOTE: can be adapted to use a different matching strategy if needed
            return {elm: matches[0] for elm, matches in filtered_possible_matches.items() if matches}

        inst_elements = list(filtered_possible_matches.keys())
        all_targets = list({m for matches in filtered_possible_matches.values() for m in matches})
        cost_matrix = np.full((len(inst_elements), len(all_targets)), fill_value=1.0)

        for i, elem in enumerate(inst_elements):
            for match in filtered_possible_matches[elem]:
                j = all_targets.index(match)
                if isinstance(elem, UMLClass):
                    score = grade_model.temp_grade_class(match, elem)[0]  # Score ∈ [0, 1]
                    logger.debug(f"Grading class {elem.name} against {match.name}: score = {score}")
                elif isinstance(elem, UMLAttribute) or isinstance(elem, UMLOperation):
                    score = grade_model.temp_grade_class_content(match, elem)[0]
                    logger.debug(f"Grading content element {elem.name} against {match.name}: score = {score}")
                else:
                    logger.warning(f"Unknown element type {type(elem)} for grading, using default score of 0.0")
                    score = 0.0
                cost_matrix[i][j] = 1.0 - score  # Convert score to cost (1 - score) so lower scores mean better matches
        logger.debug(f"Cost matrix for assignment:\n{cost_matrix}")
        row_ind, col_ind = linear_sum_assignment(cost_matrix)
        logger.debug(f"Row indices: {row_ind}, Column indices: {col_ind}")

        element_match_map: Dict[GradeReference, GradeReference] = {}
        for i, j in zip(row_ind, col_ind):
            cost = cost_matrix[i][j]
            if cost < 1.0:  # if the cost is less than 1, it means there was a match
                element_match_map[inst_elements[i]] = all_targets[j]
        logger.info(f"Best matches found: {len(element_match_map)}")
        if element_match_map:
            logger.debug(f"Best element match map: { {str(k): str(v) for k, v in element_match_map.items()} }")
        return element_match_map

    # helper function for algorithm 1, 2
    @staticmethod
    def handle_possible_matches(possible_matches: Dict[GradeReference, List[GradeReference]], grade_model: Optional[GradeModel] = None) -> Tuple[Dict[GradeReference, GradeReference], Dict[GradeReference, GradeReference]]:
        safe_matches: Dict[GradeReference, GradeReference] = {}
        best_match_map: Dict[GradeReference, GradeReference] = {}
        filtered_possible_matches: Dict[GradeReference, List[GradeReference]] = {}
        if possible_matches:
            logger.debug(f"possible matches: { {str(k): [str(v) for v in vs] for k, vs in possible_matches.items()} }")
            # find safe matches first
            safe_matches = ClassComperator.get_safe_matches(possible_matches)
            # remove safe matches from possible matches
            filtered_possible_matches = {
                cls: matches for cls, matches in possible_matches.items() if cls not in safe_matches and matches
            }
        # find best matches among the remaining possible matches
        if filtered_possible_matches:
            logger.debug(f"filtered possible matches: { {str(k): [str(v) for v in vs] for k, vs in filtered_possible_matches.items()} }")
            best_match_map = ClassComperator.find_best_match_assignment(filtered_possible_matches, grade_model)

        return safe_matches, best_match_map
  
    #Algorithm 1 Compare Classes
    #1: procedure COMPARECLASS(InstructorModel,StudentModel)
    @staticmethod
    def compare_classes(instructor_model: UMLModel, student_model: UMLModel, grade_model: Optional[GradeModel] = None) -> Tuple[Dict[UMLClass, UMLClass], List[UMLClass]]:
        logger.info("starting compare classes method")
        
        possible_matches: Dict[UMLClass, List[UMLClass]] = {}
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
        logger.info(f"found {len(possible_matches)} possible class matches")
        # NOTE: **added additionally**
        # find safe matches and best match assignments among the possible matches
        safe_matches, best_match_map = ClassComperator.handle_possible_matches(possible_matches, grade_model)
       
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
                # NOTE: ** added additionally**
                unmatched_instructor_classes.append(ci)

        
        # NOTE: **added additionally**
        # find unmatched student classes
        # contains #16 from the algorithm
        unmatched_stud_classes = [cls for cls in student_classes if cls not in class_match_map.values()]
        # clears the possible matches for further processing
        possible_matches = {}
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
                logger.debug(f"relation ends for {str(ci)}: {[str(li) for li in list_i]}")
                logger.debug(f"relation ends for {str(cs)}: {[str(ls) for ls in list_s]}")
                #19: if assocMatch(ListS,ListI) then
                if RelationCheck.relation_match(list_s, list_i, class_match_map)[0]:
                    #20: classMatchMap.put(Ci, Cs)
                    possible_matches[ci].append(cs)
        if unmatched_instructor_classes:
            logger.info(f"found {len(possible_matches)} possible class matches for unmatched classes")
        # NOTE: **added additionally**
        # the algorithm does not mention it, but we search for the best assignment again
        # find safe matches and best match assignments among the possible matches
        safe_matches, best_match_map = ClassComperator.handle_possible_matches(possible_matches, grade_model)

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
        logger.info("finished compare classes method\n")
        #23: return classMatchMap, missClassList
        return class_match_map, miss_class_list

    # helper function for algorithm 2
    # NOTE: this function could have been used in algorithm 1 as well, but we decided to keep to the original algorithm structure
    @staticmethod
    def handle_safe_and_best_matches(inst_element_list: List[GradeReference], safe_matches: Dict[GradeReference, GradeReference], best_match_map: Dict[GradeReference, GradeReference], already_matched: Optional[Dict[GradeReference, GradeReference]] = None) -> Tuple[Dict[GradeReference, GradeReference], List[GradeReference]]:
        if already_matched is None:
            match_map: Dict[GradeReference, GradeReference] = {}
        else:
            match_map = already_matched.copy()
        new_matched_elements: Dict[GradeReference, GradeReference] = {}
        unmatched_elements: List[GradeReference] = []
        for elem_i in inst_element_list:
            if elem_i not in match_map:
                if elem_i in safe_matches: 
                    # NOTE: best match is the only match here
                    best_match = safe_matches[elem_i]
                    new_matched_elements[elem_i] = best_match
                elif elem_i in best_match_map:
                    # NOTE: best match is the one with the highest score in an optimal assignment
                    best_match = best_match_map[elem_i]
                    new_matched_elements[elem_i] = best_match
                else:
                    unmatched_elements.append(elem_i)
        return new_matched_elements, unmatched_elements

    # first part of algorithm 2
    @staticmethod
    def compare_attributes(inst_att_list: List[UMLAttribute], stud_att_list: List[UMLAttribute], class_match_map: Dict[UMLClass, UMLClass], reversed_class_match_map: Dict[UMLClass, UMLClass], grade_model: Optional[GradeModel] = None) -> Tuple[Dict[UMLAttribute, UMLAttribute], Dict[UMLAttribute, UMLAttribute], List[UMLAttribute]]:
        logger.info("starting compare attributes method")
        # helper variables
        possible_attr_matches: Dict[UMLAttribute, List[UMLAttribute]] = {}
        safe_attr_matches: Dict[UMLAttribute, UMLAttribute] = {}
        best_attr_match_map: Dict[UMLAttribute, UMLAttribute] = {}
        possible_missplaced_attr_matches: Dict[UMLAttribute, List[UMLAttribute]] = {}
        unmatched_inst_attrs: List[UMLAttribute] = []
        unmatched_stud_attrs: List[UMLAttribute] = []

        # final variables for return
        attr_match_map: Dict[UMLAttribute, UMLAttribute] = {}
        misplaced_attr_map: Dict[UMLAttribute, UMLAttribute] = {}
        miss_att_list: List[UMLAttribute] = []

        #4: for all Attribute Ai in instList, As in studList do   
        for a_i in inst_att_list:
            #5:Ci ← Ai.eContainer()
            c_i: UMLClass = a_i.reference
            possible_attr_matches[a_i] = []
            for a_s in stud_att_list:
                #6:Cs ← As.eContainer()
                c_s: UMLClass = a_s.reference
                #7:if Ai is synatax or semtantic match for As then 
                if SyntacticCheck.syntactic_match(a_i.name, a_s.name)[0] or (SemanticCheck.semantic_match(a_i.name, a_s.name)[0]):
                    #8:if classMatchMap.get(Cs).equals(Ci) then 
                    if class_match_map.get(c_i) == c_s:
                        #9:matchedAttrMap.put(As, Ai) 
                        possible_attr_matches[a_i].append(a_s)
                    # NOTE: the following could be merged with the previous if statement, but we keep it for the formality of the algorithm
                    #10:else if Ci is superClass of classMatchMap.get(Cs) and Ai is not private then 
                    elif reversed_class_match_map.get(c_s) and c_i == reversed_class_match_map.get(c_s).super_class and a_i.visibility != UMLVisability.PRIVATE:
                        #11:matchedAttrMap.put(As, Ai)
                        possible_attr_matches[a_i].append(a_s)

        # NOTE: **added additionally**
        # same as in algorithm 1, we find the safe matches and best match assignments among the possible matches and assign them to the attr_match_map
        safe_attr_matches, best_attr_match_map = ClassComperator.handle_possible_matches(possible_attr_matches, grade_model)
        new_matched_attrs, new_miss_inst_attrs = ClassComperator.handle_safe_and_best_matches(inst_att_list, safe_attr_matches, best_attr_match_map, attr_match_map)
        attr_match_map.update(new_matched_attrs)
        unmatched_inst_attrs.extend(new_miss_inst_attrs)

        # NOTE: the following lines are adapted, since it seems more efficient to test only for unmatched instructor attributes
        # the comments still show the original algorithm structure
        #12: for all Attribute Ai in instAttrList, As in studAttrList do 
        unmatched_stud_attrs = [att for att in stud_att_list if att not in attr_match_map.values()]
        for a_i in unmatched_inst_attrs:
            possible_missplaced_attr_matches[a_i] = []
            #13:if As not matched And Ai is synatax or semtantic match for As then 
            for a_s in unmatched_stud_attrs:
                if SyntacticCheck.syntactic_match(a_i.name, a_s.name)[0] or SemanticCheck.semantic_match(a_i.name, a_s.name)[0]:
                    #14:misplaceAttrMap.put(As, Ai)
                    possible_missplaced_attr_matches[a_i].append(a_s)

        # NOTE: **added additionally**
        safe_attr_matches, best_attr_match_map = ClassComperator.handle_possible_matches(possible_missplaced_attr_matches, grade_model)
        new_matched_attrs, new_miss_inst_attrs = ClassComperator.handle_safe_and_best_matches(inst_att_list, safe_attr_matches, best_attr_match_map, attr_match_map)
        misplaced_attr_map.update(new_matched_attrs)
        miss_att_list.extend(new_miss_inst_attrs)

        logger.info("finished compare attributes method\n")
        return attr_match_map, misplaced_attr_map, miss_att_list

    # second part of algorithm 2
    def compare_operations(inst_opr_list: List[UMLOperation], stud_opr_list: List[UMLOperation], class_match_map: Dict[UMLClass, UMLClass], reversed_class_match_map: Dict[UMLClass, UMLClass], grade_model: Optional[GradeModel] = None) -> Tuple[Dict[UMLOperation, UMLOperation], Dict[UMLOperation, UMLOperation], List[UMLOperation]]:
        logger.info("starting compare operations method")
        # helper variables
        possible_oper_matches: Dict[UMLOperation, List[UMLOperation]] = {}
        safe_opr_matches: Dict[UMLOperation, UMLOperation] = {}
        best_opr_match_map: Dict[UMLOperation, UMLOperation] = {}
        possible_missplaced_oper_matches: Dict[UMLOperation, List[UMLOperation]] = {}
        unmatched_inst_opers: List[UMLOperation] = []
        unmatched_stud_opers: List[UMLOperation] = []

        # final variables for return
        oper_match_map: Dict[UMLOperation, UMLOperation] = {}
        misplaced_oper_match_map: Dict[UMLOperation, UMLOperation] = {}
        miss_opr_list: List[UMLOperation] = []

        #17: for all Operation Oi in instList, Os in studList do 
        for oi in inst_opr_list:
            #18:Ci ← Oi.eContainer() 
            ci: UMLClass = oi.reference
            possible_oper_matches[oi] = []
            for os in stud_opr_list:
                #19:Cs ← Os.eContainer()
                cs: UMLClass = os.reference
                #20:if Oi.synMatch(Os) or Oi.semanticMatch(Os) then 
                if SyntacticCheck.syntactic_match(oi.name, os.name)[0] or SemanticCheck.semantic_match(oi.name, os.name)[0]:
                    #21:if classMatchMap.get(Cs) equals Ci then  
                    if class_match_map.get(ci) == cs:
                        #22:matchedOperMap.put(Os, Oi) 
                        possible_oper_matches[oi].append(os)
                    #23:else if Ci is superClass of classMatchMap.get(Cs) and Oi is not private then 
                    # TODO: does this really go through all super classes?
                    elif reversed_class_match_map.get(cs) and ci == reversed_class_match_map.get(cs).super_class and oi.visibility != UMLVisability.PRIVATE:
                        #24:matchedOperMap.put(Os, Oi) 
                        possible_oper_matches[oi].append(os)
        
        # NOTE: **added additionally**
        # same as in algorithm 1, we find the safe matches and best match assignments among the possible matches and assign them to the attr_match_map
        safe_opr_matches, best_opr_match_map = ClassComperator.handle_possible_matches(possible_oper_matches, grade_model)
        new_matched_opers, new_miss_inst_opers = ClassComperator.handle_safe_and_best_matches(inst_opr_list, safe_opr_matches, best_opr_match_map, oper_match_map)
        oper_match_map.update(new_matched_opers)
        unmatched_inst_opers.extend(new_miss_inst_opers)


        #25: for all Operation Oi in instOperList, Os in studOperList do
        unmatched_stud_opers = [opr for opr in stud_opr_list if opr not in oper_match_map.values()]
        for oi in unmatched_inst_opers:
            possible_missplaced_oper_matches[oi] = []
            #26:if Os is not matched And Oi.synlMatch(Os) or Oi.semanticMatch(Os) then 
            for os in unmatched_stud_opers:
                if SyntacticCheck.syntactic_match(oi.name, os.name)[0] or SemanticCheck.semantic_match(oi.name, os.name)[0]:
                    #27:misplaceOperMap.put(Os, Oi) 
                    possible_missplaced_oper_matches[oi].append(os)
                    #28:instOperList.put(Oi, true) 
                    # NOTE:**skipped**
            #**added additionally**

        # NOTE: **added additionally**
        # same as in algorithm 1, we find the safe matches and best match assignments among the possible matches and assign them to the attr_match_map
        safe_opr_matches, best_opr_match_map = ClassComperator.handle_possible_matches(possible_missplaced_oper_matches, grade_model)
        new_matched_opers, new_miss_inst_opers = ClassComperator.handle_safe_and_best_matches(inst_opr_list, safe_opr_matches, best_opr_match_map, oper_match_map)
        misplaced_oper_match_map.update(new_matched_opers)
        miss_opr_list.extend(new_miss_inst_opers)

        logger.info("finished compare operations method\n")
        return oper_match_map, misplaced_oper_match_map, miss_opr_list

    @staticmethod
    def compare_content(instructor_model: UMLModel, student_model: UMLModel, class_match_map: Dict[UMLClass, UMLClass], grade_model: Optional[GradeModel] = None) -> Tuple[Dict[UMLAttribute, UMLAttribute], Dict[UMLAttribute, UMLAttribute], List[UMLAttribute], Dict[UMLOperation, UMLOperation], Dict[UMLOperation, UMLOperation], List[UMLOperation]]:
        logger.info("starting compare content method")

        #WARNING: if stud_class mapped to multiple inst_classes -> problem
        # NOTE: should not be possible with the current algorithm 1
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

        #4 - #14
        attr_match_map, misplaced_attr_map, miss_attr_list = ClassComperator.compare_attributes(inst_att_list, stud_att_list, class_match_map, reversed_class_match_map, grade_model)

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

        #17 - #28
        oper_matched_map, misplaced_oper_map, miss_oper_list = ClassComperator.compare_operations(inst_opr_list, stud_opr_list, class_match_map, reversed_class_match_map, grade_model)

        logger.info("finished compare content method")
        #29: return matchedAttrMap, misplaceAttrMap, matchedOperMap, misplaceOperMap
        return attr_match_map, misplaced_attr_map, miss_attr_list, oper_matched_map, misplaced_oper_map, miss_oper_list

