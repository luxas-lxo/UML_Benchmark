from UML_model.uml_class import UMLClass
from UML_model.uml_element import UMLElement

from typing import List, Tuple, Dict

class RelationCheck:
    # klappt nur wenn die anderen beziehungen zu bereits gemappten klassen vorhanden
    @staticmethod
    def relation_match(list_s: List[UMLElement], list_i: List[UMLElement], class_match_map: Dict[UMLClass, UMLClass], threshold: float = 0.5) -> Tuple[bool, float]:
        if not list_s or not list_i:
            return (False, 0)
        reverse_class_match_map = {v: k for k, v in class_match_map.items()}
        mapped_list_s = [reverse_class_match_map.get(cs).name for cs in list_s if reverse_class_match_map.get(cs)]
        set_s, set_i = set(mapped_list_s), {ci.name for ci in list_i}
        overlap = len(set_s & set_i)
        similarity = overlap / max(len(set_s), len(set_i))
        return (similarity >= threshold, similarity)