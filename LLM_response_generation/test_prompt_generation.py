import json

uml_usage = """
Use the following UML modeling rules in PlantUML:
- Naming:
    Classes: UpperCamelCase
    Attributes/operations/labels: lowerCamelCase
    Multiplicities: 1, 0..1, *, 1..*, 0..number
- Use this setup for every diagram you design:
    @startuml
    skinparam Linetype ortho
    hide empty attributes
    hide empty methods
    ' your diagram code here
    @enduml
- Classes:
    class Class {
        attribute1
        attribute12
        /derivedAttribute1
        /derivedAttribute2
        operation1()
        operation2()
    }
- Association Classes between Class1 and Class2:
    class AssociationClass {
        attribute1
        attribute2
        operation1()
        operation2()
    }
    Class1 "multiplicity1" -- "multiplicity2" Class2: undirectedLabel
    (Class1, Class2) .. AssociationClass
- Enumerations:
    enum Enumeration {
        VALUE1
        VALUE2
    }
- Association between Class3 and Class4:
    Class3 "multiplicity1" -- "multiplicity2" Class4: undirectedLabel
- Aggregation between Class5 and Class6
    Class5 "multiplicity1" --o "multiplicity2" Class6: undirectedLabel
"""
sys_prompt = "You are an expert in UML design via PlantUML. You will receive a domain description and a specific question. Base your answers strictly on the description. Do not infer or invent anything not explicitly stated. Always respond strictly in the format indicated by the question, with no explanations or additional text. Follow the rules below:\n" + uml_usage
desc = """
Chess Program DokChess 
Chess is played between two opponents who take turns moving their pieces on a square game board, known as a chessboard.
A chess piece is characterized by its color (black or white) and its type (king, queen, rook, bishop, knight, pawn). There are a total of 32 pieces.
A square can be occupied by at most one piece. A square is identified by its coordinates (on the chessboard), i.e., by specifying its file and rank.
A move indicates from which square a piece is moved to which other square. In an exceptional case, a piece may be transformed into another piece.
The current game situation is described by the positions of the pieces (i.e., by their assignment to individual squares). To complete the game situation, the information about whose turn it is (black or white) is required.
In a position, a move can be executed (executeMove). A piece can also be removed from a square if it is captured (capturePiece).
From a position, valid moves can be derived, as well as whether a
•	Check (the king of the given color is in check)
•	Stalemate (the current player has no valid move but is not in check)
•	Checkmate (the current player is in check and has no move to escape the attack)
is present.
"""

questions = [
    "Which classes can be extracted from the description? Only include classes explicitly mentioned in the description. Do not include abstract systems unless stated. Answer in the following scheme and with no additional text: \"**classes**: {ClassName1, ClassName2, ...}\".",
    "Given there is a class \"position\", is this class an \"association class\"? Answer in the following scheme and with no additional text: \"**answer**: yes or no\".",

    "Given there is a class \"position\", which attributes can be assigned to that class? Focus only on the attribute itself. The datatype of the attribute is irrelevant. Answer in the following scheme and with no additional text: \"**attributes**: {attribute1, attribute2, ...}\".",
    "Given there is a class \"position\" with the attributes \"check, checkmate, stalemate\", decide which of these are derived attributes. Derived attributes are those that can be calculated from other data in the class. Answer in the following scheme and with no additional text: \"**attributes**: {check: yes||no, checkmate: yes||no, stalemate: yes||no}\".",

    "Given there is a class \"position\", which operations can be assigned to that class? No parameter or return types are required. Parentheses are required. Answer in the following scheme and with no additional text: \"**operations**: {your-answer}\".", 

    "Given there is a class \"position\", which relations can be assigned to that class? You should asign multiplicities, type of relation, label and class in relation if explicitly mentioned in the description. Answer in the following scheme and with no additional text: \"**relations**: {{position (multiplicity-1) <type-of-relation> (multiplicity-2) <class-or-enum-in-relation>: <description>}, {...}}\".",
    "Given there is a class \"position\" with relations to the classes \"piece\" and \"move\", and a relation to the enumeration \"color\", which of these relations are only associations (no specific association type like association or composition)? Answer in the following scheme and with no additional text: \"**associations**: {position -- <target1>, position -- <target2>, ...}\".",
    "Given there is a class \"position\" with relations to the classes \"piece\" and \"move\", and a relation to the enumeration \"color\", which of these relations are aggregations? Pay attention to the direction of the aggregation. Answer in the following scheme and with no additional text: \"**aggregations**: {position o-- <target1>, position --o <target2>, ...}\".",
    "Given there is a class \"position\" with associations to the classes \"piece\" and \"move\", and an association to the enumeration \"color\", what multiplicities would you assign to each of the associations? Not every end of the association necessarily requires a multiplicity. Use only multiplicities mentioned or clearly implied. Answer in the following scheme and with no additional text: \"**multiplicities**: {{position (optional-multiplicity1) -- (optional-multiplicity2) piece}, {position (optional-multiplicity3) -- (optional-multiplicity4) move}, {position (optional-multiplicity5) -- (optional-multiplicity6) color}}\".",
    "Given there is a class \"position\" with associations to the classes \"piece\" and \"move\", and an association to the enumeration \"color\", what labels would you assign to each of the associations? Not every association needs a label. Answer in the following scheme and with no additional text: \"**labels**: {{position (optional-label1) -- (optional-label2) piece}, {position (optional-label3) -- (optional-label4) move}, {position (optional-label5) -- (optional-label6) color}}\".",

    "Given there is a class \"position\", model the class in PlantUML. Follow the PlantUML usage rules provided in the system prompt. Answer only with the code in the following format: @startuml <your-code> @enduml",
    "Model the entire description in PlantUML, including all relevant classes and relations. Follow the PlantUML usage rules provided in the system prompt. Answer only with the code in the following format: @startuml <your-code> @enduml"

]

