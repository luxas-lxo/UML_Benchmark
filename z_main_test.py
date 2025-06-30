from UML_model.uml_model import UMLModel
from grading.grade_metamodel import GradeModel
from plantuml_eval.eval_model import EvalModel

plant_uml_inst = "@startuml \nclass square { \nfile \nrank \n} \nclass move \nclass position { \n/check \n/checkmate \n/stalemate \nexecuteMove() \ncapturePiece() \n} \nclass piece \nenum color { \nBLACK \nWHITE \n} \nenum type as \"type of piece\" { \nPAWN \nKNIGHT \nBISHOP \nROOK \nQUEEN \nKING \n} \n} \nsquare \"*\" -- \"*\" square : \"from / to\" \n(square, square) .. move \nposition \"*\" -- \"*\" piece \n(position, piece) .. square \nposition \" \" -- \"1\" color:  \"whoseTurn\" \nposition \" \" -- \"0..*\" move: \"legalMoves\" \nmove \" \" o-- \"0..1\" type: \"transformed\" \npiece \" \" o-- \"1\" color: \"color\" \npiece \" \" o-- \"1\" type: \"type\" \n@enduml"
instructor_model = UMLModel(plant_uml_inst)

plant_uml_stud = "@startuml\nskinparam Linetype ortho\nhide empty attributes\nhide empty methods\n\nclass ChessPiece {\n    pieceColor\n    pieceType\n}\n\nclass Square {\n    +file: int = 0\n    rank\n    piece\n}\n\nclass Move {\n    fromSquare\n    toSquare\n    piece\n}\n\nclass Position {\n    pieces\n    turn\n    /check\n    /stalemate\n    /checkmate\n    executeMove(move)\n    capturePiece(piece)\n}\n\nclass ChessGame {\n    currentPosition\n    moves\n}\n\nenum PieceColor {\n    black\n    white\n}\n\nenum PieceType {\n    king\n    queen\n    rook\n    bishop\n    knight\n    pawn\n}\n\nChessPiece \"1\" -- \"1\" PieceColor: pieceColor\nChessPiece \"1\" -- \"1\" PieceType: pieceType\nSquare \"64\" -- \"0..1\" ChessPiece: piece\nMove \"1\" -- \"1\" Square: fromSquare\nMove \"1\" -- \"1\" Square: toSquare\nMove \"1\" -- \"1\" ChessPiece: piece\nPosition \"1\" -- \"64\" Square: squares\nPosition \"1\" -- \"1\" PieceColor: turn\nChessGame \"1\" -- \"1\" Position: currentPosition\nChessGame \"1\" -- \"*\" Move: moves\n\n@enduml"
student_model = UMLModel(plant_uml_stud)

grade_model_ss2015 = GradeModel("SS2015", instructor_model)
grade_model_ss2015.add_class_grade_structure(instructor_model.class_lookup["square"], 1.0, 0.5)
grade_model_ss2015.add_class_grade_structure(instructor_model.class_lookup["move"], 1.0)
grade_model_ss2015.add_class_grade_structure(instructor_model.class_lookup["position"], 1.0, 1.0, 0.5)
grade_model_ss2015.add_class_grade_structure(instructor_model.class_lookup["piece"], 1.0)
grade_model_ss2015.add_enum_grade_structure(instructor_model.enum_lookup["color"], 0.5, 0.5)
grade_model_ss2015.add_enum_grade_structure(instructor_model.enum_lookup["type"], 0.5, 0.5)
grade_model_ss2015.add_relation_grade_structure(instructor_model.relation_lookup["(square, square)"], 0.5, 0.5)
grade_model_ss2015.add_relation_grade_structure(instructor_model.relation_lookup["(position, piece)"], 0.5, 0.5)
grade_model_ss2015.add_relation_grade_structure(instructor_model.relation_lookup["(position, color)"], 0.5, 0.5)
grade_model_ss2015.add_relation_grade_structure(instructor_model.relation_lookup["(position, move)"], 0.5, 0.5)
grade_model_ss2015.add_relation_grade_structure(instructor_model.relation_lookup["(type, move)"], 0.5, 0.5)
grade_model_ss2015.add_relation_grade_structure(instructor_model.relation_lookup["(color, piece)"], 0.5, 0.5)
grade_model_ss2015.add_relation_grade_structure(instructor_model.relation_lookup["(type, piece)"], 0.5, 0.5)
grade_model_ss2015.add_relation_grade_structure(instructor_model.relation_lookup["(move, (square, square))"], 1.0, 1.0)
grade_model_ss2015.add_relation_grade_structure(instructor_model.relation_lookup["(square, (position, piece))"], 1.0, 1.0)

eval_model = EvalModel(instructor_model, student_model, grade_model_ss2015)
#print(repr(eval_model))
eval_model.print_compare_classes()
eval_model.print_compare_enums()
eval_model.print_compare_relations()
