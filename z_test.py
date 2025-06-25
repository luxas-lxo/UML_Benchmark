from UML_model.uml_model import UMLModel
from plantuml_eval.eval_classes import ClassComperator
from grading.grade_metamodel import GradeModel, StructuralFeature
from tools.semantic_check import SemanticCheck

print(f"SemanticCheck: {SemanticCheck.semantic_match("aroma", "taste")}")
plant_uml_inst = """
@startuml
class square {
    file
    rank
}
class move
class position {
    /check
    /checkmate
    /stalemate
    executeMove()
    capturePiece()
}
@enduml
"""
plant_uml_stud = """
@startuml
class square {
    file
    rank}
class position
class move {
    file
    rank}
@enduml
"""
inst_model = UMLModel(plant_uml_inst)
stud_model = UMLModel(plant_uml_stud)
matches, missing = ClassComperator.compare_classes(inst_model, stud_model)