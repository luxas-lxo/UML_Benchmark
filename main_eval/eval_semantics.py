from plantuml_eval.eval_model import EvalModel
from main_eval.eval_metrics import ScoringCriteria, NO_STATEMENT
from UML_model.uml_class import UMLVisibility, UMLDataType
from UML_model.uml_relation import UMLRelationType
from tools.syntactic_check import SyntacticCheck
from tools.semantic_check import SemanticCheck

class SemanticsEvaluator:
    @staticmethod
    def evaluate_classes(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        # NOTE: this is a placeholder
        criteria.score = NO_STATEMENT
        return criteria
    
    @staticmethod
    def evaluate_cls_names(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        class_name_semantic_score: float = NO_STATEMENT
        inst_matched_classes = {cls for cls in model.instructor_model.class_list if cls not in model.temp_missing_classes}
        if inst_matched_classes:
            total_classes = len(inst_matched_classes)
            name_score: float = 0.0
            for cls_i in inst_matched_classes:
                print(f"cls_i: {cls_i}")
                if model.class_match_map.get(cls_i) and (SyntacticCheck.syntactic_match(cls_i.name, model.class_match_map.get(cls_i).name)[0] or SemanticCheck.semantic_match(cls_i.name, model.class_match_map.get(cls_i).name)[0]):
                    name_score += 1
                elif model.split_class_map.get(cls_i) and (SyntacticCheck.syntactic_match(cls_i.name, model.split_class_map.get(cls_i)[0].name)[0] or SemanticCheck.semantic_match(cls_i.name, model.split_class_map.get(cls_i)[0].name)[0] or SyntacticCheck.syntactic_match(cls_i.name, model.split_class_map.get(cls_i)[1].name)[0] or SemanticCheck.semantic_match(cls_i.name, model.split_class_map.get(cls_i)[1].name)[0]):
                    name_score += 1
                else:
                    cls_i_merge_map = {classes_i[1]: cls_s for classes_i, cls_s in model.merge_class_map.items() if classes_i[1] == cls_i}
                    if cls_i_merge_map and (SyntacticCheck.syntactic_match(cls_i.name, cls_i_merge_map.get(cls_i).name)[0] or SemanticCheck.semantic_match(cls_i.name, cls_i_merge_map.get(cls_i).name)[0]):
                        name_score += 1
            class_name_semantic_score = name_score / total_classes if total_classes > 0 else NO_STATEMENT
        criteria.score = class_name_semantic_score
        return criteria

    @staticmethod
    def evaluate_cls_attributes(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        class_attr_semantic_score: float = NO_STATEMENT
        SPLIT_MERGE_PENALTY = 0.5
        inst_matched_classes = {cls for cls in model.instructor_model.class_list if cls not in model.temp_missing_classes}
        if inst_matched_classes:
            total_classes = len(inst_matched_classes)
            class_score: float = 0.0
            for cls_i in inst_matched_classes:
                attr_score: float = 0.0
                cls_i_matched_attrs = [attr for attr in cls_i.attributes if attr in model.attr_match_map.keys()]
                cls_i_inherited_attrs = [attr for attr in cls_i.attributes if attr in model.inherited_attr_map.keys()]
                cls_i_misplaced_attrs = [attr for attr in cls_i.attributes if attr in model.misplaced_attr_map.keys()]
                total_class_attrs = len(cls_i_matched_attrs) + len(cls_i_inherited_attrs) + len(cls_i_misplaced_attrs)

                # NOTE: cls_i_match_map, cls_i_split_map can only contain one or no mapping
                # NOTE: if the class is in the match map, that means all its matched, inherited attributes are in the student class 
                cls_i_match_map = {class_i: cls_s for class_i, cls_s in model.class_match_map.items() if cls_i == class_i}
                # NOTE: if the class is in the split map, that means all its matched, inherited or misplaced attributes are either in the first or second class of the split
                cls_i_split_map = {class_i: classes_s for class_i, classes_s in model.split_class_map.items() if cls_i == class_i}
                # NOTE: here we only check the second class since from the algorith the first class is already matched to the student class
                # if the class would be the fist class, we would have dealt with it in the match map
                # if the class is in the merge map as the second class, that means all its missplaced attributes are in the student class (which is matched to the first class)
                cls_i_merge_map = {classes_i[1]: cls_s for classes_i, cls_s in model.merge_class_map.items() if cls_i == classes_i[1]}
                if cls_i_match_map:
                    attr_score += len(cls_i_matched_attrs) + len(cls_i_inherited_attrs) 
                if cls_i_split_map or cls_i_merge_map:
                    # NOTE: we only take the len of the misplaced attributes here since the matched attributes are already counted in the match map and if the class has no true match it also has no attributes in the match map
                    attr_score += len(cls_i_misplaced_attrs) * SPLIT_MERGE_PENALTY
                class_score += attr_score / total_class_attrs if total_class_attrs > 0 else 1.0
            class_attr_semantic_score = class_score / total_classes if total_classes > 0 else NO_STATEMENT
        criteria.score = class_attr_semantic_score
        return criteria


    @staticmethod
    def evaluate_cls_operations(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        class_op_semantic_score: float = NO_STATEMENT
        SPLIT_MERGE_PENALTY = 0.5
        inst_matched_classes = {cls for cls in model.instructor_model.class_list if cls not in model.temp_missing_classes}
        if inst_matched_classes:
            total_classes = len(inst_matched_classes)
            class_score: float = 0.0
            for cls_i in inst_matched_classes:
                oper_score: float = 0.0
                cls_i_matched_opers = [oper for oper in cls_i.operations if oper in model.oper_matched_map.keys()]
                cls_i_inherited_opers = [oper for oper in cls_i.operations if oper in model.inherited_oper_map.keys()]
                cls_i_misplaced_opers = [oper for oper in cls_i.operations if oper in model.misplaced_oper_map.keys()]
                total_class_opers = len(cls_i_matched_opers) + len(cls_i_inherited_opers) + len(cls_i_misplaced_opers)

                # NOTE: cls_i_match_map, cls_i_split_map can only contain one or no mapping
                # NOTE: if the class is in the match map, that means all its matched, inherited operations are in the student class 
                cls_i_match_map = {class_i: cls_s for class_i, cls_s in model.class_match_map.items() if cls_i == class_i}
                # NOTE: if the class is in the split map, that means all its matched, inherited or misplaced operations are either in the first or second class of the split
                cls_i_split_map = {class_i: classes_s for class_i, classes_s in model.split_class_map.items() if cls_i == class_i}
                # NOTE: here we only check the second class since from the algorith the first class is already matched to the student class
                # if the class would be the fist class, we would have dealt with it in the match map
                # if the class is in the merge map as the second class, that means all its missplaced operations are in the student class (which is matched to the first class)
                cls_i_merge_map = {classes_i[1]: cls_s for classes_i, cls_s in model.merge_class_map.items() if cls_i == classes_i[1]}
                if cls_i_match_map:
                    oper_score += len(cls_i_matched_opers) + len(cls_i_inherited_opers) 
                if cls_i_split_map or cls_i_merge_map:
                    # NOTE: we only take the len of the misplaced operations here since the matched operations are already counted in the match map and if the class has no true match it also has no operations in the match map
                    oper_score += len(cls_i_misplaced_opers) * SPLIT_MERGE_PENALTY
                class_score += oper_score / total_class_opers if total_class_opers > 0 else 1.0
            class_op_semantic_score = class_score / total_classes if total_classes > 0 else NO_STATEMENT
        criteria.score = class_op_semantic_score
        return criteria
    
    @staticmethod
    def evaluate_attributes(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        attribute_semantic_score: float = NO_STATEMENT
        SCORE_PER_CRIT = 1/6
        if model.temp_all_att_matches:
            total_attributes = len(model.temp_all_att_matches)
            attr_score: float = 0.0
            for attr_i, attr_s in model.temp_all_att_matches.items():
                if SyntacticCheck.syntactic_match(attr_i.name, attr_s.name)[0] or SemanticCheck.semantic_match(attr_i.name, attr_s.name)[0]:
                    attr_score += SCORE_PER_CRIT

                if attr_i.derived == attr_s.derived:
                    attr_score += SCORE_PER_CRIT

                if attr_i.visibility == attr_s.visibility:
                    attr_score += SCORE_PER_CRIT
                elif attr_i.visibility == UMLVisibility.UNKNOWN:
                    # NOTE: we give half the score if no specification is given by the inst solution, but the student has a specification since we consider this less of a mistake than a complete mismatch
                    attr_score += SCORE_PER_CRIT / 2
                
                if attr_i.multiplicity == attr_s.multiplicity:
                    attr_score += SCORE_PER_CRIT
                elif SyntacticCheck.is_multiplicity_match_replace_high_numbers(attr_i.multiplicity, attr_s.multiplicity):
                    # NOTE: we give 3/4 of the score if the multiplicity is a match but with "high numbers" replaced with "*"
                    attr_score += SCORE_PER_CRIT * 3/4
                elif attr_i.multiplicity == "1":
                    # NOTE: we give half the score if no specification is given by the inst solution, but the student has a specification since we consider this less of a mistake than a complete mismatch
                    attr_score += SCORE_PER_CRIT / 2

                if attr_i.data_type == attr_s.data_type:
                    attr_score += SCORE_PER_CRIT
                elif attr_i.data_type == UMLDataType.UNKNOWN:
                    # NOTE: we give half the score if no specification is given by the inst solution, but the student has a specification since we consider this less of a mistake than a complete mismatch
                    attr_score += SCORE_PER_CRIT / 2

                if attr_i.initial == attr_s.initial:
                    attr_score += SCORE_PER_CRIT
                elif attr_i.initial == "":
                    # NOTE: we give half the score if no specification is given by the inst solution, but the student has a specification since we consider this less of a mistake than a complete mismatch
                    attr_score += SCORE_PER_CRIT / 2

            attribute_semantic_score = attr_score / (total_attributes) if total_attributes > 0 else NO_STATEMENT
        criteria.score = attribute_semantic_score
        return criteria
    
    @staticmethod
    def evaluate_att_names(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        attribute_name_semantic_score: float = NO_STATEMENT
        if model.temp_all_att_matches:
            total_attributes = len(model.temp_all_att_matches)
            attr_score: float = 0.0
            for attr_i, attr_s in model.temp_all_att_matches.items():
                if SyntacticCheck.syntactic_match(attr_i.name, attr_s.name)[0] or SemanticCheck.semantic_match(attr_i.name, attr_s.name)[0]:
                    attr_score += 1
            attribute_name_semantic_score = attr_score / total_attributes if total_attributes > 0 else NO_STATEMENT
        criteria.score = attribute_name_semantic_score
        return criteria
    
    @staticmethod
    def evaluate_att_derivation(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        attribute_derived_semantic_score: float = NO_STATEMENT
        if model.temp_all_att_matches:
            total_attributes = len(model.temp_all_att_matches)
            attr_score: float = 0.0
            for attr_i, attr_s in model.temp_all_att_matches.items():
                if attr_i.derived == attr_s.derived:
                    attr_score += 1
            attribute_derived_semantic_score = attr_score / total_attributes if total_attributes > 0 else NO_STATEMENT
        criteria.score = attribute_derived_semantic_score
        return criteria
    
    @staticmethod
    def evaluate_att_visibility(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        attribute_visibility_semantic_score: float = NO_STATEMENT
        if model.temp_all_att_matches:
            total_attributes = len(model.temp_all_att_matches)
            attr_score: float = 0.0
            for attr_i, attr_s in model.temp_all_att_matches.items():
                if attr_i.visibility == attr_s.visibility:
                    attr_score += 1
                elif attr_i.visibility == UMLVisibility.UNKNOWN:
                    # NOTE: we give half the score if no specification is given by the inst solution, but the student has a specification since we consider this less of a mistake than a complete mismatch
                    attr_score += 0.5
            attribute_visibility_semantic_score = attr_score / total_attributes if total_attributes > 0 else NO_STATEMENT
        criteria.score = attribute_visibility_semantic_score
        return criteria
    
    @staticmethod
    def evaluate_att_multiplicity(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        attribute_multiplicity_semantic_score: float = NO_STATEMENT
        REPLACE_HIGH_NUMBER_SCORE = 0.75
        if model.temp_all_att_matches:
            total_attributes = len(model.temp_all_att_matches)
            attr_score: float = 0.0
            for attr_i, attr_s in model.temp_all_att_matches.items():
                if attr_i.multiplicity == attr_s.multiplicity:
                    attr_score += 1
                elif SyntacticCheck.is_multiplicity_match_replace_high_numbers(attr_i.multiplicity, attr_s.multiplicity):
                    attr_score += REPLACE_HIGH_NUMBER_SCORE
                elif attr_i.multiplicity == "1":
                    # NOTE: we give half the score if no specification is given by the inst solution, but the student has a specification since we consider this less of a mistake than a complete mismatch
                    attr_score += 0.5
            attribute_multiplicity_semantic_score = attr_score / total_attributes if total_attributes > 0 else NO_STATEMENT
        criteria.score = attribute_multiplicity_semantic_score
        return criteria
    
    @staticmethod
    def evaluate_att_data_types(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        attribute_data_type_semantic_score: float = NO_STATEMENT
        if model.temp_all_att_matches:
            total_attributes = len(model.temp_all_att_matches)
            attr_score: float = 0.0
            for attr_i, attr_s in model.temp_all_att_matches.items():
                if attr_i.data_type == attr_s.data_type:
                    attr_score += 1
                elif attr_i.data_type == UMLDataType.UNKNOWN:
                    # NOTE: we give half the score if no specification is given by the inst solution, but the student has a specification since we consider this less of a mistake than a complete mismatch
                    attr_score += 0.5
            attribute_data_type_semantic_score = attr_score / total_attributes if total_attributes > 0 else NO_STATEMENT
        criteria.score = attribute_data_type_semantic_score
        return criteria
    
    @staticmethod
    def evaluate_att_initial_values(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        attribute_initial_semantic_score: float = NO_STATEMENT
        if model.temp_all_att_matches:
            total_attributes = len(model.temp_all_att_matches)
            attr_score: float = 0.0
            for attr_i, attr_s in model.temp_all_att_matches.items():
                if attr_i.initial == attr_s.initial:
                    attr_score += 1
                elif attr_i.initial == "":
                    # NOTE: we give half the score if no specification is given by the inst solution, but the student has a specification since we consider this less of a mistake than a complete mismatch
                    attr_score += 0.5
            attribute_initial_semantic_score = attr_score / total_attributes if total_attributes > 0 else NO_STATEMENT
        criteria.score = attribute_initial_semantic_score
        return criteria
    
    @staticmethod
    def evaluate_operations(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        operation_semantic_score: float = NO_STATEMENT
        SCORE_PER_CRIT = 1/4
        if model.temp_all_oper_matches:
            total_operations = len(model.temp_all_oper_matches)
            oper_score: float = 0.0
            for oper_i, oper_s in model.temp_all_oper_matches.items():
                if SyntacticCheck.syntactic_match(oper_i.name, oper_s.name)[0] or SemanticCheck.semantic_match(oper_i.name, oper_s.name)[0]:
                    oper_score += SCORE_PER_CRIT

                if oper_i.visibility == oper_s.visibility:
                    oper_score += SCORE_PER_CRIT
                elif oper_i.visibility == UMLVisibility.UNKNOWN:
                    # NOTE: we give half the score if no specification is given by the inst solution, but the student has a specification since we consider this less of a mistake than a complete mismatch
                    oper_score += SCORE_PER_CRIT / 2

                # NOTE: here we could check for more details and give a more detailed score
                # but in the test data are no parameters or return types anyway
                if oper_i.params == oper_s.params:
                    oper_score += SCORE_PER_CRIT
                elif not oper_i.params:
                    # NOTE: we give half the score if no specification is given by the inst solution, but the student has a specification since we consider this less of a mistake than a complete mismatch
                    oper_score += SCORE_PER_CRIT / 2
                
                if oper_i.return_types == oper_s.return_types:
                    oper_score += SCORE_PER_CRIT
                elif oper_i.return_types == [UMLDataType.VOID]:
                    # NOTE: we give half the score if no specification is given by the inst solution, but the student has a specification since we consider this less of a mistake than a complete mismatch
                    oper_score += SCORE_PER_CRIT / 2
                
            operation_semantic_score = oper_score / (total_operations) if total_operations > 0 else NO_STATEMENT
        criteria.score = operation_semantic_score
        return criteria
    
    @staticmethod
    def evaluate_opr_names(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        operation_name_semantic_score: float = NO_STATEMENT
        if model.temp_all_oper_matches:
            total_operations = len(model.temp_all_oper_matches)
            oper_score: float = 0.0
            for oper_i, oper_s in model.temp_all_oper_matches.items():
                if SyntacticCheck.syntactic_match(oper_i.name, oper_s.name)[0] or SemanticCheck.semantic_match(oper_i.name, oper_s.name)[0]:
                    oper_score += 1
            operation_name_semantic_score = oper_score / total_operations if total_operations > 0 else NO_STATEMENT
        criteria.score = operation_name_semantic_score
        return criteria
    
    @staticmethod
    def evaluate_opr_visibility(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        operation_visibility_semantic_score: float = NO_STATEMENT
        if model.temp_all_oper_matches:
            total_operations = len(model.temp_all_oper_matches)
            oper_score: float = 0.0
            for oper_i, oper_s in model.temp_all_oper_matches.items():
                if oper_i.visibility == oper_s.visibility:
                    oper_score += 1
                elif oper_i.visibility == UMLVisibility.UNKNOWN:
                    # NOTE: we give half the score if no specification is given by the inst solution, but the student has a specification since we consider this less of a mistake than a complete mismatch
                    oper_score += 0.5
            operation_visibility_semantic_score = oper_score / total_operations if total_operations > 0 else NO_STATEMENT
        criteria.score = operation_visibility_semantic_score
        return criteria
    
    @staticmethod
    def evaluate_opr_params(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        operation_params_semantic_score: float = NO_STATEMENT
        if model.temp_all_oper_matches:
            total_operations = len(model.temp_all_oper_matches)
            oper_score: float = 0.0
            for oper_i, oper_s in model.temp_all_oper_matches.items():
                if oper_i.params == oper_s.params:
                    oper_score += 1
                elif not oper_i.params:
                    # NOTE: we give half the score if no specification is given by the inst solution, but the student has a specification since we consider this less of a mistake than a complete mismatch
                    oper_score += 0.5
            operation_params_semantic_score = oper_score / total_operations if total_operations > 0 else NO_STATEMENT
        criteria.score = operation_params_semantic_score
        return criteria
    
    @staticmethod
    def evaluate_opr_return_types(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        operation_return_type_semantic_score: float = NO_STATEMENT
        if model.temp_all_oper_matches:
            total_operations = len(model.temp_all_oper_matches)
            oper_score: float = 0.0
            for oper_i, oper_s in model.temp_all_oper_matches.items():
                if oper_i.return_types == oper_s.return_types:
                    oper_score += 1
                elif oper_i.return_types == [UMLDataType.VOID]:
                    # NOTE: we give half the score if no specification is given by the inst solution, but the student has a specification since we consider this less of a mistake than a complete mismatch
                    oper_score += 0.5
            operation_return_type_semantic_score = oper_score / total_operations if total_operations > 0 else NO_STATEMENT
        criteria.score = operation_return_type_semantic_score
        return criteria
    
    @staticmethod
    def evaluate_enumerations(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        # NOTE: this is a placeholder
        criteria.score = NO_STATEMENT
        return criteria
    
    @staticmethod
    def evaluate_enum_names(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        enum_name_semantic_score: float = NO_STATEMENT
        if model.enum_match_map:
            total_enumerations = len(model.enum_match_map)
            enum_score: float = 0.0
            for enum_i, enum_s in model.enum_match_map.items():
                if SyntacticCheck.syntactic_match(enum_i.name, enum_s.name)[0] or SemanticCheck.semantic_match(enum_i.name, enum_s.name)[0]:
                    enum_score += 1
            enum_name_semantic_score = enum_score / total_enumerations if total_enumerations > 0 else NO_STATEMENT
        criteria.score = enum_name_semantic_score
        return criteria
    
    @staticmethod
    def evaluate_enum_content(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        enum_literal_semantic_score: float = NO_STATEMENT
        if model.enum_match_map:
            total_enumerations = len(model.enum_match_map)
            enum_score: float = 0.0
            for enum_i in model.enum_match_map.keys():
                value_score: float = 0.0
                enm_matched_values_i = {val for val in enum_i.values if val in model.value_match_map.keys()}
                enm_misplaced_values_i = {val for val in enum_i.values if val in model.misplaced_value_map.keys()}
                if enm_matched_values_i:
                    total_enm_values = len(enm_matched_values_i) + len(enm_misplaced_values_i)
                    value_score = len(enm_matched_values_i) / total_enm_values if total_enm_values > 0 else 1.0
                enum_score += value_score
            enum_literal_semantic_score = enum_score / total_enumerations if total_enumerations > 0 else NO_STATEMENT
        criteria.score = enum_literal_semantic_score
        return criteria

    @staticmethod
    def evaluate_enum_values(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        value_semantic_score: float = NO_STATEMENT
        all_matched_values = model.value_match_map | model.misplaced_value_map
        if all_matched_values:
            total_enum_values = len(all_matched_values)
            value_score: float = 0.0
            for value_i, value_s in all_matched_values.items():
                if SyntacticCheck.syntactic_match(value_i.name, value_s.name)[0] or SemanticCheck.semantic_match(value_i.name, value_s.name)[0]:
                    value_score += 1
            value_semantic_score = value_score / total_enum_values if total_enum_values > 0 else NO_STATEMENT
        criteria.score = value_semantic_score
        return criteria
    
    @staticmethod
    def evaluate_relations(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        # NOTE: this is a placeholder
        criteria.score = NO_STATEMENT
        return criteria
    
    @staticmethod
    def evaluate_rel_types(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        relation_type_semantic_score: float = NO_STATEMENT
        if model.relation_match_map or model.inst_assoc_link_match_map or model.sec_derivation_inst_map or model.sec_derivation_stud_map:
            total_relations = len(model.relation_match_map) + len(model.inst_assoc_link_match_map) + len(model.sec_derivation_inst_map) * 2 + len(model.sec_derivation_stud_map)
            rel_score: float = 0.0
            for rel_i, rel_s in model.relation_match_map.items():
                if rel_i.type == rel_s.type:
                    rel_score += 1
            # NOTE: for all the other matches we do not give points since the relation was split up or merged
            relation_type_semantic_score = rel_score / total_relations if total_relations > 0 else NO_STATEMENT
        criteria.score = relation_type_semantic_score
        return criteria
    
    @staticmethod
    def evaluate_rel_multiplicity(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        relation_multiplicity_semantic_score: float = NO_STATEMENT
        if model.relation_match_map or model.inst_assoc_link_match_map or model.sec_derivation_inst_map or model.sec_derivation_stud_map:
            total_relations = len(model.relation_match_map) + len(model.inst_assoc_link_match_map) + len(model.sec_derivation_inst_map) * 2 + len(model.sec_derivation_stud_map)
            rel_score: float = 0.0
            for rel_i, rel_s in model.relation_match_map.items():
                if rel_i.s_multiplicity == rel_s.s_multiplicity:
                    rel_score += 1 / 2
                elif SyntacticCheck.is_multiplicity_match_replace_high_numbers(rel_i.s_multiplicity, rel_s.s_multiplicity):
                    # NOTE: we give 3/4 of the score if the multiplicity is a match but with "high numbers" replaced with "*"
                    rel_score += (3/4) / 2
                elif rel_i.s_multiplicity == "1":
                    # NOTE: we give half the score if no specification is given by the inst solution, but the student has a specification since we consider this less of a mistake than a complete mismatch
                    rel_score += (1/2) / 2
                
                if rel_i.d_multiplicity == rel_s.d_multiplicity:
                    rel_score += 1 / 2
                elif SyntacticCheck.is_multiplicity_match_replace_high_numbers(rel_i.d_multiplicity, rel_s.d_multiplicity):
                    # NOTE: we give 3/4 of the score if the multiplicity is a match but with "high numbers" replaced with "*"
                    rel_score += (3/4) / 2
                elif rel_i.d_multiplicity == "1":
                    # NOTE: we give half the score if no specification is given by the inst solution, but the student has a specification since we consider this less of a mistake than a complete mismatch
                    rel_score += (1/2) / 2
            relation_multiplicity_semantic_score = rel_score / total_relations if total_relations > 0 else NO_STATEMENT
        criteria.score = relation_multiplicity_semantic_score
        return criteria
    
    @staticmethod
    def evaluate_rel_descriptions(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        relation_description_semantic_score: float = NO_STATEMENT
        if model.relation_match_map or model.inst_assoc_link_match_map or model.sec_derivation_inst_map or model.sec_derivation_stud_map:
            total_relations = len(model.relation_match_map) + len(model.inst_assoc_link_match_map) + len(model.sec_derivation_inst_map) * 2 + len(model.sec_derivation_stud_map)
            rel_score: float = 0.0
            for rel_i, rel_s in model.relation_match_map.items():
                # NOTE: we ignore the direction of the description since its hard to check if the reversed direction could be also semantically correct 
                # can still be that we punish here wrongly assuming the student used a description in reverse direction that has a description that is not a match
                # e.g. rel_i.desc = "parent >" and rel_s.desc = "child <"
                # could be extended to check for semantic opposites
                cleaned_rel_i_description = rel_i.description.replace("<", "").replace(">", "") if rel_i.description else ""
                cleaned_rel_s_description = rel_s.description.replace("<", "").replace(">", "") if rel_s.description else ""
                if SyntacticCheck.syntactic_match(cleaned_rel_i_description, cleaned_rel_s_description)[0] or SemanticCheck.semantic_match(cleaned_rel_i_description, cleaned_rel_s_description)[0]:
                    rel_score += 1
                elif not cleaned_rel_i_description:
                    # NOTE: we give half the score if no specification is given by the inst solution, but the student has a specification since we consider this less of a mistake than a complete mismatch
                    # for the description we could even consider giving full points then since this does not necessarily mean that the given description is wrong 
                    # but since we cannot check the meaning of the description we give half the points
                    rel_score += 0.5
            relation_description_semantic_score = rel_score / total_relations if total_relations > 0 else NO_STATEMENT
        criteria.score = relation_description_semantic_score
        return criteria
    
    @staticmethod
    def evaluate_relations_with_type(criteria: ScoringCriteria, model: EvalModel, rel_type: UMLRelationType) -> ScoringCriteria:
        # NOTE: this is a placeholder
        criteria.score = NO_STATEMENT
        return criteria



    
