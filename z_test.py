from tools.syntactic_check import SyntacticCheck

m1 = "*"
m2 = "0..22"
m3 = "1..*"
m4 = "*..*"
m5 = "*..30"
print(SyntacticCheck.is_valid_multiplicity(m1))  # True
print(SyntacticCheck.is_valid_multiplicity(m2))  # True
print(SyntacticCheck.replace_high_numbers_in_multiplicity(m1))  # "*"
print(SyntacticCheck.replace_high_numbers_in_multiplicity(m2))  # "0..22"
print(SyntacticCheck.replace_high_numbers_in_multiplicity(m3))  # "1..*"
print(SyntacticCheck.replace_high_numbers_in_multiplicity(m4))  # "*..*"
print(SyntacticCheck.replace_high_numbers_in_multiplicity(m5))  # "*..*"
print(SyntacticCheck.is_multiplicity_match_replace_high_numbers(m1, m2))  # True

print(SyntacticCheck.get_numbers_or_stars_from_multiplicity(m1))  # ("*", "*"
print(SyntacticCheck.get_numbers_or_stars_from_multiplicity(m2))  # ("0", "22"
print(SyntacticCheck.get_numbers_or_stars_from_multiplicity(m3))  # ("1", "*"
print(SyntacticCheck.get_numbers_or_stars_from_multiplicity(m4))  # ("*", "*"
print(SyntacticCheck.get_numbers_or_stars_from_multiplicity(m5))  # ("*", "*"
print(SyntacticCheck.get_numbers_or_stars_from_multiplicity("lol"))

print(SyntacticCheck.compare_multiplicities(m1, m2), m2)  # 0.0
print(SyntacticCheck.compare_multiplicities(m1, m3), m3)  # 0.0
print(SyntacticCheck.compare_multiplicities(m1, m4), m4)  # 0.0
print(SyntacticCheck.compare_multiplicities(m1, m5), m5)  # 0.0