examples = [
    "{no example}",
    "Given there is a class \"square\", is this class an association class? Answer: \"**answer**: {yes}\".",

    "Given there is a class \"square\", which attributes can be assigned to that class? Answer: \"**attributes**: {file, rank}\".",
    "Given there is a class \"square\" with the attributes \"file, rank\", decide which of these are derived attributes. Answer: \"**attributes**: {file: no, rank: no}\".",
    
    "Given there is a class \"square\", which operations can be assigned to that class? Answer: \"**operations**: {}\".",

    "Given there is a class \"square\", which relations can be assigned to that class? You should asign multiplicities, type of relation, description and class in relation if possible. Answer: \"**relations**: {{square \"*\" -- \"*\" square : \"from / to \"}, {(position, piece) .. square}}\".",
    "Given there is a class \"square\" with relations to itself and a relation to the association from  \"position to piece\", which of these relations are associations? Answer: \"**associations**: {square -- square, square -- (position, piece)}\".",
    "Given there is a class \"square\" with relations to itself and a relation to the association from  \"position to piece\", which of these relations are aggregations?: \"**aggregations**: {}\".",
    "Given there is a class \"square\" with associations to itself and a link to the association from  \"position to piece\", what multiplicities would you assign to each of the relations? Answer: \"**multiplicities**: {{square \"*\" -- \"*\" square}, {square .. (position, piece)}}\".",
    "Given there is a class \"square\" with associations to itself and a link to the association from  \"position to piece\", what labels would you assign to each of the relations? Answer: \"**labels**: {{square \"from\" -- \"to\" square}, {square -- (position, piece)}}\".",

    "Given there is a class \"square\", model the class in PlantUML. Answer: @startuml class square {file \nrank} \nsquare \"*\" -- \"*\" square : \"from / to \" \nposition -- piece \n(position, piece) .. square \n@enduml",
    "{no example}"
]

solutions = [
    "**classes**: {square, move, position, piece}",
    "**answer**: {no}",

    "**attributes**: {check, checkmate, stalemate}",
    "**attributes**: {check: yes, checkmate: yes, stalemate: yes}",

    "**operations**: {executeMove(), capturePiece()}",

    "**relations**: {{position (*) association (*) piece}, {position () association (1) color: whoseTurn}, {position () association (0..1) move: legalMoves}}",
    "**associations**: {position -- piece, position -- color, position -- move}",
    "**aggregations**: {}",
    "**multiplicities**: {{position (*) -- (*) piece}, {position () -- (0..1) move}, {position () -- (1) color}}",
    "**labels**: {{position () -- () piece}, {position () -- (legalMoves) move}, {position () -- (whoseTurn) color}}",

    "@startuml \nclass square { \nfile \nrank \n} \nsquare \"*\" -- \"*\" square: \"from / to\" \nposition -- piece \n(position, piece) .. square \n@enduml",
    "@startuml \nclass square { \nfile \nrank \n} \nclass move \nclass position { \n\\check \n\\checkmate \n\\stalemate \nexecuteMove() \ncapturePiece() \n} \nclass piece \nenum color { \nBLACK \nWHITE \n} \nenum type as \"type of piece\" { \nPAWN \nKNIGHT \nBISHOP \nROOK \nQUEEN \nKING \n} \n} \nsquare \"*\" -- \"*\" square : \"from / to\" \n(square, square) .. move \nposition \"*\" -- \"*\" piece \n(position, piece) .. square \nposition \" \" -- \"1\" color:  \"whoseTurn\" \nposition \" \" -- \"0..*\" move: \"legalMoves\" \nmove \" \" o-- \"0..1\" type: \"transformed\" \npiece \" \" o-- \"1\" color: \"color\" \npiece \" \" o-- \"1\" type: \"type\" \n@enduml"

]
with open("uml_prompts.jsonl", "w", encoding="utf-8") as f:
    for question, example, solution in zip(questions, examples, solutions):
        entry = {
            "system_prompt": sys_prompt,
            "description": desc.strip(),
            "question": question,
            "example": example,
            "solution": solution
        }
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


