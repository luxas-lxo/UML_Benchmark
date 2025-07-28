from plantuml_eval.eval_model import EvalModel
from main_eval.eval_metrics import ScoringCriteria, NO_STATEMENT
from UML_model.uml_relation import UMLRelationType, UMLRelation
from UML_model.uml_class import UMLDataType, UMLVisibility
from tools.syntactic_check import SyntacticCheck
from tools.UML_parser import ERROR_FLAG

from itertools import chain
from typing import Dict

class SyntaxEvaluator:
    @staticmethod
    def evaluate_classes(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        class_syntax_score: float = NO_STATEMENT
        all_matched_classes = (
            set(model.class_match_map.values())
            | {cls for classes in model.split_class_map.values() for cls in classes}
            | set(model.merge_class_map.values())
        )
        if all_matched_classes:
            total_classes = len(all_matched_classes)
            syntax_score = total_classes
            for cls_s in all_matched_classes:
                if cls_s.name == ERROR_FLAG:
                    syntax_score -= 1
            class_syntax_score = syntax_score / total_classes if total_classes > 0 else NO_STATEMENT
        criteria.score = class_syntax_score
        return criteria
    
    @staticmethod
    def evaluate_classes_global(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        class_syntax_score: float = NO_STATEMENT
        if model.student_model.class_list:
            total_classes = len(model.student_model.class_list)
            syntax_score = total_classes
            for cls_s in model.student_model.class_list:
                if not SyntacticCheck.is_upper_camel_case(cls_s.name):
                    syntax_score -= 1
            class_syntax_score = syntax_score / total_classes if total_classes > 0 else NO_STATEMENT
        criteria.score = class_syntax_score
        return criteria
    
    @staticmethod
    def evaluate_attributes(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        attribute_syntax_score: float = NO_STATEMENT
        if model.temp_all_att_matches:
            total_attributes = len(model.temp_all_att_matches)
            syntax_score = total_attributes
            for attr_s in model.temp_all_att_matches.values():
                if attr_s.name == ERROR_FLAG or attr_s.visibility == UMLVisibility.ERROR or attr_s.data_type == UMLDataType.ERROR or attr_s.initial == ERROR_FLAG:
                    syntax_score -= 1
            attribute_syntax_score = syntax_score / total_attributes if total_attributes > 0 else NO_STATEMENT
        criteria.score = attribute_syntax_score
        return criteria
    
    @staticmethod
    def evaluate_attributes_global(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        attribute_syntax_score: float = NO_STATEMENT
        if model.student_model.attribute_list:
            total_attributes = len(model.student_model.attribute_list)
            syntax_score = total_attributes
            for attr_s in model.student_model.attribute_list:
                if attr_s.name == ERROR_FLAG or attr_s.visibility == UMLVisibility.ERROR or attr_s.data_type == UMLDataType.ERROR or attr_s.initial == ERROR_FLAG:
                    syntax_score -= 1
            attribute_syntax_score = syntax_score / total_attributes if total_attributes > 0 else NO_STATEMENT
        criteria.score = attribute_syntax_score
        return criteria
    
    @staticmethod
    def evaluate_att_name(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        att_name_syntax_score: float = NO_STATEMENT
        if model.temp_all_att_matches:
            total_attributes = len(model.temp_all_att_matches)
            syntax_score = total_attributes
            for attr_s in model.temp_all_att_matches.values():
                if attr_s.name == ERROR_FLAG:
                    syntax_score -= 1
            att_name_syntax_score = syntax_score / total_attributes if total_attributes > 0 else NO_STATEMENT
        criteria.score = att_name_syntax_score
        return criteria
    
    @staticmethod
    def evaluate_att_name_global(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        att_name_syntax_score: float = NO_STATEMENT
        if model.student_model.attribute_list:
            total_attributes = len(model.student_model.attribute_list)
            syntax_score = total_attributes
            for attr_s in model.student_model.attribute_list:
                if attr_s.name == ERROR_FLAG:
                    syntax_score -= 1
            att_name_syntax_score = syntax_score / total_attributes if total_attributes > 0 else NO_STATEMENT
        criteria.score = att_name_syntax_score
        return criteria
    
    @staticmethod
    def evaluate_att_visibility(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        att_visibility_syntax_score: float = NO_STATEMENT
        if model.temp_all_att_matches:
            total_attributes = len(model.temp_all_att_matches)
            syntax_score = total_attributes
            for attr_s in model.temp_all_att_matches.values():
                if attr_s.visibility == UMLVisibility.ERROR:
                    syntax_score -= 1
            att_visibility_syntax_score = syntax_score / total_attributes if total_attributes > 0 else NO_STATEMENT
        criteria.score = att_visibility_syntax_score
        return criteria
    
    @staticmethod
    def evaluate_att_visibility_global(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        att_visibility_syntax_score: float = NO_STATEMENT
        if model.student_model.attribute_list:
            total_attributes = len(model.student_model.attribute_list)
            syntax_score = total_attributes
            for attr_s in model.student_model.attribute_list:
                if attr_s.visibility == UMLVisibility.ERROR:
                    syntax_score -= 1
            att_visibility_syntax_score = syntax_score / total_attributes if total_attributes > 0 else NO_STATEMENT
        criteria.score = att_visibility_syntax_score
        return criteria
    
    @staticmethod
    def evaluate_att_multiplicity(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        att_multiplicity_syntax_score: float = NO_STATEMENT
        if model.temp_all_att_matches:
            total_attributes = len(model.temp_all_att_matches)
            syntax_score = total_attributes
            for attr_s in model.temp_all_att_matches.values():
                if attr_s.multiplicity == ERROR_FLAG:
                    syntax_score -= 1
            att_multiplicity_syntax_score = syntax_score / total_attributes if total_attributes > 0 else NO_STATEMENT
        criteria.score = att_multiplicity_syntax_score
        return criteria
    
    @staticmethod
    def evaluate_att_multiplicity_global(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        att_multiplicity_syntax_score: float = NO_STATEMENT
        if model.student_model.attribute_list:
            total_attributes = len(model.student_model.attribute_list)
            syntax_score = total_attributes
            for attr_s in model.student_model.attribute_list:
                if attr_s.multiplicity == ERROR_FLAG:
                    syntax_score -= 1
            att_multiplicity_syntax_score = syntax_score / total_attributes if total_attributes > 0 else NO_STATEMENT
        criteria.score = att_multiplicity_syntax_score
        return criteria
    
    @staticmethod
    def evaluate_att_data_type(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        att_data_type_syntax_score: float = NO_STATEMENT
        if model.temp_all_att_matches:
            total_attributes = len(model.temp_all_att_matches)
            syntax_score = total_attributes
            for attr_s in model.temp_all_att_matches.values():
                if attr_s.data_type == UMLDataType.ERROR:
                    syntax_score -= 1
            att_data_type_syntax_score = syntax_score / total_attributes if total_attributes > 0 else NO_STATEMENT
        criteria.score = att_data_type_syntax_score
        return criteria
    
    @staticmethod
    def evaluate_att_data_type_global(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        att_data_type_syntax_score: float = NO_STATEMENT
        if model.student_model.attribute_list:
            total_attributes = len(model.student_model.attribute_list)
            syntax_score = total_attributes
            for attr_s in model.student_model.attribute_list:
                if attr_s.data_type == UMLDataType.ERROR:
                    syntax_score -= 1
            att_data_type_syntax_score = syntax_score / total_attributes if total_attributes > 0 else NO_STATEMENT
        criteria.score = att_data_type_syntax_score
        return criteria

    @staticmethod
    def evaluate_att_initial_value(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        att_initial_value_syntax_score: float = NO_STATEMENT
        if model.temp_all_att_matches:
            total_attributes = len(model.temp_all_att_matches)
            syntax_score = total_attributes
            for attr_s in model.temp_all_att_matches.values():
                if attr_s.initial == ERROR_FLAG:
                    syntax_score -= 1
            att_initial_value_syntax_score = syntax_score / total_attributes if total_attributes > 0 else NO_STATEMENT
        criteria.score = att_initial_value_syntax_score
        return criteria
    
    @staticmethod
    def evaluate_att_initial_value_global(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        att_initial_value_syntax_score: float = NO_STATEMENT
        if model.student_model.attribute_list:
            total_attributes = len(model.student_model.attribute_list)
            syntax_score = total_attributes
            for attr_s in model.student_model.attribute_list:
                if attr_s.initial == ERROR_FLAG:
                    syntax_score -= 1
            att_initial_value_syntax_score = syntax_score / total_attributes if total_attributes > 0 else NO_STATEMENT
        criteria.score = att_initial_value_syntax_score
        return criteria
    
    @staticmethod
    def evaluate_operations(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        operation_syntax_score: float = NO_STATEMENT
        if model.temp_all_oper_matches:
            total_operations = len(model.temp_all_oper_matches)
            syntax_score = total_operations
            for op_s in model.temp_all_oper_matches.values():
                if op_s.visibility == UMLVisibility.ERROR or any(v == UMLDataType.ERROR for v in op_s.params.values()) or any(t == UMLDataType.ERROR for t in op_s.return_types) or op_s.name == ERROR_FLAG:
                    syntax_score -= 1
            operation_syntax_score = syntax_score / total_operations if total_operations > 0 else NO_STATEMENT
        criteria.score = operation_syntax_score
        return criteria
    
    @staticmethod
    def evaluate_operations_global(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        operation_syntax_score: float = NO_STATEMENT
        if model.student_model.operation_list:
            total_operations = len(model.student_model.operation_list)
            syntax_score = total_operations
            for op_s in model.student_model.operation_list:
                if op_s.visibility == UMLVisibility.ERROR or any(v == UMLDataType.ERROR for v in op_s.params.values()) or any(p == ERROR_FLAG for p in op_s.params.keys()) or any(t == UMLDataType.ERROR for t in op_s.return_types) or op_s.name == ERROR_FLAG:
                    syntax_score -= 1
            operation_syntax_score = syntax_score / total_operations if total_operations > 0 else NO_STATEMENT
        criteria.score = operation_syntax_score
        return criteria
    
    @staticmethod
    def evaluate_op_name(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        op_name_syntax_score: float = NO_STATEMENT
        if model.temp_all_oper_matches:
            total_operations = len(model.temp_all_oper_matches)
            syntax_score = total_operations
            for op_s in model.temp_all_oper_matches.values():
                if op_s.name == ERROR_FLAG:
                    syntax_score -= 1
            op_name_syntax_score = syntax_score / total_operations if total_operations > 0 else NO_STATEMENT
        criteria.score = op_name_syntax_score
        return criteria
    
    @staticmethod
    def evaluate_op_name_global(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        op_name_syntax_score: float = NO_STATEMENT
        if model.student_model.operation_list:
            total_operations = len(model.student_model.operation_list)
            syntax_score = total_operations
            for op_s in model.student_model.operation_list:
                if op_s.name == ERROR_FLAG:
                    syntax_score -= 1
            op_name_syntax_score = syntax_score / total_operations if total_operations > 0 else NO_STATEMENT
        criteria.score = op_name_syntax_score
        return criteria
    
    @staticmethod
    def evaluate_op_visibility(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        op_visibility_syntax_score: float = NO_STATEMENT
        if model.temp_all_oper_matches:
            total_operations = len(model.temp_all_oper_matches)
            syntax_score = total_operations
            for op_s in model.temp_all_oper_matches.values():
                if op_s.visibility == UMLVisibility.ERROR:
                    syntax_score -= 1
            op_visibility_syntax_score = syntax_score / total_operations if total_operations > 0 else NO_STATEMENT
        criteria.score = op_visibility_syntax_score
        return criteria
    
    @staticmethod
    def evaluate_op_visibility_global(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        op_visibility_syntax_score: float = NO_STATEMENT
        if model.student_model.operation_list:
            total_operations = len(model.student_model.operation_list)
            syntax_score = total_operations
            for op_s in model.student_model.operation_list:
                if op_s.visibility == UMLVisibility.ERROR:
                    syntax_score -= 1
            op_visibility_syntax_score = syntax_score / total_operations if total_operations > 0 else NO_STATEMENT
        criteria.score = op_visibility_syntax_score
        return criteria
    
    @staticmethod
    def evaluate_op_parameters(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        op_parameters_syntax_score: float = NO_STATEMENT
        if model.temp_all_oper_matches:
            total_operations = len(model.temp_all_oper_matches)
            syntax_score = total_operations
            for op_s in model.temp_all_oper_matches.values():
                if any(v == UMLDataType.ERROR for v in op_s.params.values()) or any(p == ERROR_FLAG for p in op_s.params.keys()):
                    syntax_score -= 1
            op_parameters_syntax_score = syntax_score / total_operations if total_operations > 0 else NO_STATEMENT
        criteria.score = op_parameters_syntax_score
        return criteria
    
    @staticmethod
    def evaluate_op_parameters_global(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        op_parameters_syntax_score: float = NO_STATEMENT
        if model.student_model.operation_list:
            total_operations = len(model.student_model.operation_list)
            syntax_score = total_operations
            for op_s in model.student_model.operation_list:
                if any(v == UMLDataType.ERROR for v in op_s.params.values()) or any(p == ERROR_FLAG for p in op_s.params.keys()):
                    syntax_score -= 1
            op_parameters_syntax_score = syntax_score / total_operations if total_operations > 0 else NO_STATEMENT
        criteria.score = op_parameters_syntax_score
        return criteria
    
    @staticmethod
    def evaluate_op_return_types(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        op_return_types_syntax_score: float = NO_STATEMENT
        if model.temp_all_oper_matches:
            total_operations = len(model.temp_all_oper_matches)
            syntax_score = total_operations
            for op_s in model.temp_all_oper_matches.values():
                if any(t == UMLDataType.ERROR for t in op_s.return_types):
                    syntax_score -= 1
            op_return_types_syntax_score = syntax_score / total_operations if total_operations > 0 else NO_STATEMENT
        criteria.score = op_return_types_syntax_score
        return criteria
    
    @staticmethod
    def evaluate_op_return_types_global(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        op_return_types_syntax_score: float = NO_STATEMENT
        if model.student_model.operation_list:
            total_operations = len(model.student_model.operation_list)
            syntax_score = total_operations
            for op_s in model.student_model.operation_list:
                if any(t == UMLDataType.ERROR for t in op_s.return_types):
                    syntax_score -= 1
            op_return_types_syntax_score = syntax_score / total_operations if total_operations > 0 else NO_STATEMENT
        criteria.score = op_return_types_syntax_score
        return criteria
    
    @staticmethod
    def evaluate_enumerations(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        enum_syntax_score: float = NO_STATEMENT
        if model.enum_match_map:
            total_enums = len(model.enum_match_map)
            syntax_score = total_enums
            for enu_s in model.enum_match_map.values():
                if enu_s.name == ERROR_FLAG:
                    syntax_score -= 1
            enum_syntax_score = syntax_score / total_enums if total_enums > 0 else NO_STATEMENT
        criteria.score = enum_syntax_score
        return criteria
    
    @staticmethod
    def evaluate_enumerations_global(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        enum_syntax_score: float = NO_STATEMENT
        if model.student_model.enum_list:
            total_enums = len(model.student_model.enum_list)
            syntax_score = total_enums
            for enu_s in model.student_model.enum_list:
                if enu_s.name == ERROR_FLAG:
                    syntax_score -= 1
            enum_syntax_score = syntax_score / total_enums if total_enums > 0 else NO_STATEMENT
        criteria.score = enum_syntax_score
        return criteria
    
    @staticmethod
    def evaluate_enum_values(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        enum_value_syntax_score: float = NO_STATEMENT
        if model.temp_all_value_matches:
            total_enum_values = len(model.temp_all_value_matches)
            syntax_score = total_enum_values
            for value_s in model.temp_all_value_matches.values():
                if value_s.name == ERROR_FLAG:
                    syntax_score -= 1
            enum_value_syntax_score = syntax_score / total_enum_values if total_enum_values > 0 else NO_STATEMENT
        criteria.score = enum_value_syntax_score
        return criteria
    
    @staticmethod
    def evaluate_enum_values_global(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        enum_value_syntax_score: float = NO_STATEMENT
        if model.student_model.value_list:
            total_enum_values = len(model.student_model.value_list)
            syntax_score = total_enum_values
            for value_s in model.student_model.value_list:
                if value_s.name == ERROR_FLAG:
                    syntax_score -= 1
            enum_value_syntax_score = syntax_score / total_enum_values if total_enum_values > 0 else NO_STATEMENT
        criteria.score = enum_value_syntax_score
        return criteria
    
    @staticmethod
    def evaluate_relations(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        # NOTE: we consider here only relations that were matched regularly; other relation matches are ignored for this check since there is no finite matching for sec degree derived relations, alternative asso link.
        # but they are considered in the global evaluation
        # NOTE: could be extended to a check for source and destination names
        # not implemented in the PlantUML parser yet
        # additionally we penalize relations with unknown type, e.g. the type could be a valid plantuml relation type but not one we support
        # could also be changed later
        relation_syntax_score: float = NO_STATEMENT
        if model.relation_match_map:
            total_relations = len(model.relation_match_map)
            syntax_score = total_relations
            for rel_s in model.relation_match_map.values():
                if rel_s.type == UMLRelationType.UNKNOWN or rel_s.s_multiplicity == ERROR_FLAG or rel_s.d_multiplicity == ERROR_FLAG or rel_s.description == ERROR_FLAG:
                    syntax_score -= 1
            relation_syntax_score = syntax_score / total_relations if total_relations > 0 else NO_STATEMENT
        criteria.score = relation_syntax_score
        return criteria
    
    @staticmethod
    def evaluate_relations_global(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        relation_syntax_score: float = NO_STATEMENT
        if model.student_model.relation_list:
            total_relations = len(model.student_model.relation_list)
            syntax_score = total_relations
            for rel_s in model.student_model.relation_list:
                if rel_s.type == UMLRelationType.UNKNOWN or rel_s.s_multiplicity == ERROR_FLAG or rel_s.d_multiplicity == ERROR_FLAG or rel_s.description == ERROR_FLAG:
                    syntax_score -= 1
            relation_syntax_score = syntax_score / total_relations if total_relations > 0 else NO_STATEMENT
        criteria.score = relation_syntax_score
        return criteria
    
    @staticmethod
    def evaluate_rel_type(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        # NOTE: we consider here only relations that were matched regularly; other relation matches are ignored for this check since there is no finite matching for sec degree derived relations, alternative asso link.
        # but they are considered in the global evaluation
        rel_type_syntax_score: float = NO_STATEMENT
        if model.relation_match_map:
            total_relations = len(model.relation_match_map)
            syntax_score = total_relations
            for rel_s in model.relation_match_map.values():
                if rel_s.type == UMLRelationType.UNKNOWN:
                    syntax_score -= 1
            rel_type_syntax_score = syntax_score / total_relations if total_relations > 0 else NO_STATEMENT
        criteria.score = rel_type_syntax_score
        return criteria
    
    @staticmethod
    def evaluate_rel_type_global(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        rel_type_syntax_score: float = NO_STATEMENT
        if model.student_model.relation_list:
            total_relations = len(model.student_model.relation_list)
            syntax_score = total_relations
            for rel_s in model.student_model.relation_list:
                if rel_s.type == UMLRelationType.UNKNOWN:
                    syntax_score -= 1
            rel_type_syntax_score = syntax_score / total_relations if total_relations > 0 else NO_STATEMENT
        criteria.score = rel_type_syntax_score
        return criteria
    
    @staticmethod
    def evaluate_rel_multiplicity(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        # NOTE: we consider here only relations that were matched regularly; other relation matches are ignored for this check since there is no finite matching for sec degree derived relations, alternative asso link.
        # but they are considered in the global evaluation
        rel_multiplicity_syntax_score: float = NO_STATEMENT
        if model.relation_match_map:
            total_relations = len(model.relation_match_map)
            syntax_score = total_relations
            for rel_s in model.relation_match_map.values():
                if rel_s.s_multiplicity == ERROR_FLAG or rel_s.d_multiplicity == ERROR_FLAG:
                    syntax_score -= 1
            rel_multiplicity_syntax_score = syntax_score / total_relations if total_relations > 0 else NO_STATEMENT
        criteria.score = rel_multiplicity_syntax_score
        return criteria
    
    @staticmethod
    def evaluate_rel_multiplicity_global(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        rel_multiplicity_syntax_score: float = NO_STATEMENT
        if model.student_model.relation_list:
            total_relations = len(model.student_model.relation_list)
            syntax_score = total_relations
            for rel_s in model.student_model.relation_list:
                if rel_s.s_multiplicity == ERROR_FLAG or rel_s.d_multiplicity == ERROR_FLAG:
                    syntax_score -= 1
            rel_multiplicity_syntax_score = syntax_score / total_relations if total_relations > 0 else NO_STATEMENT
        criteria.score = rel_multiplicity_syntax_score
        return criteria
    
    @staticmethod
    def evaluate_rel_description(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        # NOTE: we consider here only relations that were matched regularly; other relation matches are ignored for this check since there is no finite matching for sec degree derived relations, alternative asso link.
        # but they are considered in the global evaluation
        rel_description_syntax_score: float = NO_STATEMENT
        if model.relation_match_map:
            total_relations = len(model.relation_match_map)
            syntax_score = total_relations
            for rel_s in model.relation_match_map.values():
                if rel_s.description == ERROR_FLAG:
                    syntax_score -= 1
            rel_description_syntax_score = syntax_score / total_relations if total_relations > 0 else NO_STATEMENT
        criteria.score = rel_description_syntax_score
        return criteria
    
    @staticmethod
    def evaluate_rel_description_global(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        rel_description_syntax_score: float = NO_STATEMENT
        if model.student_model.relation_list:
            total_relations = len(model.student_model.relation_list)
            syntax_score = total_relations
            for rel_s in model.student_model.relation_list:
                if rel_s.description == ERROR_FLAG:
                    syntax_score -= 1
            rel_description_syntax_score = syntax_score / total_relations if total_relations > 0 else NO_STATEMENT
        criteria.score = rel_description_syntax_score
        return criteria
    
    @staticmethod
    def evaluate_relations_with_type(criteria: ScoringCriteria, model: EvalModel, rel_type: UMLRelationType) -> ScoringCriteria:
        # NOTE: for the association link relations this check is not important since they are not matched in the same way as the other relations
        # the check there will be always NO_STATEMENT or 1.0 since the syntactic errors cannot occur in the parsing
        # could be added later if needed
        rel_syntax_score: float = NO_STATEMENT
        rel_match_map_with_type: Dict[UMLRelation, UMLRelation] = {rel_i: rel_s for rel_i, rel_s in model.relation_match_map.items() if rel_i.type == rel_type}
        if rel_match_map_with_type:
            total_relations = len(rel_match_map_with_type)
            syntax_score = total_relations
            for rel_s in rel_match_map_with_type.values():
                if rel_s.type == UMLRelationType.UNKNOWN or rel_s.s_multiplicity == ERROR_FLAG or rel_s.d_multiplicity == ERROR_FLAG or rel_s.description == ERROR_FLAG:
                    syntax_score -= 1
            rel_syntax_score = syntax_score / total_relations if total_relations > 0 else NO_STATEMENT
        criteria.score = rel_syntax_score
        return criteria
    
    @staticmethod
    def evaluate_relations_with_type_global(criteria: ScoringCriteria, model: EvalModel, rel_type: UMLRelationType) -> ScoringCriteria:
        # NOTE: for the association link relations this check is not important since they are not matched in the same way as the other relations
        # the check there will be always NO_STATEMENT or 1.0 since the syntactic errors cannot occur in the parsing
        # could be added later if needed
        rel_syntax_score: float = NO_STATEMENT
        rel_list_with_type = [rel_s for rel_s in model.student_model.relation_list if rel_s.type == rel_type]
        if rel_list_with_type:
            total_relations = len(rel_list_with_type)
            syntax_score = total_relations
            for rel_s in rel_list_with_type:
                if rel_s.s_multiplicity == ERROR_FLAG or rel_s.d_multiplicity == ERROR_FLAG or rel_s.description == ERROR_FLAG:
                    syntax_score -= 1
            rel_syntax_score = syntax_score / total_relations if total_relations > 0 else NO_STATEMENT
        criteria.score = rel_syntax_score
        return criteria