import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from UML_model.uml_model import UMLModel
#from plantuml_eval.eval_classes import ClassComperator
from grading.grade_metamodel_new import GradeModel, StructuralFeature

plantuml_text1 = """
@startuml
class Alter
class Brunnen
class Clown

Alter -- Brunnen
Alter -- Clown
@enduml
"""

plantuml_text2 = """
@startuml
class Alter
class Blunnen
class Z

Alter -- Blunnen
Alter -- Z
@enduml

"""

#uml_model1 = UMLModel(plantuml_str=plantuml_text1)
#uml_model2 = UMLModel(plantuml_str=plantuml_text2)


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

plant_uml_inst = "@startuml \nclass square { \nfile \nrank \n} \nclass move \nclass position { \n/check \n/checkmate \n/stalemate \nexecuteMove() \ncapturePiece() \n} \nclass piece \nenum color { \nBLACK \nWHITE \n} \nenum type as \"type of piece\" { \nPAWN \nKNIGHT \nBISHOP \nROOK \nQUEEN \nKING \n} \n} \nsquare \"*\" -- \"*\" square : \"from / to\" \n(square, square) .. move \nposition \"*\" -- \"*\" piece \n(position, piece) .. square \nposition \" \" -- \"1\" color:  \"whoseTurn\" \nposition \" \" -- \"0..*\" move: \"legalMoves\" \nmove \" \" o-- \"0..1\" type: \"transformed\" \npiece \" \" o-- \"1\" color: \"color\" \npiece \" \" o-- \"1\" type: \"type\" \n@enduml"
instructor_model = UMLModel(plant_uml_inst)
grade_model_ss2015 = GradeModel(instructor_model)
grade_model_ss2015.add_class_grade_structure("square", 1.0, 0.5)
grade_model_ss2015.add_class_grade_structure("move", 1.0)
grade_model_ss2015.add_class_grade_structure("position", 1.0, 1.0, 0.5)
grade_model_ss2015.add_class_grade_structure("piece", 1.0)
for obj in grade_model_ss2015.classes:
    print(f"Object({obj.element}, {obj.points}, {obj.st_features})")
    print("\n")

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

"""
Klassen:
    Stellung 5 Punkte
        - existiert 1 Punkt
        - Attribute 3 Punkte
            - /schach 1 Punkt
            - /matt 1 Punkte
            - /patt 1 Punkt
        - Operationen 1 Punkt
            - führeZugAus() 0.5 Punkte
            - schlageFigur() 0.5 Punkte

    Feld 2 Punkt
        - existiert 1 Punkt
        - Attribute 1 Punkt
            - linie 0.5 Punkte
            - reihe 0.5 Punkte

    Zug 1 Punkt
        - existiert 1 Punkt

    Figur 1 Punkt
        - existiert 1 Punkt

Enumerationen:
    Farbe 1 Punkt
        - existiert 0.5 Punkte
        - alle Werte vorhanden 0.5 Punkte
            - WEISS, SCHWARZ 0.5 Punkte
        
    Figurenart 1 Punkt
        - existiert 0.5 Punkte
        - alle Werte vorhanden 0.5 Punkte
            - BAUER, LÄUFER, SPRINGER, TURM, DAME, KÖNIG 0.5 Punkte

Beziehungen:
    Stellung -- Farbe 1 Punkt
        - existiert 0.5 Punkte
        - alles richtig 0.5 Punkte
            - Rolle: amZug 
            - Multiziplitäten: _ , 1
            - Type: Assoziation
    
    Stellung -- Figur 1 Punkt
        - existiert 0.5 Punkte
        - alles richtig 0.5 Punkte
            - Rolle: _ 
            - Multiziplitäten: * , *
            - Type: Assoziation

    Stellung -- Zug 1 Punkt
        - existiert 0.5 Punkte
        - alles richtig 0.5 Punkte
            - Rolle: gültigeZüge 
            - Multiziplitäten: _ , 0..*
            - Type: Assoziation
    
    Feld -- Feld 1 Punkt
        - existiert 0.5 Punkte
        - alles richtig 0.5 Punkte
            - Rolle: von/nach 
            - Multiziplitäten: * , *
            - Type: Assoziation

    Feld -- (Stellung, Figur) 3 Punkte
        - existiert 3 Punkte
    
    Zug -- (Feld, Feld) 3 punkte
        - existiert 3 Punkte
    
    Zug -- Figurenart 1 Punkt
        - existiert 0.5 Punkte
        - alles richtig 0.5 Punkte
            - Rolle: umgewandelt 
            - Multiziplitäten: _ , 0..1
            - Type: Aggregation 

    Figur -- Farbe 1 Punkt
        - existiert 0.5 Punkte
        - alles richtig 0.5 Punkte
            - Rolle: farbe 
            - Multiziplitäten: _ , 1
            - Type: Aggregation 

    Figur -- Figurenart 1 Punkt
        - existiert 0.5 Punkte
        - alles richtig 0.5 Punkte
            - Rolle: figurenart 
            - Multiziplitäten: _ , 1
            - Type: Aggregation 
"""