import Levenshtein
from typing import Tuple
import logging
import re

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
        word1 = word1.strip().lower()
        word2 = word2.strip().lower()
        similarity = SyntacticCheck.levenshtein_score(word1, word2)
        if similarity >= threshold:
            logger.debug(f"Syntactic match: '{word1}' and '{word2}': score = {similarity:.2f}")
        return (similarity >= threshold, similarity)
    
    @staticmethod
    def is_upper_camel_case(word: str) -> bool:
        # UpperCamelCase: Starts with uppercase, no underscores, each word starts with uppercase
        return bool(re.fullmatch(r'(?:[A-Z][a-z0-9]*)+', word))

    @staticmethod
    def is_lower_camel_case(word: str) -> bool:
        # lowerCamelCase: Starts with lowercase, no underscores, each new word starts with uppercase
        return bool(re.fullmatch(r'[a-z]+(?:[A-Z][a-z0-9]*)*', word))
    
    @staticmethod
    def is_all_upper_case(word: str) -> bool:
        # ALL_UPPER_CASE: All uppercase letters, can include underscores
        return bool(re.fullmatch(r'[A-Z_]+', word))
    
    @staticmethod
    def is_all_lower_case(word: str) -> bool:
        # all_lower_case: All lowercase letters, can include underscores
        return bool(re.fullmatch(r'[a-z_]+', word))
    
    @staticmethod
    def is_valid_multiplicity(multiplicity: str) -> bool:
        # Valid multiplicities: 0..1, 1, 0..*, *, 1..*, 1..n, n..m, etc.
        # Allow optional [] or () around the term
        valid_pattern = re.compile(
            r'^\s*[\[\(]?\s*(?:\d+|\*|\d+\.\.\d+|\d+\.\.\*)\s*[\]\)]?\s*$'
        )
        pattern_match = bool(valid_pattern.match(multiplicity.strip()))
        if pattern_match:
            start, end = SyntacticCheck.get_numbers_or_stars_from_multiplicity(multiplicity)
            if start > end:
                logger.debug(f"Invalid multiplicity: start ({start}) is greater than end ({end}) in '{multiplicity}'")
                return False
            if any(x < 0 for x in (start, end)):
                logger.debug(f"Invalid multiplicity: negative value in '{multiplicity}' (start={start}, end={end})")
                return False
        return True
    
    @staticmethod
    def is_multiplicity_match_replace_high_numbers(mult_i: str, mult_s: str) -> bool:
        mult_s = SyntacticCheck.replace_high_numbers_in_multiplicity(mult_s)
        # Normalize common multiplicity patterns
        if mult_s in ["*..*", "0..*"]:
            mult_s = "*"
        return mult_i == mult_s
    
    @staticmethod
    def replace_high_numbers_in_multiplicity(multiplicity: str) -> str:
        # Replace any number > 20 with '*'
        return re.sub(r'\d+', SyntacticCheck._replace_if_high_number, multiplicity)

    @staticmethod
    def _replace_if_high_number(match: re.Match) -> str:
        num = int(match.group())
        return '*' if num > 20 else str(num)

    @staticmethod
    def get_numbers_or_stars_from_multiplicity(multiplicity: str) -> Tuple[float, float]:
        # Extracts the number or '*' from a multiplicity string 
        match_1 = re.match(r"^(?P<start>\d+|\*)\.\.(?P<end>\d+|\*)$", multiplicity.strip())
        match_2 = re.match(r"^(?P<start>\d+|\*)$", multiplicity.strip())
        if match_1:
            start = float('inf') if match_1.group("start") == '*' else float(match_1.group("start"))
            end = float('inf') if match_1.group("end") == '*' else float(match_1.group("end"))
            return start, end
        elif match_2:
            end = float('inf') if match_2.group("start") == '*' else float(match_2.group("start"))
            start = 0 if end == float('inf') else end
            return start, end
        else:
            logger.warning(f"Invalid multiplicity format: {multiplicity}")
            return float('NaN'), float('NaN')
        
        

