import Levenshtein
from typing import Tuple
import logging

logger = logging.getLogger("syntactic_check")
logger.setLevel(logging.DEBUG)

if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(levelname)s] - %(name)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

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
        if similarity >= threshold:
            logger.debug(f"Syntactic match: '{word1}' and '{word2}': score = {similarity:.2f}")
        return (similarity >= threshold, similarity)