@staticmethod
def evaluate_attributes(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
    attribute_completeness_score: float = 1.0
    total_score = len(model.attr_match_map)
    score: float = total_score
    SCORE_PUNISHMENT = 1/5
    if model.instructor_model.class_list:
        for attr_i, attr_s in model.attr_match_map.items():
            if not SyntacticCheck.syntactic_match(attr_i, attr_s)[0] and not SemanticCheck.semantic_match(attr_i, attr_s)[0]:
                score -= SCORE_PUNISHMENT
            if attr_i.data_type != attr_s.data_type:
                score -= SCORE_PUNISHMENT * (1/2 if attr_i.data_type == UMLDataType.UNKNOWN else 1)
            if attr_i.visibility != attr_s.visibility:
                score -= SCORE_PUNISHMENT * (1/2 if attr_i.visibility == UMLVisibility.UNKNOWN else 1)
            if attr_i.initial != attr_s.initial:
                score -= SCORE_PUNISHMENT * (1/2 if attr_i.initial == "" else 1)
            if attr_i.derived != attr_s.derived:
                score -= SCORE_PUNISHMENT * (1/2 if not attr_i.derived else 1)
        attribute_completeness_score = score / total_score if total_score > 0 else 1.0
    criteria.score = attribute_completeness_score
    return criteria

@staticmethod
def evaluate_operations(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
    operation_completeness_score: float = 1.0
    total_score = len(model.oper_matched_map)
    score: float = total_score
    SCORE_PUNISHMENT = 1/4
    if model.instructor_model.class_list:
        for op_i, op_s in model.oper_matched_map.items():
            if not SyntacticCheck.syntactic_match(op_i, op_s)[0] and not SemanticCheck.semantic_match(op_i, op_s)[0]:
                score -= SCORE_PUNISHMENT
            if op_i.visibility != op_s.visibility:
                score -= SCORE_PUNISHMENT * (1/2 if op_i.visibility == UMLVisibility.UNKNOWN else 1)
            if op_i.params != op_s.params:
                # NOTE: similar to the syntactic check this can be replaced later with a more sophisticated check
                # but for now this is sufficient since there are no parameters in any of the test cases
                score -= SCORE_PUNISHMENT * (1/2 if not op_i.params else 1)
            if op_i.return_types != op_s.return_types:
                # NOTE: similar to the parameters this can be replaced later with a more sophisticated check
                # but for now this is sufficient since there are no return types in any of the test cases
                score -= SCORE_PUNISHMENT * (1/2 if not op_i.return_types else 1)
        operation_completeness_score = score / total_score if total_score > 0 else 1.0
    criteria.score = operation_completeness_score
    return criteria

@staticmethod
def evaluate_relations(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
    relation_completeness_score: float = 1.0
    total_score = len(model.relation_match_map)
    score: float = total_score
    SCORE_PUNISHMENT = 1/3
    if model.instructor_model.relation_list:
        for rel_i, rel_s in model.relation_match_map.items():
            if rel_i.type != rel_s.type:
                score -= SCORE_PUNISHMENT
            if rel_i.s_multiplicity != rel_s.s_multiplicity:
                score -= SCORE_PUNISHMENT * (1/2 if SyntacticCheck.is_multiplicity_match_replace_high_numbers(rel_i.s_multiplicity, rel_s.s_multiplicity) else 1)
            if rel_i.d_multiplicity != rel_s.d_multiplicity:
                score -= SCORE_PUNISHMENT * (1/2 if SyntacticCheck.is_multiplicity_match_replace_high_numbers(rel_i.d_multiplicity, rel_s.d_multiplicity) else 1)
            cleaned_desc_i = rel_i.description.replace("<", "").replace(">", "") if rel_i.description else ""
            cleaned_desc_s = rel_s.description.replace("<", "").replace(">", "") if rel_s.description else ""
            if rel_i.description and not SyntacticCheck.syntactic_match(cleaned_desc_i, cleaned_desc_s)[0] and not SemanticCheck.semantic_match(cleaned_desc_i, cleaned_desc_s)[0]:
                # NOTE: we ignore the direction of the description since its hard to check if the reversed direction could be also semantically correct 
                # can still be that we punish here wrongly assuming the student used a description in reverse direction that has a description that is not a match
                score -= SCORE_PUNISHMENT 
        relation_completeness_score = score / total_score if total_score > 0 else 1.0
    criteria.score = relation_completeness_score
    return criteria

@staticmethod
def evaluate_multiplicities(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
    multiplicity_completeness_score: float = 1.0
    total_score = len(model.relation_match_map)
    score: float = total_score
    SCORE_PUNISHMENT = 1/2
    if model.relation_match_map:
        for rel_i, rel_s in model.relation_match_map.items():
            if not SyntacticCheck.is_multiplicity_match_replace_high_numbers(rel_i.s_multiplicity, rel_s.s_multiplicity):
                score -= SCORE_PUNISHMENT
            if not SyntacticCheck.is_multiplicity_match_replace_high_numbers(rel_i.d_multiplicity, rel_s.d_multiplicity):
                score -= SCORE_PUNISHMENT
        multiplicity_completeness_score = score / total_score if total_score > 0 else 1.0
    criteria.score = multiplicity_completeness_score
    return criteria

@staticmethod
def evaluate_roles(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
    # NOTE: role names are not implemented in the PlantUML parser, so this method is a placeholder.
    criteria.score = 1.0
    return criteria

@staticmethod
def evaluate_relation_names(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
    relation_name_completeness_score: float = 1.0
    total_score = len(model.relation_match_map)
    score: float = total_score
    SCORE_PUNISHMENT = 1
    if model.relation_match_map:
        for rel_i, rel_s in model.relation_match_map.items():
            cleaned_desc_i = rel_i.description.replace("<", "").replace(">", "") if rel_i.description else ""
            cleaned_desc_s = rel_s.description.replace("<", "").replace(">", "") if rel_s.description else ""
            if rel_i.description and not SyntacticCheck.syntactic_match(cleaned_desc_i, cleaned_desc_s)[0] and not SemanticCheck.semantic_match(cleaned_desc_i, cleaned_desc_s)[0]:
                score -= SCORE_PUNISHMENT
        relation_name_completeness_score = score / total_score if total_score > 0 else 1.0
    criteria.score = relation_name_completeness_score
    return criteria

@staticmethod
def evaluate_enumerations(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
    enumeration_completeness_score: float = 1.0
    total_score = len(model.enum_match_map)
    score: float = 0.0
    if model.enum_match_map:
        for enum_i, enum_s in model.enum_match_map.items():
            if SyntacticCheck.syntactic_match(enum_i.name, enum_s.name)[0] or SemanticCheck.semantic_match(enum_i.name, enum_s.name)[0]:
                score += 1
        enumeration_completeness_score = score / total_score if total_score > 0 else 1.0
    criteria.score = enumeration_completeness_score
    return criteria

@staticmethod
def evaluate_enum_values(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
    enum_value_completeness_score: float = 1.0
    total_score = sum(len(enum.values) for enum in model.instructor_model.enum_list)
    score: float = 0.0
    if model.value_match_map:
        for val_i, val_s in model.value_match_map.items():
            if SyntacticCheck.syntactic_match(val_i, val_s)[0] or SemanticCheck.semantic_match(val_i, val_s)[0]:
                score += 1
        enum_value_completeness_score = score / total_score if total_score > 0 else 1.0
    criteria.score = enum_value_completeness_score
    return criteria