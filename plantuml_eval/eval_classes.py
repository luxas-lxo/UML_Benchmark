from tools.syntactic_check import SyntacticCheck
from tools.semantic_check import SemanticCheck
from tools.content_check import ContentCheck
from tools.relation_check import RelationCheck
from UML_model.uml_class import UMLClass
from UML_model.uml_element import UMLElement

from enum import Enum
from typing import List, Dict


class MatchType(Enum):
    SyntacticMatch = "syntax"
    SemanticMatch = "semantic"
    ContentMatch = "content"
    RelationMatch = "relation"
    NoMatch = "none"

class ClassMatch:
    def __init__(self, class_matched: UMLClass, class_to: UMLClass, match_type: MatchType, score: float = 0):
        self.class_matched = class_matched
        self.class_to = class_to
        self.match_type = match_type
        self.score = score


class ClassComperator:

    #Algorithm 1 Compare Classes
    #1: procedure COMPARECLASS(InstructorModel,StudentModel)
    #2: instList← InstructorModel.getClass()
    #3: studList← StudentModel.getClass()
    @staticmethod
    def compare_classes(instructor_classes: List[UMLClass], student_classes: List[UMLClass]):
        possible_matches: Dict[UMLClass, List[ClassMatch]] = {}  
        class_match_map: Dict[UMLClass, UMLClass] = {}
        miss_class_list: List[UMLClass] = []
        final_miss_class_list: List[UMLClass] = []

        #4: for all Class Ci in instList, Cs in studList do
        for ci in instructor_classes:
            possible_matches[ci] = []
            for cs in student_classes:
                #5: if syntacticMatch(Cs.name, Ci.name) or
                if (res := SyntacticCheck.syntactic_match(ci.name, cs.name))[0]:
                    #8: storePossibleMatch(Ci, Cs)
                    possible_matches[ci].append(ClassMatch(cs, ci, MatchType.SyntacticMatch, res[1]))
                #6: semanticMatch(Cs.name, Ci.name) ) or
                if (res := SemanticCheck.semantic_match(ci.name, cs.name))[0]:
                    #8: storePossibleMatch(Ci, Cs)
                    possible_matches[ci].append(ClassMatch(cs, ci, MatchType.SemanticMatch, res[1]))
                #7: contentMatch(Cs.content, Ci.content) then
                if (res := ContentCheck.content_match(ci, cs))[0]: # TODO: bei attributen/operationen auch semantik und syntax prüfen
                    #8: storePossibleMatch(Ci, Cs)
                    possible_matches[ci].append(ClassMatch(cs, ci, MatchType.ContentMatch, res[1]))
                
        #9: for all Class Ci in instList do
        for ci, matches in possible_matches.items():
            #10: if ∃ matched classes for Ci then
            if matches:
                #11: find among the matches of Ci the Cbest
                #12: that obtains the highest mark among the matches
                best_match = matches[0].class_matched  # TODO find best possible match
                #13: classMatchMap.put(Ci, Cbest)
                class_match_map[ci] = best_match
            else:
                miss_class_list.append(ci)

        unmatched_stud_classes = [cls for cls in student_classes if cls not in class_match_map.values()]
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
                    possible_matches[ci].append(ClassMatch(cs, ci, MatchType.RelationMatch, res[1]))
            #20: classMatchMap.put(Ci, Cs)
            if possible_matches[ci]:
                best_match = possible_matches[ci][0]  # TODO find best possible match
                class_match_map[ci] = best_match.class_matched
            #21: if no match exists for Ci then 
            if ci not in class_match_map:
                #22: missClassList.add(Ci)
                final_miss_class_list.append(ci)  
        
        #23: return classMatchMap, missClassList
        return class_match_map, final_miss_class_list   


