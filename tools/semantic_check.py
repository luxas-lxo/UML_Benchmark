from itertools import product
from typing import Tuple
from sentence_transformers import SentenceTransformer
import spacy
from nltk.corpus import wordnet as wn
from nltk.corpus import wordnet_ic
import re

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
nlp = spacy.load('en_core_web_lg')
brown_ic = wordnet_ic.ic('ic-brown.dat')

class SemanticCheck:
    @staticmethod
    def normalize_identifier(identifier: str) -> str:
        # Insert space before any uppercase letter that follows a lowercase letter or a number
        s = re.sub(r'(?<=[a-z0-9])([A-Z])', r' \1', identifier)
        # Insert space before sequences of uppercase letters followed by lowercase letters (acronyms like XMLParser)
        s = re.sub(r'(?<=[A-Z])([A-Z][a-z])', r' \1', s)
        # Replace underscores with spaces
        s = s.replace("_", " ")
        s = s.lower()
        return s

    @staticmethod
    def wup_score(w1: str, w2: str):
        words1 = w1.split()
        words2 = w2.split()
        max_score = 0
        for word1, word2 in product(words1, words2):
            synsets1 = wn.synsets(word1)
            synsets2 = wn.synsets(word2)
            if synsets1 and synsets2:
                score = max((s1.wup_similarity(s2) or 0) for s1 in synsets1 for s2 in synsets2)
                max_score = max(max_score, score)
        return max_score

    @staticmethod
    def lin_score(w1: str, w2: str):
        words1 = w1.split()
        words2 = w2.split()
        max_score = 0
        positions = [wn.NOUN, wn.VERB]
        for word1, word2 in product(words1, words2):
            for pos in positions:
                syns1 = wn.synsets(word1, pos = pos)
                syns2 = wn.synsets(word2, pos = pos)
                if syns1 and syns2:
                    try:
                        score = max((s1.lin_similarity(s2, brown_ic) or 0) for s1 in syns1 for s2 in syns2)
                        max_score = max(max_score, score)
                    except:
                        continue  
        return max_score

    @staticmethod
    def transformer_score(w1: str, w2: str):
        wordlist = [w1, w2]
        embeddings = model.encode(wordlist)
        similarity = model.similarity(embeddings[0], embeddings[1]).item()
        return similarity

    @staticmethod
    def word2vec_score(w1, w2):
        wordlist = [w1, w2]
        embeddings = [nlp(w) for w in wordlist]
        similarity = embeddings[0].similarity(embeddings[1])
        return similarity

    @staticmethod
    def semantic_match(word1: str, word2: str, threshold: float = 0.7) -> Tuple[bool, float]:
        word1 = SemanticCheck.normalize_identifier(word1)
        word2 = SemanticCheck.normalize_identifier(word2)
        wup = SemanticCheck.wup_score(word1, word2)
        lin = SemanticCheck.lin_score(word1, word2)
        w2v = SemanticCheck.word2vec_score(word1, word2)
        tra = SemanticCheck.transformer_score(word1, word2)
        score = (0.1 * wup + 0.2 * lin + 0.3 * w2v + 0.4 * tra)
        return (score >= threshold, score)
