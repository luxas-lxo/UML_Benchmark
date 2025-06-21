import Levenshtein
from typing import Tuple

class SyntacticCheck:
    
    @staticmethod
    def levenshtein_score(w1: str, w2: str):
        max_len = max(len(w1), len(w2))
        distance = Levenshtein.distance(w1, w2)
        similarity = 1 - (distance / max_len)
        return similarity
    
    @staticmethod
    def syntactic_match(word1: str, word2: str, threshold: float = 0.6) -> Tuple[bool, float]:
        similarity = SyntacticCheck.levenshtein_score(word1, word2)
        return (similarity >= threshold, similarity)