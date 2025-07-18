from plantuml_eval.eval_model import EvalModel
from main_eval.eval_metrics import ScoringCriteria
from UML_model.uml_relation import UMLRelationType, UMLRelation
from UML_model.uml_class import UMLDataType, UMLVisibility
from tools.syntactic_check import SyntacticCheck
from tools.UML_parser import ERROR_FLAG

from itertools import chain
from typing import Dict

class SyntaxEvaluator:
    @staticmethod
    def evaluate_classes(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        # NOTE: could be split into different criteria
        # this method validates the syntax relative to the instructor model (e.g. what is in the instructor model must be in the student model doesn't matter the semnatics of it)
        total_score = 0
        SCORE_PUNISHMENT = 1/3
        for cls_i, cls_s in model.class_match_map.items():
            total_score += 1
            if len(cls_i.attributes) > len(cls_s.attributes):
                total_score -= SCORE_PUNISHMENT
            if len(cls_i.operations) > len(cls_s.operations):
                total_score -= SCORE_PUNISHMENT
            if  cls_s.name == ERROR_FLAG:
                total_score -= SCORE_PUNISHMENT
        max_score = len(model.class_match_map)
        class_syntax_score = total_score / max_score if max_score > 0 else 1.0
        criteria.score = class_syntax_score
        return criteria
    
    @staticmethod
    def evaluate_formal_classes(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        # NOTE: here only names are evaluated, since the parser should not allow any other syntax errors
        all_classes = len(model.student_model.class_list)
        score = all_classes
        seen = set()
        duplicated_class_names = set()
        SCORE_PUNISHMENT = 1
        for cls_s in model.student_model.class_list:
            name_s = cls_s.name.lower().strip()
            if name_s in seen:
                duplicated_class_names.add(name_s)
            else:
                seen.add(name_s)
            if cls_s.name == ERROR_FLAG or name_s in duplicated_class_names:
                score -= SCORE_PUNISHMENT
        total_score = score / all_classes if all_classes > 0 else 1.0
        criteria.score = total_score
        return criteria
    

    @staticmethod
    def evaluate_attributes(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        # NOTE: could be split into different criteria
        # this method validates the syntax relative to the instructor model (e.g. what is in the instructor model must be in the student model doesn't matter the semnatics of it)
        total_score = 0
        SCORE_PUNISHMENT = 1/5
        for att_i, att_s in chain(model.misplaced_attr_map.items(), model.attr_match_map.items()):
            total_score += 1
            if att_i.derived and not att_s.derived:
                total_score -= SCORE_PUNISHMENT
            if (att_i.data_type != UMLDataType.UNKNOWN and att_s.data_type == UMLDataType.UNKNOWN) or att_s.data_type == UMLDataType.ERROR:
                total_score -= SCORE_PUNISHMENT
            if (att_i.visibility != UMLVisibility.UNKNOWN and att_s.visibility == UMLVisibility.UNKNOWN) or att_s.visibility == UMLVisibility.ERROR:
                total_score -= SCORE_PUNISHMENT
            if (att_i.initial != "" and  att_s.initial == "") or att_s.initial == ERROR_FLAG:
                total_score -= SCORE_PUNISHMENT
            if att_s.name == ERROR_FLAG:
                total_score -= SCORE_PUNISHMENT
        max_score = len(model.attr_match_map) + len(model.misplaced_attr_map)
        attribute_syntax_score = total_score / max_score if max_score > 0 else 1.0
        criteria.score = attribute_syntax_score
        return criteria

    @staticmethod
    def evaluate_formal_attributes(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        # NOTE: could be split into different criteria
        # this method validates the syntax global in the student model
        all_atts = len(model.student_model.attribute_list)
        score = all_atts
        SCORE_PUNISHMENT = 1
        for att_s in model.student_model.attribute_list:
            if att_s.initial == ERROR_FLAG or att_s.visibility == UMLVisibility.ERROR or att_s.data_type == UMLDataType.ERROR or att_s.name == ERROR_FLAG:
                score -= SCORE_PUNISHMENT
        total_score = score / all_atts if all_atts > 0 else 1.0
        criteria.score = total_score
        return criteria
    
    @staticmethod
    def evaluate_operations(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        total_score = 0
        SCORE_PUNISHMENT = 1/4
        for op_i, op_s in chain(model.misplaced_oper_map.items(), model.oper_matched_map.items()):
            total_score += 1
            if op_s.name == ERROR_FLAG:
                total_score -= SCORE_PUNISHMENT
            if (op_i.visibility != UMLVisibility.UNKNOWN and op_s.visibility == UMLVisibility.UNKNOWN) or op_s.visibility == UMLVisibility.ERROR:
                total_score -= SCORE_PUNISHMENT
            if (op_i.params and not op_s.params) or any(v == UMLDataType.ERROR for v in op_s.params.values()) or len(op_s.params) < len(op_i.params):
                total_score -= SCORE_PUNISHMENT
            elif op_i.params and op_s.params:
                # NOTE: this part could be replaced later with a better check but for this we would need to match params of operations
                # for our purposes should this be sufficient since no diagram contains operations with specified param types anyway
                type_counter_i = 0
                for p_type_i in op_i.params.values():
                    if p_type_i not in (UMLDataType.UNKNOWN, UMLDataType.ERROR):
                        type_counter_i +=1
                type_counter_s = 0
                for p_type_s in op_s.params.values():
                    if p_type_s not in (UMLDataType.UNKNOWN, UMLDataType.ERROR):
                        type_counter_s += 1
                if type_counter_i > type_counter_s:
                    total_score -= SCORE_PUNISHMENT
            if (op_i.return_types and not op_s.return_types) or any(t == UMLDataType.ERROR for t in op_s.return_types) or len(op_s.return_types) < len(op_i.return_types):
                total_score -= SCORE_PUNISHMENT
        max_score = len(model.oper_matched_map) + len(model.misplaced_oper_map)
        operation_syntax_score = total_score / max_score if max_score > 0 else 1.0
        criteria.score = operation_syntax_score
        return criteria
    
    @staticmethod
    def evaluate_formal_operations(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        # NOTE: could be split into different criteria
        # this method validates the syntax global in the student model
        all_ops = len(model.student_model.operation_list)
        score = all_ops
        SCORE_PUNISHMENT = 1
        for op_s in model.student_model.operation_list:
            if op_s.visibility == UMLVisibility.ERROR or any(v == UMLDataType.ERROR for v in op_s.params.values()) or any(t == UMLDataType.ERROR for t in op_s.return_types) or op_s.name == ERROR_FLAG:
                score -= SCORE_PUNISHMENT
        total_score = score / all_ops if all_ops > 0 else 1.0
        criteria.score = total_score
        return criteria
    
    @staticmethod
    def evaluate_relation(criteria: ScoringCriteria, model: EvalModel, rel_type: UMLRelationType) -> ScoringCriteria:
        filtered_rel_map: Dict[UMLRelation, UMLRelation] = {rel_i: rel_s for rel_i, rel_s in model.relation_match_map.items() if rel_i.type == rel_type}
        total_score = 0
        SCORE_PUNISHMENT = 1/4
        for rel_i, rel_s in filtered_rel_map.items():
            total_score += 1
            if rel_s.type != rel_type:
                total_score -= SCORE_PUNISHMENT
            if (rel_i.description and not rel_s.description) or rel_s.description == ERROR_FLAG:
                total_score -= SCORE_PUNISHMENT
            if rel_s.s_multiplicity == ERROR_FLAG:
                total_score -= SCORE_PUNISHMENT
            if rel_s.d_multiplicity == ERROR_FLAG:
                total_score -= SCORE_PUNISHMENT
        relation_syntax_score = total_score / len(filtered_rel_map) if filtered_rel_map else 1.0
        criteria.score = relation_syntax_score
        return criteria
    
    @staticmethod
    def evaluate_formal_relations(criteria: ScoringCriteria, model: EvalModel, rel_type: UMLRelationType) -> ScoringCriteria:
        all_filtered_relations = [rel for rel in model.student_model.relation_list if rel.type == rel_type]
        score = len(all_filtered_relations)
        SCORE_PUNISHMENT = 1
        for asso_s in model.student_model.association_list:
            if asso_s.description == ERROR_FLAG or asso_s.s_multiplicity == ERROR_FLAG or asso_s.d_multiplicity == ERROR_FLAG:
                score -= SCORE_PUNISHMENT
        total_score = score / len(all_filtered_relations) if all_filtered_relations else 1.0
        criteria.score = total_score
        return criteria

    @staticmethod
    def evaluate_all_relations(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        score = len(model.student_model.relation_list)
        SCORE_PUNISHMENT = 1
        for rel in model.student_model.relation_list:
            if rel.type == UMLRelationType.UNKNOWN or rel.description == ERROR_FLAG or rel.s_multiplicity == ERROR_FLAG or rel.d_multiplicity == ERROR_FLAG:
                score -= SCORE_PUNISHMENT
        total_score = score / len(model.student_model.relation_list) if model.student_model.relation_list else 1.0
        criteria.score = total_score
        return criteria

    
    @staticmethod
    def evaluate_multiplicities(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        all_multiplicities = [rel.s_multiplicity for rel in model.relation_match_map.values()] + [rel.d_multiplicity for rel in model.relation_match_map.values()]
        score = len(all_multiplicities)
        SCORE_PUNISHMENT = 1
        for multiplicity in all_multiplicities:
            if multiplicity == ERROR_FLAG:
                score -= SCORE_PUNISHMENT
        total_score = score / len(all_multiplicities) if all_multiplicities else 1.0
        criteria.score = total_score
        return criteria
    
    @staticmethod
    def evaluate_formal_multiplicities(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        all_multiplicities = [rel.s_multiplicity for rel in model.student_model.relation_list] + [rel.d_multiplicity for rel in model.student_model.relation_list]
        score = len(all_multiplicities)
        SCORE_PUNISHMENT = 1
        for multiplicity in all_multiplicities:
            if multiplicity == ERROR_FLAG:
                score -= SCORE_PUNISHMENT
        total_score = score / len(all_multiplicities) if all_multiplicities else 1.0
        criteria.score = total_score
        return criteria
    
    @staticmethod
    def evaluate_roles(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        # NOTE: role names are not implemented in the PlantUML parser, so this method is a placeholder.
        criteria.score = 1.0
        return criteria
    
    @staticmethod
    def evaluate_formal_roles(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        # NOTE: role names are not implemented in the PlantUML parser, so this method is a placeholder.
        criteria.score = 1.0
        return criteria
    
    @staticmethod
    def evaluate_association_classes(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        # NOTE: at the moment there is nothig that could be syntactically checked for association classes since the parser does not support syntactical differentiation
        criteria.score = 1.0
        return criteria
    
    @staticmethod
    def evaluate_formal_association_classes(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        # NOTE: at the moment there is nothig that could be syntactically checked for association classes since the parser does not support syntactical differentiation
        criteria.score = 1.0
        return criteria

    @staticmethod
    def evaluate_enumerations(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        all_enums = len(model.enum_match_map)
        score = all_enums
        SCORE_PUNISHMENT = 1/2
        for enum_i, enum_s in model.enum_match_map.items():
            if enum_s.name == ERROR_FLAG:
                score -= SCORE_PUNISHMENT
            if len(enum_i.values) > len(enum_s.values):
                score -= SCORE_PUNISHMENT
        total_score = score / all_enums if all_enums > 0 else 1.0
        criteria.score = total_score
        return criteria
    
    @staticmethod
    def evaluate_formal_enumerations(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        all_enums = len(model.student_model.enum_list)
        score = all_enums
        seen = set()
        duplicated_enum_names = set()
        SCORE_PUNISHMENT = 1
        for enum_s in model.student_model.enum_list:
            name_s = enum_s.name.lower().strip()
            if name_s in seen:
                duplicated_enum_names.add(name_s)
            else:
                seen.add(name_s)
            if enum_s.name == ERROR_FLAG or name_s in duplicated_enum_names:
                score -= SCORE_PUNISHMENT
        total_score = score / all_enums if all_enums > 0 else 1.0
        criteria.score = total_score
        return criteria

    @staticmethod
    def evaluate_enum_values(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        total_score = 0
        SCORE_PUNISHMENT = 1
        for val_s in chain(model.value_match_map.values(), model.misplaced_value_map.values()):
            total_score += 1
            if val_s.name == ERROR_FLAG:
                total_score -= SCORE_PUNISHMENT
        max_score = len(model.value_match_map) + len(model.misplaced_value_map)
        enum_value_score = total_score / max_score if max_score > 0 else 1.0
        criteria.score = enum_value_score
        return criteria
    
    @staticmethod
    def evaluate_formal_enum_values(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        all_enum_values = sum(len(enum.values) for enum in model.student_model.enum_list)
        score = all_enum_values
        SCORE_PUNISHMENT = 1
        for enum in model.student_model.enum_list:
            for value in enum.values:
                if value.name == ERROR_FLAG:
                    score -= SCORE_PUNISHMENT
        total_score = score / all_enum_values if all_enum_values > 0 else 1.0
        criteria.score = total_score
        return criteria

    @staticmethod
    def evaluate_global_class_names(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        all_classes = len(model.student_model.class_list)
        score = all_classes
        SCORE_PUNISHMENT = 1
        for cls_s in model.student_model.class_list:
            if not SyntacticCheck.is_upper_camel_case(cls_s.name):
                score -= SCORE_PUNISHMENT
        total_score = score / all_classes if all_classes > 0 else 1.0
        criteria.score = total_score
        return criteria
    
    @staticmethod
    def evaluate_global_attribute_names(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        all_atts = len(model.student_model.attribute_list)
        score = all_atts
        SCORE_PUNISHMENT = 1
        for att_s in model.student_model.attribute_list:
            if not SyntacticCheck.is_lower_camel_case(att_s.name):
                score -= SCORE_PUNISHMENT
        total_score = score / all_atts if all_atts > 0 else 1.0
        criteria.score = total_score
        return criteria
    
    @staticmethod
    def evaluate_global_operation_names(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        all_ops = len(model.student_model.operation_list)
        score = all_ops
        SCORE_PUNISHMENT = 1
        for op_s in model.student_model.operation_list:
            if not SyntacticCheck.is_lower_camel_case(op_s.name):
                score -= SCORE_PUNISHMENT
        total_score = score / all_ops if all_ops > 0 else 1.0
        criteria.score = total_score
        return criteria
    
    @staticmethod
    def evaluate_global_enum_names(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        all_enums = len(model.student_model.enum_list)
        score = all_enums
        SCORE_PUNISHMENT = 1
        for enum_s in model.student_model.enum_list:
            if not SyntacticCheck.is_upper_camel_case(enum_s.name):
                score -= SCORE_PUNISHMENT
        total_score = score / all_enums if all_enums > 0 else 1.0
        criteria.score = total_score
        return criteria
    
    @staticmethod
    def evaluate_global_enum_values(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        all_enum_values = sum(len(enum.values) for enum in model.student_model.enum_list)
        score = all_enum_values
        SCORE_PUNISHMENT = 1
        for enum in model.student_model.enum_list:
            for value in enum.values:
                if not SyntacticCheck.is_all_upper_case(value.name):
                    score -= SCORE_PUNISHMENT
        total_score = score / all_enum_values if all_enum_values > 0 else 1.0
        criteria.score = total_score
        return criteria