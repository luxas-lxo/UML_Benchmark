from UML_model.uml_class import UMLClass

class ContentCheck:

    @staticmethod
    def content_match(class1: UMLClass, class2: UMLClass, threshold: float = 0.6) -> bool:
        total = len(class1.attributes) + len(class1.operations)
        if total == 0:
            return False
        match_count = sum(1 for a in class1.attributes if a in class2.attributes)
        match_count += sum(1 for op in class1.operations if op in class2.operations)
        similarity = match_count / total
        return similarity >= threshold