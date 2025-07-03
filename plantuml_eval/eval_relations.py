from UML_model.uml_model import UMLModel
from UML_model.uml_class import UMLClass
from UML_model.uml_enum import UMLEnum
from UML_model.uml_element import UMLElement
from UML_model.uml_relation import UMLRelation, UMLRelationType
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
    def compare_relations(instructor_model: UMLModel, student_model: UMLModel, class_match_map: Dict[UMLClass, UMLClass], miss_inst_class_list: List[UMLClass], enum_match_map: Dict[UMLEnum, UMLEnum], inst_enum_miss_list: List[UMLEnum], grade_model: Optional[GradeModel] = None) -> Tuple[Dict[UMLRelation, UMLRelation], Dict[UMLRelation, Tuple[UMLRelation, UMLRelation]], Dict[Tuple[UMLClass, UMLClass],UMLRelation], Dict[Tuple[UMLRelation, UMLRelation], UMLRelation], Dict[UMLRelation, Tuple[UMLRelation, UMLRelation]], List[UMLRelation]]:
        # NOTE: this algorithm is extended to also match relations between classes and enums
        logger.debug("Starting relation comparison")
        # variables for returning
        relation_match_map: Dict[UMLRelation, UMLRelation] = {}
        inst_assoc_link_match_map: Dict[UMLRelation, Tuple[UMLRelation, UMLRelation]] = {}
        stud_assoc_link_match_map: Dict[Tuple[UMLClass, UMLClass], UMLRelation] = {}
        sec_derivation_inst_map: Dict[Tuple[UMLRelation, UMLRelation], UMLRelation] = {}
        sec_derivation_stud_map: Dict[UMLRelation, Tuple[UMLRelation, UMLRelation]] = {}
        miss_relation_list: List[UMLRelation] = []

        # variables for internal use
        element_match_map: Dict[Union[UMLClass, UMLEnum], Union[UMLClass, UMLEnum]] = class_match_map | enum_match_map
        reversed_element_match_map: Dict[Union[UMLClass, UMLEnum], Union[UMLClass, UMLEnum]] = {v: k for k, v in element_match_map.items()}
        missing_inst_elms: List[UMLElement] = miss_inst_class_list + inst_enum_miss_list
        miss_stud_class_list: List[UMLClass] = [cls for cls in student_model.class_list if cls not in class_match_map.values()]
        stud_enum_miss_list: List[UMLEnum] = [enu for enu in student_model.enum_list if enu not in enum_match_map.values()]
        missing_stud_elms: List[UMLElement] = miss_stud_class_list + stud_enum_miss_list

        possible_relation_map: Dict[UMLRelation, List[UMLRelation]] = {}
        all_reachable_inst_elements: Dict[UMLElement, List[UMLElement]] = instructor_model.build_reachability_map()
        possible_relation_class_map: Dict[UMLClass, List[UMLClass]] = {}
        derivation_in_inst_model: Dict[UMLClass, List[UMLRelation]] = {}
        
        all_reachable_stud_elements: Dict[UMLElement, List[UMLElement]] = student_model.build_reachability_map()
        derivation_in_stud_model: Dict[UMLClass, List[UMLRelation]] = {}
        missing_stud_relations: List[UMLRelation] = []

        #2: instAssocList←InstructorModel.getAssociation() 
        inst_relation_list: List[UMLRelation] = instructor_model.relation_list
        #3: studAssocList ← StudentModel.getAssociation() 
        stud_relation_list: List[UMLRelation] = student_model.relation_list

        #4: for all Association Ai in instAssocList, As in studAssocList do 
        for ri in inst_relation_list:
            possible_relation_map[ri] = []
            for rs in stud_relation_list:
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

        # NOTE:**added additionally**
        # finding alternative structure for association link to associated classes
        logger.debug("Finding association links alternative matches")
        for ri in miss_relation_list:
            if ri.type == UMLRelationType.ASSOCIATION_LINK:
                inst_assoc: UMLRelation = ri.destination
                stud_cls_1 = class_match_map.get(inst_assoc.source)
                stud_cls_2 = class_match_map.get(inst_assoc.destination)
                stud_assoc_class = class_match_map.get(ri.source)
                stud_ends = stud_assoc_class.get_relation_ends() if stud_assoc_class else []
                if stud_assoc_class and stud_cls_1 in stud_ends and stud_cls_2 in stud_ends:
                    for rs_1 in stud_relation_list:
                        if rs_1.equals(UMLRelation(UMLRelationType.ASSOCIATION, stud_cls_1, stud_assoc_class)):
                            break
                    for rs_2 in stud_relation_list:
                        if rs_1 != rs_2 and rs_2.equals(UMLRelation(UMLRelationType.ASSOCIATION, stud_cls_2, stud_assoc_class)):
                            break
                    if rs_1 and rs_2:
                        inst_assoc_link_match_map[ri] = (rs_1, rs_2)
                        logger.debug(f"Association link match found: {ri} with classes {rs_1} and {rs_2}")

        student_miss_relations = [rel for rel in student_model.relation_list if rel not in relation_match_map.values()]
        for rs in student_miss_relations:
            if rs.type == UMLRelationType.ASSOCIATION_LINK:
                stud_assoc: UMLRelation = rs.destination
                inst_cls_1 = reversed_element_match_map.get(stud_assoc.source)
                inst_cls_2 = reversed_element_match_map.get(stud_assoc.destination)
                inst_assoc_class = reversed_element_match_map.get(rs.source)
                inst_ends = inst_assoc_class.get_relation_ends() if inst_assoc_class else []
                if inst_assoc_class and inst_cls_1 in inst_ends and inst_cls_2 in inst_ends:
                    for ri_1 in inst_relation_list:
                        if ri_1.equals(UMLRelation(UMLRelationType.ASSOCIATION, inst_cls_1, inst_assoc_class)):
                            break
                    for ri_2 in inst_relation_list:
                        if ri_1 != ri_2 and ri_2.equals(UMLRelation(UMLRelationType.ASSOCIATION, inst_cls_2, inst_assoc_class)):
                            break
                    if ri_1 and ri_2:
                        stud_assoc_link_match_map[(ri_1, ri_2)] = rs
                        logger.debug(f"Association link match found: {rs} with classes {ri_1} and {ri_2}")

        logger.debug(f"{len(inst_assoc_link_match_map)} association link matches found in instructor model")
        logger.debug(f"{len(stud_assoc_link_match_map)} association link matches found in student model")

        #7: for all class C in missClassList do
        for e in missing_inst_elms:
            possible_relation_class_map[e] = []
            #8: for all Class Ci in InstructorModel is connected with C do
            for ci in all_reachable_inst_elements.get(e, []):
                #9: possibleAssocMap.get(C).add(Ci)
                possible_relation_class_map[e].append(ci)
        logger.debug(f"{len(possible_relation_class_map)} elements with possible relations in instructor model found")

        #10: for all Association As in studAssocList do
        for rs in stud_relation_list:
            #11: endClass1 ← As.getEnd1()
            source = reversed_element_match_map.get(rs.source)
            #12: endClass2 ← As.getEnd2() 
            destination = reversed_element_match_map.get(rs.destination)
            #13: for all Key Class C in possibleAssocMap do 
            #14: possibleClassList←possibleAssocMap.get(C) 
            for e, possible_elm_list in possible_relation_class_map.items():
                derivation_in_inst_model[e] = derivation_in_inst_model.get(e, [])
                #15: if endClass1 in possibleClassList and endClass2 in possibleClassList then 
                if source in possible_elm_list and destination in possible_elm_list:
                    #16:derivationList.add(As)
                    derivation_in_inst_model[e].append(rs)
                    logger.debug(f"Derivation found: {str(rs)} for classes {source} and {destination}")

        # NOTE:**added additionally**
        # finds second degree derivations (i.e. an instructor class that is not matched as a connection between two student classes)
        # could be extendet for higher degree but for now only second degree derivations are considered
        for e, derivation in derivation_in_inst_model.items():
            for rs in derivation:
                source = reversed_element_match_map.get(rs.source)
                destination = reversed_element_match_map.get(rs.destination)
                if source and destination:
                    for rel_1 in miss_relation_list:
                        if rel_1 and rel_1.classes_equal(UMLRelation(UMLRelationType.UNKNOWN, source, e)):
                            for rel_2 in miss_relation_list:
                                if rel_2 and rel_2.classes_equal(UMLRelation(UMLRelationType.UNKNOWN, e, destination)):
                                    # Found a second degree derivation
                                    sec_derivation_inst_map[(rel_1, rel_2)] = rs
                                    logger.debug(f"Second degree derivation found: {str(rs)} for relations {str(rel_1)} and {str(rel_2)}")

        # NOTE:**added additionally**
        # same proceddure as above just for unmatched student classes
        possible_relation_class_map = {}
        missing_stud_relations = [rel for rel in student_model.relation_list if rel not in relation_match_map.values()]

        for e in missing_stud_elms:
            possible_relation_class_map[e] = []
            for es in all_reachable_stud_elements.get(e, []):
                possible_relation_class_map[e].append(es)
        logger.debug(f"{len(possible_relation_class_map)} elements with possible relations in student model found")

        for ri in inst_relation_list:
            source = element_match_map.get(ri.source)
            destination = element_match_map.get(ri.destination)
            for e, possible_elm_list in possible_relation_class_map.items():
                derivation_in_stud_model[e] = derivation_in_stud_model.get(e, [])
                if source in possible_elm_list and destination in possible_elm_list:
                    if ri not in relation_match_map:
                        derivation_in_stud_model[e].append(ri)
                        logger.debug(f"Derivation found: {str(ri)} for classes {source} and {destination}")

        # finds second degree derivations (i.e. an student class that is not matched as a connection between two instructor classes)
        for e, derivation in derivation_in_stud_model.items():
            for ri in derivation:
                source = element_match_map.get(ri.source)
                destination = element_match_map.get(ri.destination)
                if source and destination:
                    for rel_1 in missing_stud_relations:
                        if rel_1 and rel_1.classes_equal(UMLRelation(UMLRelationType.UNKNOWN, source, e)):
                            for rel_2 in missing_stud_relations:
                                if rel_2 and rel_2.classes_equal(UMLRelation(UMLRelationType.UNKNOWN, e, destination)):
                                    # Found a second degree derivation
                                    sec_derivation_stud_map[ri] = (rel_1, rel_2)
                                    logger.debug(f"Second degree derivation found: {str(ri)} for relations {str(rel_1)} and {str(rel_2)}")

        miss_relation_list = [
            rel for rel in miss_relation_list
            if not relation_match_map.get(rel)
            and not inst_assoc_link_match_map.get(rel)
            and not any(k.destination == rel for k in inst_assoc_link_match_map.keys())
            and not any(k[0] == rel for k in stud_assoc_link_match_map.keys())
            and not any(k[1] == rel for k in stud_assoc_link_match_map.keys())
            and not any(k[0] == rel for k in sec_derivation_inst_map.keys())
            and not any(k[1] == rel for k in sec_derivation_inst_map.keys())
            and not sec_derivation_stud_map.get(rel)
        ]
        logger.info(f"Relation comparison complete: {len(relation_match_map)} matches found, {len(sec_derivation_inst_map) + len(sec_derivation_stud_map)} derivations found, {len(miss_relation_list)} missing relations found")
        logger.info("finished compare relations method\n")
        #17: return associationMatchMap, derivationList
        return relation_match_map, inst_assoc_link_match_map, stud_assoc_link_match_map, sec_derivation_inst_map, sec_derivation_stud_map, miss_relation_list
        # TODO: find best matches for second degree derivations, alternative association links