from typing import Dict

class Grade:
    def __init__(self, element_name: str, element_type: str, points: float = 0.0):
        self.element_name = element_name  
        self.element_type = element_type
        self.points = points
        self.subgrades: Dict[str, float] = {}  

    def add_subgrade(self, name: str, points: float):
        self.subgrades[name] = points

    def total(self) -> float:
        return self.points + sum(self.subgrades.values())

    def __repr__(self):
        return f"<Grade {self.element_type} '{self.element_name}': {self.total()} points>"

class GradeModel:
    def __init__(self):
        self.class_grades: Dict[str, Grade] = {}  
        self.attribute_grades: Dict[str, Dict[str, float]] = {} 
        self.operation_grades: Dict[str, Dict[str, float]] = {}  

    def add_class_grade(self, class_name: str, points: float):
        self.class_grades[class_name] = Grade(class_name, "class", points)

    def add_attribute_grade(self, class_name: str, attribute_name: str, points: float):
        if class_name not in self.attribute_grades:
            self.attribute_grades[class_name] = {}
        self.attribute_grades[class_name][attribute_name] = points

    def add_operation_grade(self, class_name: str, operation_name: str, points: float):
        if class_name not in self.operation_grades:
            self.operation_grades[class_name] = {}
        self.operation_grades[class_name][operation_name] = points

    def get_total_grade(self) -> float:
        total = sum(g.total() for g in self.class_grades.values())
        total += sum(sum(attrs.values()) for attrs in self.attribute_grades.values())
        total += sum(sum(ops.values()) for ops in self.operation_grades.values())
        return total

    def __repr__(self):
        return (f"<GradeModel: total={self.get_total_grade()}>\n"
                f"Classes: {self.class_grades}\n"
                f"Attributes: {self.attribute_grades}\n"
                f"Operations: {self.operation_grades}")
