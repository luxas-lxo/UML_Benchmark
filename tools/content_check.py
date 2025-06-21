from UML_model.uml_class import UMLClass
from tools.semantic_check import SemanticCheck
from tools.syntactic_check import SyntacticCheck

from typing import Tuple

class ContentCheck:

    @staticmethod
    def content_match(inst_class: UMLClass, stud_class: UMLClass, threshold: float = 0.5) -> Tuple[bool, float]:
        total = len(inst_class.attributes) + len(inst_class.operations)
        if total == 0:
            return (False, 0)
        
        match_count = 0

        for inst_att in inst_class.attributes:
            for stud_att in stud_class.attributes:
                if SyntacticCheck.syntactic_match(inst_att.name, stud_att.name)[0] or SemanticCheck.semantic_match(inst_att.name, stud_att.name)[0]:
                    match_count += 1
                    break

        for inst_opr in inst_class.operations:
            for stud_opr in stud_class.operations:
                if SyntacticCheck.syntactic_match(inst_opr.name, stud_opr.name)[0] or SemanticCheck.semantic_match(inst_opr.name, stud_opr.name)[0]:
                    match_count += 1
                    break

        similarity = match_count / total
        return (similarity >= threshold, similarity)