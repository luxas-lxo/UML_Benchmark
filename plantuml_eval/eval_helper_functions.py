from UML_model.uml_class import UMLClass, UMLAttribute, UMLOperation
from UML_model.uml_enum import UMLEnum, UMLValue
from UML_model.uml_relation import UMLRelation
from grading.grade_metamodel import GradeModel
from grading.grade_reference import GradeReference

from typing import List, Dict, Optional, Tuple, Union
import logging
from collections import Counter
from scipy.optimize import linear_sum_assignment
import numpy as np


logger = logging.getLogger("helper_eval")
logger.setLevel(logging.DEBUG)

if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(levelname)s] - %(name)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

class EvalHelper:
    # helper for algorithm 1, 2, 6
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

    # helper for algorithm 1, 2, 6
    @staticmethod
    def find_best_match_assignment(filtered_possible_matches: Dict[GradeReference, List[GradeReference]], grade_model: Optional[GradeModel] = None, element_match_map: Optional[Dict[Union[UMLClass, UMLEnum], Union[UMLClass, UMLEnum]]] = None) -> Dict[GradeReference, GradeReference]:
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
                elif isinstance(elem, UMLEnum):
                    score = grade_model.temp_grade_enum(match, elem)[0]
                    logger.debug(f"Grading enum {elem.name} against {match.name}: score = {score}")
                elif isinstance(elem, UMLRelation):
                    if element_match_map is None:
                        logger.warning("Element match map is None, cannot grade relations properly.")
                        score = 0.0
                    else:
                        score = grade_model.temp_grade_relation(match, elem, element_match_map)[0]
                        logger.debug(f"Grading relation {elem.name} against {match.name}: score = {score}")
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

    # helper for algorithm 1, 2, 6
    @staticmethod
    def handle_possible_matches(possible_matches: Dict[GradeReference, List[GradeReference]], grade_model: Optional[GradeModel] = None, element_match_map: Optional[Dict[Union[UMLClass, UMLEnum], Union[UMLClass, UMLEnum]]] = None) -> Tuple[Dict[GradeReference, GradeReference], Dict[GradeReference, GradeReference]]:
        safe_matches: Dict[GradeReference, GradeReference] = {}
        best_match_map: Dict[GradeReference, GradeReference] = {}
        filtered_possible_matches: Dict[GradeReference, List[GradeReference]] = {}
        if possible_matches:
            logger.debug(f"possible matches: { {str(k): [str(v) for v in vs] for k, vs in possible_matches.items()} }")
            # find safe matches first
            safe_matches = EvalHelper.get_safe_matches(possible_matches)
            # remove safe matches from possible matches
            filtered_possible_matches = {
                cls: matches for cls, matches in possible_matches.items() if cls not in safe_matches and matches
            }
        # find best matches among the remaining possible matches
        if filtered_possible_matches:
            logger.debug(f"filtered possible matches: { {str(k): [str(v) for v in vs] for k, vs in filtered_possible_matches.items()} }")
            best_match_map = EvalHelper.find_best_match_assignment(filtered_possible_matches, grade_model, element_match_map)

        return safe_matches, best_match_map
  
    # helper for algorithm 2, 6
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
