from tools.syntactic_check import SyntacticCheck
from tools.semantic_check import SemanticCheck
from tools.content_check import ContentCheck
from tools.relation_check import RelationCheck
from UML_model.uml_class import UMLClass, UMLAttribute, UMLOperation, UMLVisibility
from UML_model.uml_relation import UMLRelationType
from UML_model.uml_model import UMLModel
from grading.grade_metamodel import GradeModel
from plantuml_eval.eval_helper_functions import EvalHelper

from typing import List, Dict, Optional, Tuple
import logging


logger = logging.getLogger("class_eval")
logger.setLevel(logging.DEBUG)

if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(levelname)s] - %(name)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

class ClassComperator:
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
                    ContentCheck.class_content_match(ci, cs)[0]):
                    #8: storePossibleMatch(Ci, Cs)
                    possible_matches[ci].append(cs)
        logger.info(f"found {len(possible_matches)} possible class matches")
        # NOTE: **added additionally**
        # find safe matches and best match assignments among the possible matches
        safe_matches, best_match_map = EvalHelper.handle_possible_matches(possible_matches, grade_model)
       
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
        safe_matches, best_match_map = EvalHelper.handle_possible_matches(possible_matches, grade_model)

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

    # first part of algorithm 2
    @staticmethod
    def compare_attributes(inst_att_list: List[UMLAttribute], stud_att_list: List[UMLAttribute], class_match_map: Dict[UMLClass, UMLClass], reversed_class_match_map: Dict[UMLClass, UMLClass], grade_model: Optional[GradeModel] = None) -> Tuple[Dict[UMLAttribute, UMLAttribute], Dict[UMLAttribute, UMLAttribute], Dict[UMLAttribute, UMLAttribute], List[UMLAttribute]]:
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
        inherited_attr_map: Dict[UMLAttribute, UMLAttribute] = {}
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
                    # NOTE: the authors recomends to follow the inheritance hierarchy all the way up, but for the given test cases, 2 levels of inheritance are sufficient
                    elif reversed_class_match_map.get(c_s) and (c_i == reversed_class_match_map.get(c_s).super_class or (reversed_class_match_map.get(c_s).super_class and c_i == reversed_class_match_map.get(c_s).super_class.super_class)) and a_i.visibility != UMLVisibility.PRIVATE:
                        #11:matchedAttrMap.put(As, Ai)
                        possible_attr_matches[a_i].append(a_s)

        # NOTE: **added additionally**
        # same as in algorithm 1, we find the safe matches and best match assignments among the possible matches and assign them to the attr_match_map
        safe_attr_matches, best_attr_match_map = EvalHelper.handle_possible_matches(possible_attr_matches, grade_model, class_match_map)
        new_matched_attrs, new_miss_inst_attrs = EvalHelper.handle_safe_and_best_matches(inst_att_list, safe_attr_matches, best_attr_match_map, attr_match_map)
        attr_match_map.update(new_matched_attrs)
        unmatched_inst_attrs.extend(new_miss_inst_attrs)

        # this part seperates the inherited attributes from the matched attributes for later evaluation
        for a_i, a_s in attr_match_map.items():
            if class_match_map.get(a_i.reference) != a_s.reference:
                inherited_attr_map[a_i] = a_s
        for a_i in inherited_attr_map:
            if a_i in attr_match_map:
                del attr_match_map[a_i]

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
        safe_attr_matches, best_attr_match_map = EvalHelper.handle_possible_matches(possible_missplaced_attr_matches, grade_model)
        new_matched_attrs, new_miss_inst_attrs = EvalHelper.handle_safe_and_best_matches(inst_att_list, safe_attr_matches, best_attr_match_map, {**attr_match_map, **inherited_attr_map})
        misplaced_attr_map.update(new_matched_attrs)
        miss_att_list.extend(new_miss_inst_attrs)

        logger.info("finished compare attributes method\n")
        return attr_match_map, inherited_attr_map, misplaced_attr_map, miss_att_list

    # second part of algorithm 2
    @staticmethod
    def compare_operations(inst_opr_list: List[UMLOperation], stud_opr_list: List[UMLOperation], class_match_map: Dict[UMLClass, UMLClass], reversed_class_match_map: Dict[UMLClass, UMLClass], grade_model: Optional[GradeModel] = None) -> Tuple[Dict[UMLOperation, UMLOperation], Dict[UMLOperation, UMLOperation], Dict[UMLOperation, UMLOperation], List[UMLOperation]]:
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
        inherited_oper_map: Dict[UMLOperation, UMLOperation] = {}
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
                    # NOTE: the authors recomends to follow the inheritance hierarchy all the way up, but for the given test cases, 2 levels of inheritance are sufficient
                    elif reversed_class_match_map.get(cs) and (ci == reversed_class_match_map.get(cs).super_class or (reversed_class_match_map.get(cs).super_class and ci == reversed_class_match_map.get(cs).super_class.super_class)) and oi.visibility != UMLVisibility.PRIVATE:
                        #24:matchedOperMap.put(Os, Oi)
                        possible_oper_matches[oi].append(os)
        
        # NOTE: **added additionally**
        # same as in algorithm 1, we find the safe matches and best match assignments among the possible matches and assign them to the attr_match_map
        safe_opr_matches, best_opr_match_map = EvalHelper.handle_possible_matches(possible_oper_matches, grade_model, class_match_map)
        new_matched_opers, new_miss_inst_opers = EvalHelper.handle_safe_and_best_matches(inst_opr_list, safe_opr_matches, best_opr_match_map, oper_match_map)
        oper_match_map.update(new_matched_opers)
        unmatched_inst_opers.extend(new_miss_inst_opers)

        # this part seperates the inherited operations from the matched operations for later evaluation
        for oi, os in oper_match_map.items():
            if class_match_map.get(oi.reference) != os.reference:
                inherited_oper_map[oi] = os
        for oi in inherited_oper_map:
            if oi in oper_match_map:
                del oper_match_map[oi]

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
        safe_opr_matches, best_opr_match_map = EvalHelper.handle_possible_matches(possible_missplaced_oper_matches, grade_model)
        new_matched_opers, new_miss_inst_opers = EvalHelper.handle_safe_and_best_matches(inst_opr_list, safe_opr_matches, best_opr_match_map, {**oper_match_map, **inherited_oper_map})
        misplaced_oper_match_map.update(new_matched_opers)
        miss_opr_list.extend(new_miss_inst_opers)

        logger.info("finished compare operations method\n")
        return oper_match_map, inherited_oper_map, misplaced_oper_match_map, miss_opr_list

    #Algorithm 2 Compare attributes and operations in InstructorModel with StudentModel
    #1: procedure COMPARECONTENT(InstructorModel,StudentModel, classMatchMap)
    @staticmethod
    def compare_class_content(instructor_model: UMLModel, student_model: UMLModel, class_match_map: Dict[UMLClass, UMLClass], grade_model: Optional[GradeModel] = None) -> Tuple[Dict[UMLAttribute, UMLAttribute], Dict[UMLAttribute, UMLAttribute], Dict[UMLAttribute, UMLAttribute], List[UMLAttribute], Dict[UMLOperation, UMLOperation], Dict[UMLOperation, UMLOperation], Dict[UMLOperation, UMLOperation], List[UMLOperation]]:
        logger.info("starting compare content method")

        # WARNING: if stud_class mapped to multiple inst_classes -> problem
        # NOTE: problem case should not trigger with the current algorithm 1
        reversed_class_match_map: Dict[UMLClass, UMLClass] = {v: k for k, v in class_match_map.items()}

        #2: instList← InstructorModel.getAttribute() 
        inst_att_list: List[UMLAttribute] = instructor_model.attribute_list

        #3: studList← StudentModel.getAttribute() 
        stud_att_list: List[UMLAttribute] = student_model.attribute_list

        #4 - #14
        attr_match_map, inherited_attr_map, misplaced_attr_map, miss_attr_list = ClassComperator.compare_attributes(inst_att_list, stud_att_list, class_match_map, reversed_class_match_map, grade_model)

        #15: instList← InstructorModel.getOperation()
        inst_opr_list: List[UMLOperation] = instructor_model.operation_list

        #16: studList← StudentModel.getOperation() 
        stud_opr_list: List[UMLOperation] = student_model.operation_list

        #17 - #28
        oper_matched_map, inherited_oper_map, misplaced_oper_map, miss_oper_list = ClassComperator.compare_operations(inst_opr_list, stud_opr_list, class_match_map, reversed_class_match_map, grade_model)

        logger.info("finished compare content method")
        #29: return matchedAttrMap, misplaceAttrMap, matchedOperMap, misplaceOperMap
        return attr_match_map, inherited_attr_map, misplaced_attr_map, miss_attr_list, oper_matched_map, inherited_oper_map, misplaced_oper_map, miss_oper_list

    #Algorithm 3 Check whether a class is split into two classes
    #1: procedure CLASSSPLITMATCH(InstructorModel, StudentModel)
    @staticmethod
    def class_split_match(instructor_model: UMLModel, student_model: UMLModel, attr_match_map: Dict[UMLAttribute, UMLAttribute], misplaced_attr_map: Dict[UMLAttribute, UMLAttribute], oper_matched_map: Dict[UMLOperation, UMLOperation], misplaced_oper_map: Dict[UMLOperation, UMLOperation]) -> Dict[UMLClass, Tuple[UMLClass, UMLClass]]:
        logger.info("starting class split match method")
        split_class_map: Dict[UMLClass, Tuple[UMLClass, UMLClass]] = {}

        #1: instList← InstructorModel.getClass()
        inst_list: List[UMLClass] = instructor_model.class_list
        #2: studList← StudentModel.getClass()
        stud_list: List[UMLClass] = student_model.class_list

        #3: for all Class Cs0 in studList, Cs1 in studList do
        for cs0 in stud_list:
            for cs1 in stud_list:
                #4: if Cs0 and Cs1 has 1-to-multiple association then
                if cs0 != cs1 and any(rel for rel in cs1.relations if rel.type == UMLRelationType.ASSOCIATION and rel.destination == cs0 and rel.s_multiplicity == "1" and rel.d_multiplicity == "*"):
                    #5: for all Class Ci in instList do
                    for ci in inst_list:
                        #6: if Ci has same properties with Cs0 and Cs1 then
                        # NOTE: the checks within the method could be done earlier to exclude classes that are not relevant for the split check
                        # but we decided to keep the structure of the algorithm as it is
                        if ContentCheck.classes_have_same_properties(ci, cs0, cs1, attr_match_map, misplaced_attr_map, oper_matched_map, misplaced_oper_map):
                            #7: splitClassMap.put(Ci, <Cs0,Cs1>)
                            split_class_map[ci] = (cs0, cs1)
                            break  # found a match, no need to continue checking other classes
        logger.info(f"found {len(split_class_map)} class splits")
        logger.debug(f"split class map: { {str(k): str(v) for k, v in split_class_map.items()} }")
        logger.info("finished class split match method\n")
        #8: return splitClassMap
        return split_class_map

    #Algorithm 4 Check whether a class is merged into another class
    #1: procedure CLASSMERGEMATCH(InstructorModel, StudentModel)
    @staticmethod
    def class_merge_match(instructor_model: UMLModel, class_match_map: Dict[UMLClass, UMLClass], misplaced_attr_map: Dict[UMLAttribute, UMLAttribute], misplaced_oper_map: Dict[UMLOperation, UMLOperation]) -> Dict[Tuple[UMLClass, UMLClass], UMLClass]:
        logger.info("starting class merge match method")
        merge_class_map: Dict[Tuple[UMLClass, UMLClass], UMLClass] = {}

        #2: for all Class Ci1 in InstructorModel matched with Cs in StudentModel do
        for ci1, cs in class_match_map.items():
            #3: for all Class Ci2 in InstructorModel which content is misplaced in Cs do
            for ci2 in instructor_model.class_list:
                if ContentCheck.class_contains_missplaced_properties(ci2, cs, misplaced_attr_map, misplaced_oper_map):
                    #4: if Ci1 has association with Ci2 then
                    if any(rel for rel in ci1.relations if rel.destination == ci2 and rel.source == ci1 and rel.type == UMLRelationType.ASSOCIATION):
                        #5: mergeClassMap.put(Cs,<Ci1,Ci2>)
                        merge_class_map[(ci1, ci2)] = cs
        logger.info(f"found {len(merge_class_map)} class merges")
        logger.debug(f"merge class map: { {str(k): str(v) for k, v in merge_class_map.items()} }")
        logger.info("finished class merge match method\n")
        #7:return mergeClassMap
        return merge_class_map