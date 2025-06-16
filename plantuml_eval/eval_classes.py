import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from grading.grade_model import GradeModel
from grading.grade_meta_model import GradeModel, EObjectGrade, EStructuralFeatureGrade
from tools.syntactic_check import SyntacticCheck
from tools.semantic_check import SemanticCheck
from tools.content_check import ContentCheck
from UML_model.uml_class import UMLClass
from UML_model.uml_model import UMLModel
from UML_model.uml_element import UMLElement

from typing import List, Dict

class ClassComperator:

    # klappt nur wenn die anderen beziehungen zu bereits gemappten klassen vorhanden
    @staticmethod
    def relation_match(list_s: List[UMLElement], list_i: List[UMLElement], class_match_map: Dict[UMLClass, UMLClass], threshold: float = 0.5) -> bool:
        if not list_s or not list_i:
            return False
        reverse_class_match_map = {v: k for k, v in class_match_map.items()}
        mapped_list_s = [reverse_class_match_map.get(cs).name for cs in list_s if reverse_class_match_map.get(cs)]
        set_s, set_i = set(mapped_list_s), set(ci.name for ci in list_i)
        print(set_i)
        print(set_s)
        overlap = len(set_s & set_i)
        print(overlap)
        similarity = overlap / max(len(set_s), len(set_i))
        print(similarity)
        return similarity >= threshold

    #Algorithm 1 Compare Classes
    #1: procedure COMPARECLASS(InstructorModel,StudentModel)
    #2: instList← InstructorModel.getClass()
    #3: studList← StudentModel.getClass()
    @staticmethod
    def compare_classes(instructor_classes: List[UMLClass], student_classes: List[UMLClass]):
        possible_matches: Dict[UMLClass, List[UMLClass]] = {}  
        class_match_map: Dict[UMLClass, UMLClass] = {}
        miss_class_list: List[UMLClass] = []
        final_miss_class_list: List[UMLClass] = []

        #4: for all Class Ci in instList, Cs in studList do
        for ci in instructor_classes:
            possible_matches[ci] = []
            for cs in student_classes:
                #5: if syntacticMatch(Cs.name, Ci.name) or
                if SyntacticCheck.syntactic_match(ci.name, cs.name):
                    #8: storePossibleMatch(Ci, Cs)
                    possible_matches[ci].append(cs)
                #6: semanticMatch(Cs.name, Ci.name) ) or
                elif SemanticCheck.semantic_match(ci.name, cs.name):
                    #8: storePossibleMatch(Ci, Cs)
                    possible_matches[ci].append(cs)
                #7: contentMatch(Cs.content, Ci.content) then
                elif ContentCheck.content_match(ci, cs):
                    #8: storePossibleMatch(Ci, Cs)
                    possible_matches[ci].append(cs)
                

        #9: for all Class Ci in instList do
        for ci, matches in possible_matches.items():
            #10: if ∃ matched classes for Ci then
            if matches:
                #11: TODO: find among the matches of Ci the Cbest
                #12: TODO: that obtains the highest mark among the matches
                best_match = matches[0]  
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
                if ClassComperator.relation_match(list_s, list_i, class_match_map):
                    #20: classMatchMap.put(Ci, Cs)
                    class_match_map[ci] = cs
            #21: if no match exists for Ci then
            if ci not in class_match_map:
                #22: missClassList.add(Ci)
                final_miss_class_list.append(ci)  
        
        #23: return classMatchMap, missClassList
        return class_match_map, final_miss_class_list   
"""
class_grades = EObjectGrade()
class_grades.points = 2.0

attr_grades = EStructuralFeatureGrade()
attr_grades.points = 1.0
class_grades.structuralgrades.append(attr_grades)

print(f"Class Grade: {class_grades.points}")
print(f"Attribute Grade: {class_grades.structuralgrades[0].points}")
"""
"""  
grades = GradeModel()
grades.class_points["piece"] = 1.0
grades.class_points["position"] = 1.0
grades.class_points["square"] = 1.0
grades.class_points["move"] = 1.0
grades.attribute_points["position"] = {"/check": 1.0, "/checkmate": 1.0, "/stalemate": 1.0}
grades.attribute_points["square"] = {"file": 0.5, "rank": 0.5}
grades.operation_points["position"] = {"executeMove()": 0.5, "capturePiece()": 0.5}
""" 

#plant_uml_inst = "@startuml \nclass square { \nfile \nrank \n} \nclass move \nclass position { \n/check \n/checkmate \n/stalemate \nexecuteMove() \ncapturePiece() \n} \nclass piece \nenum color { \nBLACK \nWHITE \n} \nenum type as \"type of piece\" { \nPAWN \nKNIGHT \nBISHOP \nROOK \nQUEEN \nKING \n} \n} \nsquare \"*\" -- \"*\" square : \"from / to\" \n(square, square) .. move \nposition \"*\" -- \"*\" piece \n(position, piece) .. square \nposition \" \" -- \"1\" color:  \"whoseTurn\" \nposition \" \" -- \"0..*\" move: \"legalMoves\" \nmove \" \" o-- \"0..1\" type: \"transformed\" \npiece \" \" o-- \"1\" color: \"color\" \npiece \" \" o-- \"1\" type: \"type\" \n@enduml"
#instructor_model = UMLModel(plant_uml_inst)
"""
for c in instructor_model.class_list:
    print(f"{c.name}: {c.attributes}, {c.operations}, {str(c.relations)}")
for e in instructor_model.enum_list:
    print(f"{e.name}: {e.values}")
for r in instructor_model.relation_list:
    print(f"{r}")
print("\n")
"""

#plant_uml_stud = "@startuml\nskinparam Linetype ortho\nhide empty attributes\nhide empty methods\n\nclass ChessPiece {\n    pieceColor\n    pieceType\n}\n\nclass Square {\n    file\n    rank\n    piece\n}\n\nclass Move {\n    fromSquare\n    toSquare\n    piece\n}\n\nclass Position {\n    pieces\n    turn\n    /check\n    /stalemate\n    /checkmate\n    executeMove(move)\n    capturePiece(piece)\n}\n\nclass ChessGame {\n    currentPosition\n    moves\n}\n\nenum PieceColor {\n    black\n    white\n}\n\nenum PieceType {\n    king\n    queen\n    rook\n    bishop\n    knight\n    pawn\n}\n\nChessPiece \"1\" -- \"1\" PieceColor: pieceColor\nChessPiece \"1\" -- \"1\" PieceType: pieceType\nSquare \"64\" -- \"0..1\" ChessPiece: piece\nMove \"1\" -- \"1\" Square: fromSquare\nMove \"1\" -- \"1\" Square: toSquare\nMove \"1\" -- \"1\" ChessPiece: piece\nPosition \"1\" -- \"64\" Square: squares\nPosition \"1\" -- \"1\" PieceColor: turn\nChessGame \"1\" -- \"1\" Position: currentPosition\nChessGame \"1\" -- \"*\" Move: moves\n\n@enduml"
#student_model = UMLModel(plant_uml_stud)
"""
for c in student_model.class_list:
    print(f"{c.name}: {c.attributes}, {c.operations}, {str(c.relations)}")
for e in student_model.enum_list:
    print(f"{e.name}: {e.values}")
for r in student_model.relation_list:
    print(f"{r}")
print("\n")

print(f"square rel ends: {instructor_model.class_list[0].get_relation_ends()}")
"""
#matches, missing = ClassComperator.compare_classes(instructor_model.class_list, student_model.class_list)
#print("Matches:", matches)
#print("Missing:", missing)

