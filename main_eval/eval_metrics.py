class ScoringCriteria:
    def __init__(self, category: str, id: str, description: str, weight: float = 0, score: float = 0.0):
        self.category: str = category
        self.id: str = id
        self.description: str = description
        self.weight: float = weight
        self.score: float = score

    def __repr__(self):
        return f"ScoringCriteria(category={self.category}, id={self.id}, description={self.description}, weight={self.weight}, score={self.score})"
    
    def __str__(self):
        return f"ScoringCriteria({self.id})"
    
# TODO: Add weight to ScoringCriteria
class ScoringScheme:
    def __init__(self):
        COMPLETENESS = "Completeness"
        SYNTAX = "Syntactic Correctness"
        SEMANTICS = "Semantic Correctness"

        cpt1 = ScoringCriteria(COMPLETENESS, "CPT1", "All necessary classes are included")
        cpt2 = ScoringCriteria(COMPLETENESS, "CPT2", "Classes include all necessary attributes")
        cpt3 = ScoringCriteria(COMPLETENESS, "CPT3", "Classes include all necessary operations")
        cpt4 = ScoringCriteria(COMPLETENESS, "CPT4", "All necessary relations are included")
        cpt5 = ScoringCriteria(COMPLETENESS, "CPT5", "Multiplicities are included in relations")
        cpt6 = ScoringCriteria(COMPLETENESS, "CPT6", "Relations names are included")
        cpt7 = ScoringCriteria(COMPLETENESS, "CPT7", "Role names are included")
        cpt8 = ScoringCriteria(COMPLETENESS, "CPT8", "All necessary enumerations are included")
        cpt9 = ScoringCriteria(COMPLETENESS, "CPT9", "Enumerations include all necessary values")

        self.completeness_criteria = [cpt1, cpt2, cpt3, cpt4, cpt5, cpt6, cpt7, cpt8, cpt9]

        syc1 = ScoringCriteria(SYNTAX, "SYC1", "Classes are correctly represented")
        syc1g = ScoringCriteria(SYNTAX, "SYC1.global", "Classes are formally correct")
        syc2 = ScoringCriteria(SYNTAX, "SYC2", "Class attributes are correctly represented")
        syc2g = ScoringCriteria(SYNTAX, "SYC2.global", "Class attributes are formally correct")
        syc3 = ScoringCriteria(SYNTAX, "SYC3", "Class operations are correctly represented")
        syc3g = ScoringCriteria(SYNTAX, "SYC3.global", "Class operations are formally correct")
        syc4 = ScoringCriteria(SYNTAX, "SYC4", "Simple associations are correctly represented")
        syc4g = ScoringCriteria(SYNTAX, "SYC4.global", "Simple associations are formally correct")
        syc5 = ScoringCriteria(SYNTAX, "SYC5", "Aggregation relations are correctly represented")
        syc5g = ScoringCriteria(SYNTAX, "SYC5.global", "Aggregation relations are formally correct")
        syc6 = ScoringCriteria(SYNTAX, "SYC6", "Composition relations are correctly represented")
        syc6g = ScoringCriteria(SYNTAX, "SYC6.global", "Composition relations are formally correct")
        syc7 = ScoringCriteria(SYNTAX, "SYC7", "Generalization relations are correctly represented")
        syc7g = ScoringCriteria(SYNTAX, "SYC7.global", "Generalization relations are formally correct")
        syc8 = ScoringCriteria(SYNTAX, "SYC8", "Relation multiplicities are correctly represented")
        syc8g = ScoringCriteria(SYNTAX, "SYC8.global", "Relation multiplicities are formally correct")
        syc9 = ScoringCriteria(SYNTAX, "SYC9", "Roles are correctly represented")
        syc9g = ScoringCriteria(SYNTAX, "SYC9.global", "Roles are formally correct")
        syc10 = ScoringCriteria(SYNTAX, "SYC10", "Aggregation class relations are correctly represented")
        syc10g = ScoringCriteria(SYNTAX, "SYC10.global", "Aggregation class relations are formally correct")
        syc11 = ScoringCriteria(SYNTAX, "SYC11", "Enumerations are correctly represented")
        syc11g = ScoringCriteria(SYNTAX, "SYC11.global", "Enumeration values are formally correct")
        syc12 = ScoringCriteria(SYNTAX, "SYC12", "Enumeration values are correctly represented")
        syc12g = ScoringCriteria(SYNTAX, "SYC12.global", "Enumeration values are formally correct")
        syc20g = ScoringCriteria(SYNTAX, "SYC20.global", "All classes are in UpperCamelCase")
        syc21g = ScoringCriteria(SYNTAX, "SYC21.global", "All attributes are in lowerCamelCase")
        syc22g = ScoringCriteria(SYNTAX, "SYC22.global", "All operations are in lowerCamelCase")
        syc23g = ScoringCriteria(SYNTAX, "SYC23.global", "All enumeration names are in UpperCamelCase")
        syc24g = ScoringCriteria(SYNTAX, "SYC24.global", "All enumeration values are in ALL_UPPER_CASE")
        syc25g = ScoringCriteria(SYNTAX, "SYC25.global", "All relations are formally correct")

        self.syntax_criteria = [syc1, syc2, syc3, syc4, syc5, syc6, syc7, syc8, syc9, syc10, syc11, syc12, syc1g, syc2g, syc3g, syc4g, syc5g, syc6g, syc7g, syc8g, syc9g, syc10g, syc11g, syc12g, syc20g, syc21g, syc22g, syc23g, syc24g, syc25g]

        sec1 = ScoringCriteria(SEMANTICS, "SEC1", "Class names are appropriate")
        sec2 = ScoringCriteria(SEMANTICS, "SEC2", "Attribute names are appropriate")
        sec3 = ScoringCriteria(SEMANTICS, "SEC3", "Operation names are appropriate")
        sec4 = ScoringCriteria(SEMANTICS, "SEC4", "Relation names are appropriate")
        sec5 = ScoringCriteria(SEMANTICS, "SEC5", "Multiplicities are correct")
        sec6 = ScoringCriteria(SEMANTICS, "SEC6", "Role names are appropriate")
        sec7 = ScoringCriteria(SEMANTICS, "SEC7", "There are no redundant classes")
        sec8 = ScoringCriteria(SEMANTICS, "SEC8", "There are no redundant attributes")
        sec9 = ScoringCriteria(SEMANTICS, "SEC9", "There are no redundant operations")
        sec10 = ScoringCriteria(SEMANTICS, "SEC10", "There are no redundant relations")  

        self.semantics_criteria = [sec1, sec2, sec3, sec4, sec5, sec6, sec7, sec8, sec9, sec10]
        self.criteria = self.completeness_criteria + self.syntax_criteria + self.semantics_criteria

