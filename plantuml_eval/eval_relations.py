from UML_model.uml_model import UMLModel
from UML_model.uml_class import UMLClass
from UML_model.uml_enum import UMLEnum
from UML_model.uml_relation import UMLRelation
from grading.grade_metamodel import GradeModel
from plantuml_eval.eval_helper_functions import EvalHelper

from typing import List, Dict, Tuple, Union, Optional
import logging

logger = logging.getLogger("relation_eval")
logger.setLevel(logging.DEBUG)

if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(levelname)s] - %(name)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

class RelationComperator:
    #Algorithm 5 Compare association in InstructorModel and StudentModel 
    #1: procedure COMPAREASSOC(InstructorModel, StudentModel,missClassList) 
    @staticmethod
    def compare_relations(instructor_model: UMLModel, student_model: UMLModel, class_match_map: Dict[UMLClass, UMLClass], miss_class_list: List[UMLClass], enum_match_map: Dict[UMLEnum, UMLEnum], enum_miss_list: List[UMLEnum], grade_model: Optional[GradeModel] = None) -> Tuple[Dict[UMLRelation, UMLRelation], List[UMLRelation]]:
        logger.debug("Starting relation comparison")
        relation_match_map: Dict[UMLRelation, UMLRelation] = {}
        derivation_list: List[UMLRelation] = []
        miss_relation_list: List[UMLRelation] = []

        possible_relation_class_map: Dict[UMLClass, List[UMLClass]] = {}
        element_match_map: Dict[Union[UMLClass, UMLEnum], Union[UMLClass, UMLEnum]] = class_match_map | enum_match_map
        possible_relation_map: Dict[UMLRelation, List[UMLRelation]] = {}

        #2: instAssocList←InstructorModel.getAssociation() 
        inst_relation_list: List[UMLRelation] = instructor_model.relation_list
        #3: studAssocList ← StudentModel.getAssociation() 
        stud_relation_list: List[UMLRelation] = student_model.relation_list

        #4: for all Association Ai in instAssocList, As in studAssocList do 
        for ri in inst_relation_list:
            possible_relation_map[ri] = []
            for rs in stud_relation_list:
                print(f"Comparing {ri} with {rs}")
                #5: if Ai and As connect two pairs of matched classes then 
                if ((ri.source, rs.source) in element_match_map.items() and (ri.destination, rs.destination) in element_match_map.items()) or ((ri.source, rs.destination) in element_match_map.items() and (ri.destination, rs.source) in element_match_map.items()):
                    logger.debug(f"Possible relation match found: {ri} with {rs}")
                    #6: associationMatchMap.put(As, Ai) 
                    possible_relation_map[ri].append(rs)

        #**added additionally**
        safe_relation_matches, best_relation_match_map = EvalHelper.handle_possible_matches(possible_relation_map, grade_model, element_match_map)
        new_matched_relations, new_miss_inst_relations = EvalHelper.handle_safe_and_best_matches(inst_relation_list, safe_relation_matches, best_relation_match_map, relation_match_map)
        relation_match_map.update(new_matched_relations)
        miss_relation_list.extend(new_miss_inst_relations)
        logger.debug(f"{len(miss_relation_list)} missing relations found")
        logger.debug(f"missing relations: {', '.join(str(r) for r in miss_relation_list)}")

        # TODO: alternative structure for association link to associated classes

        all_reachable_classes: Dict[UMLClass, List[UMLClass]] = instructor_model.build_class_reachability_map()
        #7: for all class C in missClassList do
        for c in miss_class_list:
            possible_relation_class_map[c] = []
            #8: for all Class Ci in InstructorModel is connected with C do
            for ci in all_reachable_classes.get(c, []):
                #9: possibleAssocMap.get(C).add(Ci)
                possible_relation_class_map[c].append(ci)
        logger.debug(f"{len(possible_relation_class_map)} classes with possible associations found")

        #10: for all Association As in studAssocList do
        for rs in stud_relation_list:
            #11: endClass1 ← As.getEnd1()
            source_class = class_match_map.get(rs.source)
            #12: endClass2 ← As.getEnd2() 
            destination_class = class_match_map.get(rs.destination)
            #13: for all Key Class C in possibleAssocMap do 
            #14: possibleClassList←possibleAssocMap.get(C) 
            for c, possible_class_list in possible_relation_class_map.items():
                #15: if endClass1 in possibleClassList and endClass2 in possibleClassList then 
                if source_class in possible_class_list and destination_class in possible_class_list:
                    #16:derivationList.add(As)
                    derivation_list.append(rs)
                    logger.debug(f"Derivation found: {str(rs)} for classes {source_class} and {destination_class}")

        logger.info(f"Association comparison complete: {len(relation_match_map)} matches found, {len(derivation_list)} derivations found")
        logger.info("finished compare relations method\n")            
        #17: return associationMatchMap, derivationList
        return relation_match_map, derivation_list
    
    # TODO: Enum relations