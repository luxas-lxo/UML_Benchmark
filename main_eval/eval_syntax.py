from plantuml_eval.eval_model import EvalModel
from main_eval.eval_metrics import ScoringCriteria
from UML_model.uml_relation import UMLRelationType
from UML_model.uml_class import UMLDataType, UMLVisibility
from tools.syntactic_check import SyntacticCheck

from itertools import chain

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
            if not SyntacticCheck.is_upper_camel_case(cls_s.name):
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
        SCORE_PUNISHMENT = 1/2
        for cls_s in model.student_model.class_list:
            name_s = cls_s.name.lower().strip()
            if name_s in seen:
                duplicated_class_names.add(name_s)
            else:
                seen.add(name_s)
            if not SyntacticCheck.is_upper_camel_case(cls_s.name):
                score -= SCORE_PUNISHMENT
            if name_s in duplicated_class_names:
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
            if att_i.data_type not in (UMLDataType.UNKNOWN, UMLDataType.ERROR) and att_s.data_type in (UMLDataType.UNKNOWN, UMLDataType.ERROR):
                total_score -= SCORE_PUNISHMENT
            if att_i.visibility not in (UMLVisibility.UNKNOWN, UMLVisibility.ERROR) and att_s.visibility in (UMLVisibility.UNKNOWN, UMLVisibility.ERROR):
                total_score -= SCORE_PUNISHMENT
            if att_i.initial not in ("--error--", "") and  att_s.initial in ("--error--", ""):
                total_score -= SCORE_PUNISHMENT
            if not SyntacticCheck.is_lower_camel_case(att_s.name):
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
        SCORE_PUNISHMENT = 1/4
        for att_s in model.student_model.attribute_list:
            if att_s.initial == "--error--":
                score -= SCORE_PUNISHMENT
            if att_s.visibility == UMLVisibility.ERROR:
                score -= SCORE_PUNISHMENT
            if att_s.data_type == UMLDataType.ERROR:
                score -= SCORE_PUNISHMENT
            if not SyntacticCheck.is_lower_camel_case(att_s.name):
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
            if op_i.visibility not in (UMLVisibility.UNKNOWN, UMLVisibility.ERROR) and op_s.visibility in (UMLVisibility.UNKNOWN, UMLVisibility.ERROR):
                total_score -= SCORE_PUNISHMENT
            if op_i.params and (not op_s.params or any(v == UMLDataType.ERROR for v in op_s.params.values())):
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
            if op_i.return_types and (not op_s.return_types or any(t == UMLDataType.ERROR for t in op_s.return_types) or len(op_s.return_types) < len(op_i.return_types)):
                total_score -= SCORE_PUNISHMENT
            if not SyntacticCheck.is_lower_camel_case(op_s.name):
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
        SCORE_PUNISHMENT = 1/4
        for op_s in model.student_model.operation_list:
            if op_s.visibility == UMLVisibility.ERROR:
                score -= SCORE_PUNISHMENT
            if any(v == UMLDataType.ERROR for v in op_s.params.values()):
                score -= SCORE_PUNISHMENT
            if any(t == UMLDataType.ERROR for t in op_s.return_types):
                score -= SCORE_PUNISHMENT
            if not SyntacticCheck.is_lower_camel_case(op_s.name):
                score -= SCORE_PUNISHMENT
        total_score = score / all_ops if all_ops > 0 else 1.0
        criteria.score = total_score
        return criteria
    
    @staticmethod
    def evaluate_simple_associations(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        pass
    
    @staticmethod
    def evaluate_aggregations(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        pass
    
    @staticmethod
    def evaluate_compositions(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        pass
    
    @staticmethod
    def evaluate_generalizations(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        pass
    
    @staticmethod
    def evaluate_multiplicities(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        pass
    
    @staticmethod
    def evaluate_roles(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        # NOTE: role names are not implemented in the PlantUML parser, so this method is a placeholder.
        return criteria
    
    @staticmethod
    def evaluate_association_classes(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        pass

    @staticmethod
    def evaluate_enumerations(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        pass

    @staticmethod
    def evaluate_enum_values(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        pass