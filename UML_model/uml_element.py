from abc import ABC, abstractmethod

class UMLElement(ABC):
    def __init__(self, name: str):
        self.name: str = name  

    def __str__(self):
        return f"{self.__class__.__name__}({getattr(self, 'name', '-')})"

    @abstractmethod
    def to_plantuml(self) -> str:
        raise NotImplementedError("Subclasses must implement to_plantuml()")

    
    

