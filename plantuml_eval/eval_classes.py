from tools.syntactic_check import SyntacticCheck
from tools.semantic_check import SemanticCheck
from tools.content_check import ContentCheck
from tools.relation_check import RelationCheck
from UML_model.uml_class import UMLClass, UMLAttribute, UMLOperation, UMLVisability
from UML_model.uml_element import UMLElement
from UML_model.uml_model import UMLModel

from enum import Enum
from typing import List, Dict, Optional


class MatchType(Enum):
    SyntacticMatch = "syntax"
    SemanticMatch = "semantic"
    ContentMatch = "content"
    RelationMatch = "relation"
    NoMatch = "none"

class Match:
    def __init__(self, matched: UMLElement, to_inst: UMLElement, match_type: MatchType, score: float = 0):
        self.matched = matched
        self.to_inst = to_inst
        self.match_type = match_type
        self.score = score


class ClassComperator:
    @staticmethod
    def find_best_class_match(inst_class: UMLClass, possible_matches: List[Match]):
        #TODO später vllt noch mit wirklicher bewertung?
        best_score = 0
        best_match: Optional[Match] = None
        for m in possible_matches:
            if m.score > best_score:
                best_match = m
        return best_match
    
    @staticmethod
    def find_best_content_match(inst_att: UMLAttribute, possible_matches: List[Match]):
        #TODO später vllt noch mit wirklicher bewertung?
        best_score = 0
        best_match: Optional[Match] = None
        for m in possible_matches:
            if m.score > best_score:
                best_match = m
        return best_match

    #Algorithm 1 Compare Classes
    #1: procedure COMPARECLASS(InstructorModel,StudentModel)
    @staticmethod
    def compare_classes(instructor_model: UMLModel, student_model: UMLModel):
        possible_matches: Dict[UMLClass, List[Match]] = {}  
        class_match_map: Dict[UMLClass, UMLClass] = {}
        miss_class_list: List[UMLClass] = []
        final_miss_class_list: List[UMLClass] = []

        #2: instList← InstructorModel.getClass()
        instructor_classes: List[UMLClass] = instructor_model.class_list
        #3: studList← StudentModel.getClass()
        student_classes: List[UMLClass] = student_model.class_list

        #4: for all Class Ci in instList, Cs in studList do
        for ci in instructor_classes:
            possible_matches[ci] = []
            for cs in student_classes:
                #5: if syntacticMatch(Cs.name, Ci.name) or
                if (res := SyntacticCheck.syntactic_match(ci.name, cs.name))[0]:
                    #8: storePossibleMatch(Ci, Cs)
                    possible_matches[ci].append(Match(cs, ci, MatchType.SyntacticMatch, res[1]))
                #6: semanticMatch(Cs.name, Ci.name) ) or
                if (res := SemanticCheck.semantic_match(ci.name, cs.name))[0]:
                    #8: storePossibleMatch(Ci, Cs)
                    possible_matches[ci].append(Match(cs, ci, MatchType.SemanticMatch, res[1]))
                #7: contentMatch(Cs.content, Ci.content) then
                if (res := ContentCheck.content_match(ci, cs))[0]:
                    #8: storePossibleMatch(Ci, Cs)
                    possible_matches[ci].append(Match(cs, ci, MatchType.ContentMatch, res[1]))
                
        #9: for all Class Ci in instList do
        for ci, matches in possible_matches.items():
            #10: if ∃ matched classes for Ci then
            if matches:
                #11: find among the matches of Ci the Cbest
                #12: that obtains the highest mark among the matches 
                best_match = ClassComperator.find_best_class_match(ci, matches)
                #13: classMatchMap.put(Ci, Cbest)
                class_match_map[ci] = best_match.matched
            else:
                miss_class_list.append(ci)

        unmatched_stud_classes: List[UMLClass] = [cls for cls in student_classes if cls not in class_match_map.values()]
        #14: for all Class Ci in missClassList do 
        for ci in miss_class_list:
            #15: for all Class Cs in studList do 
            #16:if no match exists for Cs then 
            for cs in unmatched_stud_classes:
                #17: ListI← Ci.getAssociationEnds()
                list_i = ci.get_relation_ends()
                #18: ListS← Cs.getAssociationEnds()
                list_s = cs.get_relation_ends()
                #19: if assocMatch(ListS,ListI) then
                if (res := RelationCheck.relation_match(list_s, list_i, class_match_map))[0]:
                    #20: classMatchMap.put(Ci, Cs)
                    possible_matches[ci].append(Match(cs, ci, MatchType.RelationMatch, res[1]))
            #**added additionally**
            if possible_matches.get(ci):
                best_match = ClassComperator.find_best_class_match(ci, possible_matches[ci])
                class_match_map[ci] = best_match.matched
            #21: if no match exists for Ci then 
            if ci not in class_match_map:
                #22: missClassList.add(Ci)
                final_miss_class_list.append(ci)  
        
        #23: return classMatchMap, missClassList
        return class_match_map, final_miss_class_list   

    #Algorithm 2 Compare attributes and operations in InstructorModel with StudentModel 
    #1: procedure COMPARECONTENT(InstructorModel, StudentModel, classMatchMap) 
    @staticmethod
    def compare_content(instructor_model: UMLModel, student_model: UMLModel, class_match_map: Dict[UMLClass, UMLClass]):
        possible_attr_matches: Dict[UMLAttribute, List[Match]] = {}
        attr_match_map: Dict[UMLAttribute, UMLAttribute] = {}
        possible_missplaced_attr_matches: Dict[UMLAttribute, List[Match]] = {}
        misplaced_attr_map: Dict[UMLAttribute, UMLAttribute] = {}

        possible_oper_matches: Dict[UMLOperation, List[Match]] = {}
        oper_matched_map: Dict[UMLOperation, UMLOperation] = {}
        possible_missplaced_oper_matches: Dict[UMLOperation, List[Match]] = {}
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
                        possible_attr_matches[a_i].append(Match(a_s, a_i, MatchType.SyntacticMatch, res[1]))
                    #10:else if Ci is superClass of classMatchMap.get(Cs) and Ai is not private then 
                    elif c_i == reversed_class_match_map.get(c_s).super_class and a_i.visability != UMLVisability.PRIVATE:
                        #11:matchedAttrMap.put(As, Ai)
                        possible_attr_matches[a_i].append(Match(a_s, a_i, MatchType.SyntacticMatch, res[1]))
                #7:if Ai is synatax or semtantic match for As then 
                if (res := SemanticCheck.semantic_match(a_i.name, a_s.name))[0]:
                    #8:if classMatchMap.get(Cs).equals(Ci) then 
                    if class_match_map.get(c_i) == c_s:
                        #9:matchedAttrMap.put(As, Ai) 
                        possible_attr_matches[a_i].append(Match(a_s, a_i, MatchType.SemanticMatch, res[1]))
                    #10:else if Ci is superClass of classMatchMap.get(Cs) and Ai is not private then
                    elif c_i == reversed_class_match_map.get(c_s).super_class and a_i.visability != UMLVisability.PRIVATE:
                        #11:matchedAttrMap.put(As, Ai)
                        possible_attr_matches[a_i].append(Match(a_s, a_i, MatchType.SemanticMatch, res[1]))
            #**added additionally**
            if possible_attr_matches.get(a_i):
                best_match = ClassComperator.find_best_content_match(a_i, possible_attr_matches[a_i]) 
                attr_match_map[a_i] = best_match.matched
        
        #12: for all Attribute Ai in instAttrList, As in studAttrList do 
        unmatched_stud_attrs = [att for att in stud_att_list if att not in attr_match_map.values()]
        for a_i in inst_att_list:
            possible_missplaced_attr_matches[a_i] = []
            #13:if As not matched And Ai is synatax or semtantic match for As then 
            for a_s in unmatched_stud_attrs:
                if (res := SyntacticCheck.syntactic_match(a_i.name, a_s.name))[0]:
                    #14:misplaceAttrMap.put(As, Ai)
                    possible_missplaced_attr_matches[a_i].append(Match(a_s, a_i, MatchType.SyntacticMatch, res[1]))
                if (res := SemanticCheck.semantic_match(a_i.name, a_s.name))[0]:
                    #14:misplaceAttrMap.put(As, Ai)
                    possible_missplaced_attr_matches[a_i].append(Match(a_s, a_i, MatchType.SemanticMatch, res[1]))
            #**added additionally**
            if possible_missplaced_attr_matches.get(a_i):
                best_match = ClassComperator.find_best_content_match(a_i, possible_missplaced_attr_matches[a_i])
                misplaced_attr_map[a_i] = best_match.matched

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
                        possible_oper_matches[oi].append(Match(os, oi, MatchType.SyntacticMatch, res[1]))
                    #23:else if Ci is superClass of classMatchMap.get(Cs) and Oi is not private then 
                    elif ci == reversed_class_match_map.get(cs).super_class and oi.visability != UMLVisability.PRIVATE:
                        #24:matchedOperMap.put(Os, Oi) 
                        possible_oper_matches[oi].append(Match(os, oi, MatchType.SyntacticMatch, res[1]))
                #20:if Oi.synMatch(Os) or Oi.semanticMatch(Os) then
                if (res := SemanticCheck.semantic_match(oi.name, os.name))[0]:
                    #21:if classMatchMap.get(Cs) equals Ci then 
                    if class_match_map.get(ci) == cs:
                        #22:matchedOperMap.put(Os, Oi) 
                        possible_oper_matches[oi].append(Match(os, oi, MatchType.SemanticMatch, res[1]))
                    #23:else if Ci is superClass of classMatchMap.get(Cs) and Oi is not private then
                    elif ci == reversed_class_match_map.get(cs).super_class and oi.visability != UMLVisability.PRIVATE:
                        #24:matchedOperMap.put(Os, Oi)
                        possible_oper_matches[oi].append(Match(os, oi, MatchType.SemanticMatch, res[1]))
            #**added additionally**
            if possible_oper_matches.get(oi):
                best_match = ClassComperator.find_best_content_match(oi, possible_oper_matches[oi])
                oper_matched_map[oi] = best_match.matched

        #25: for all Operation Oi in instOperList, Os in studOperList do
        unmatched_stud_opers = [opr for opr in stud_opr_list if opr not in oper_matched_map.values()]
        for oi in inst_opr_list:
            possible_missplaced_oper_matches[oi] = []
            #26:if Os is not matched And Oi.synlMatch(Os) or Oi.semanticMatch(Os) then 
            for os in unmatched_stud_opers:
                if (res := SyntacticCheck.syntactic_match(oi.name, os.name))[0]:
                    #27:misplaceOperMap.put(Os, Oi) 
                    possible_missplaced_oper_matches[oi].append(Match(os, oi, MatchType.SyntacticMatch, res[1]))
                    #28:instOperList.put(Oi, true) 
                    #**skipped**
                if (res := SemanticCheck.semantic_match(oi.name, os.name))[0]:
                    #27:misplaceOperMap.put(Os, Oi)
                    possible_missplaced_oper_matches[oi].append(Match(os, oi, MatchType.SemanticMatch, res[1]))
                    #28:instOperList.put(Oi, true) 
                    #**skipped**
            #**added additionally**
            if possible_missplaced_oper_matches.get(oi):
                best_match = ClassComperator.find_best_content_match(oi, possible_missplaced_oper_matches[oi])
                misplaced_oper_map[oi] = best_match.matched

        #29: return matchedAttrMap, misplaceAttrMap, matchedOperMap, misplaceOperMap
        return attr_match_map, misplaced_attr_map, oper_matched_map, misplaced_oper_map

