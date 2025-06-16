import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from UML_model.uml_model import UMLModel
from plantuml_eval.eval_classes import compare_classes

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

uml_model1 = UMLModel(plantuml_str=plantuml_text1)
uml_model2 = UMLModel(plantuml_str=plantuml_text2)
a, b = compare_classes(uml_model1.class_list, uml_model2.class_list)
print(a)
print(b)

