import Levenshtein

class SyntacticCheck:
    
    @staticmethod
    def levenshtein_score(w1, w2):
        max_len = max(len(w1), len(w2))
        distance = Levenshtein.distance(w1, w2)
        similarity = 1 - (distance / max_len)
        return similarity
    
    @staticmethod
    def string_in_string(w1, w2):
        if w1 in w2:
            return True
        words1 = w1.split()
        if (w in w2 for w in words1):
            return True
    
    @staticmethod
    def syntactic_match(word1: str, word2: str, threshold: float = 0.6) -> bool:
        similarity = SyntacticCheck.levenshtein_score(word1, word2)
        return similarity >= threshold