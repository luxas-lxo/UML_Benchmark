from UML_model.uml_class import UMLClass
from UML_model.uml_element import UMLElement

from typing import List, Tuple, Dict
import logging

logger = logging.getLogger("relation_check")
logger.setLevel(logging.DEBUG)

if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(levelname)s] - %(name)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

class RelationCheck:
    # NOTE: only works if the other relationships are to already mapped destination classes
    @staticmethod
    def relation_match(list_s: List[UMLElement], list_i: List[UMLElement], class_match_map: Dict[UMLClass, UMLClass], threshold: float = 0.5) -> Tuple[bool, float]:
        if not list_s or not list_i:
            return (False, 0)
        reverse_class_match_map = {v: k for k, v in class_match_map.items()}
        mapped_list_s = [reverse_class_match_map.get(cs).name for cs in list_s if reverse_class_match_map.get(cs)]
        set_s, set_i = set(mapped_list_s), {ci.name for ci in list_i}
        overlap = len(set_s & set_i)
        similarity = overlap / max(len(set_s), len(set_i))
        if similarity >= threshold:
            logger.debug(f"Relation match: {set_s} and {set_i}: score = {similarity:.2f}")
        return (similarity >= threshold, similarity)