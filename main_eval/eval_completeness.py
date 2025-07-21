from plantuml_eval.eval_model import EvalModel
from main_eval.eval_metrics import ScoringCriteria, NO_STATEMENT
from UML_model.uml_class import UMLVisibility, UMLDataType, UMLAttribute, UMLOperation
from UML_model.uml_relation import UMLRelationType
from tools.UML_parser import ERROR_FLAG

from typing import Dict
from itertools import chain

class CompletenessEvaluator:
    # NOTE: here we also consider elements that are missrepresented in the student model
    # e.g. a merged or split class
    # this is since the completeness does not check for semantics or syntax, just for existence
    @staticmethod
    def evaluate_classes(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        class_completeness_score: float = NO_STATEMENT
        if model.instructor_model.class_list:
            total_classes = len(model.instructor_model.class_list)
            class_completeness_score = (total_classes - len(model.temp_missing_classes)) / total_classes if total_classes > 0 else NO_STATEMENT
        criteria.score = class_completeness_score
        return criteria
    
    @staticmethod
    def evaluate_attributes(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        attribute_completeness_score: float = NO_STATEMENT
        if model.instructor_model.attribute_list:
            total_attributes = len(model.instructor_model.attribute_list)
            attribute_completeness_score = (total_attributes - len(model.missed_attr_list)) / total_attributes if total_attributes > 0 else NO_STATEMENT
        criteria.score = attribute_completeness_score
        return criteria

    @staticmethod
    def evaluate_att_visibility(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        visibility_completeness_score: float = NO_STATEMENT
        attributes_with_visibility = [att for att in model.instructor_model.attribute_list if att.visibility != UMLVisibility.UNKNOWN]
        att_with_vis_match_map: Dict[UMLAttribute, UMLAttribute] = {att_i: att_s for att_i, att_s in model.temp_all_att_matches.items() if att_i in attributes_with_visibility}
        if attributes_with_visibility:
            total_attributes = len(attributes_with_visibility)
            score: float = total_attributes
            for att_s in att_with_vis_match_map.values():
                if att_s.visibility == UMLVisibility.UNKNOWN:
                    score -= 1
            for att_i in model.missed_attr_list:
                if att_i.visibility != UMLVisibility.UNKNOWN:
                    score -= 1
            visibility_completeness_score = score / total_attributes if total_attributes > 0 else NO_STATEMENT
        criteria.score = visibility_completeness_score
        return criteria

    @staticmethod
    def evaluate_att_data_type(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        data_type_completeness_score: float = NO_STATEMENT
        attributes_with_data_type = [att for att in model.instructor_model.attribute_list if att.data_type != UMLDataType.UNKNOWN]
        att_with_data_type_match_map: Dict[UMLAttribute, UMLAttribute] = {att_i: att_s for att_i, att_s in model.temp_all_att_matches.items() if att_i in attributes_with_data_type}
        if attributes_with_data_type:
            total_attributes = len(attributes_with_data_type)
            score: float = total_attributes
            for att_s in att_with_data_type_match_map.values():
                if att_s.data_type == UMLDataType.UNKNOWN:
                    score -= 1
            for att_i in model.missed_attr_list:
                if att_i.data_type != UMLDataType.UNKNOWN:
                    score -= 1
            data_type_completeness_score = score / total_attributes if total_attributes > 0 else NO_STATEMENT
        criteria.score = data_type_completeness_score
        return criteria
    
    @staticmethod
    def evaluate_att_initial_value(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        initial_value_completeness_score: float = NO_STATEMENT
        attributes_with_initial_value = [att for att in model.instructor_model.attribute_list if att.initial != ""]
        att_with_initial_value_match_map: Dict[UMLAttribute, UMLAttribute] = {att_i: att_s for att_i, att_s in model.temp_all_att_matches.items() if att_i in attributes_with_initial_value}
        if attributes_with_initial_value:
            total_attributes = len(attributes_with_initial_value)
            score: float = total_attributes
            for att_s in att_with_initial_value_match_map.values():
                if att_s.initial == "":
                    score -= 1
            for att_i in model.missed_attr_list:
                if att_i.initial != "":
                    score -= 1
            initial_value_completeness_score = score / total_attributes if total_attributes > 0 else NO_STATEMENT
        criteria.score = initial_value_completeness_score
        return criteria
    
    @staticmethod
    def evaluate_operations(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        operation_completeness_score: float = NO_STATEMENT
        if model.instructor_model.operation_list:
            total_operations = len(model.instructor_model.operation_list)
            operation_completeness_score = (total_operations - len(model.missed_oper_list)) / total_operations if total_operations > 0 else NO_STATEMENT
        criteria.score = operation_completeness_score
        return criteria
    
    @staticmethod
    def evaluate_op_visibility(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        visibility_completeness_score: float = NO_STATEMENT
        operations_with_visibility = [op for op in model.instructor_model.operation_list if op.visibility != UMLVisibility.UNKNOWN]
        op_with_vis_match_map: Dict[UMLOperation, UMLOperation] = {op_i: op_s for op_i, op_s in model.temp_all_oper_matches.items() if op_i in operations_with_visibility}
        if operations_with_visibility:
            total_operations = len(operations_with_visibility)
            score: float = total_operations
            for op_s in op_with_vis_match_map.values():
                if op_s.visibility == UMLVisibility.UNKNOWN:
                    score -= 1
            for op_i in model.missed_oper_list:
                if op_i.visibility != UMLVisibility.UNKNOWN:
                    score -= 1
            visibility_completeness_score = score / total_operations if total_operations > 0 else NO_STATEMENT
        criteria.score = visibility_completeness_score
        return criteria
    
    @staticmethod
    def evaluate_op_parameters(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        parameter_completeness_score: float = NO_STATEMENT
        operations_with_parameters = [op for op in model.instructor_model.operation_list if op.params]
        op_with_param_match_map: Dict[UMLOperation, UMLOperation] = {op_i: op_s for op_i, op_s in model.temp_all_oper_matches.items() if op_i in operations_with_parameters}
        if operations_with_parameters:
            total_operations = len(operations_with_parameters)
            score: float = total_operations
            for op_s in op_with_param_match_map.values():
                if not op_s.params:
                    score -= 1
            for op_i in model.missed_oper_list:
                if op_i.params:
                    score -= 1
            parameter_completeness_score = score / total_operations if total_operations > 0 else NO_STATEMENT
        criteria.score = parameter_completeness_score
        return criteria
    
    @staticmethod
    def evaluate_op_return_types(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        return_type_completeness_score: float = NO_STATEMENT
        operations_with_return_types = [op for op in model.instructor_model.operation_list if op.return_types]
        op_with_return_type_match_map: Dict[UMLOperation, UMLOperation] = {op_i: op_s for op_i, op_s in model.temp_all_oper_matches.items() if op_i in operations_with_return_types}
        if operations_with_return_types:
            total_operations = len(operations_with_return_types)
            score: float = total_operations
            for op_s in op_with_return_type_match_map.values():
                if not op_s.return_types:
                    score -= 1
            for op_i in model.missed_oper_list:
                if op_i.return_types:
                    score -= 1
            return_type_completeness_score = score / total_operations if total_operations > 0 else NO_STATEMENT
        criteria.score = return_type_completeness_score
        return criteria

    @staticmethod
    def evaluate_enumerations(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        enumeration_completeness_score: float = NO_STATEMENT
        if model.instructor_model.enum_list:
            total_enumerations = len(model.instructor_model.enum_list)
            enumeration_completeness_score = (total_enumerations - len(model.missing_enums)) / total_enumerations if total_enumerations > 0 else NO_STATEMENT
        criteria.score = enumeration_completeness_score
        return criteria
    
    @staticmethod
    def evaluate_enum_values(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        enum_value_completeness_score: float = NO_STATEMENT
        if model.instructor_model.enum_list:
            total_values = len(model.instructor_model.value_list)
            enum_value_completeness_score = (total_values - len(model.missed_value_list)) / total_values if total_values > 0 else NO_STATEMENT
        criteria.score = enum_value_completeness_score
        return criteria
    
    @staticmethod
    def evaluate_relations(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        relation_completeness_score: float = 1.0
        if model.instructor_model.relation_list:
            total_relations = len(model.instructor_model.relation_list)
            relation_completeness_score = (total_relations - len(model.miss_relation_list_loose)) / total_relations if total_relations > 0 else NO_STATEMENT
        criteria.score = relation_completeness_score
        return criteria
    
    @staticmethod
    def evaluate_rel_multiplicity(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        # NOTE: we consider here only relations that were matched regularly; other relation matches are penalized since the content evaluation is unclear (e.g., secondary derived relations have 4 multiplicities instead of 2).
        # Additionally, there is no finite matching for secondary derived relations (e.g., there is no best match selection yet).
        relations_with_s_multiplicity = [rel for rel in model.instructor_model.relation_list if rel.s_multiplicity != "1"]
        relations_with_d_multiplicity = [rel for rel in model.instructor_model.relation_list if rel.d_multiplicity != "1"]
        relations_with_s_and_d_multiplicity = [rel for rel in model.instructor_model.relation_list if rel in relations_with_s_multiplicity and rel in relations_with_d_multiplicity]
        for rel in relations_with_s_and_d_multiplicity:
            relations_with_s_multiplicity.remove(rel)
            relations_with_d_multiplicity.remove(rel)
        rel_with_s_multiplicity_match_map: Dict[UMLRelationType, UMLRelationType] = {rel_i: rel_s for rel_i, rel_s in model.relation_match_map.items() if rel_i in relations_with_s_multiplicity}
        rel_with_d_multiplicity_match_map: Dict[UMLRelationType, UMLRelationType] = {rel_i: rel_s for rel_i, rel_s in model.relation_match_map.items() if rel_i in relations_with_d_multiplicity}
        rel_with_s_and_d_multiplicity_match_map: Dict[UMLRelationType, UMLRelationType] = {rel_i: rel_s for rel_i, rel_s in model.relation_match_map.items() if rel_i in relations_with_s_and_d_multiplicity}

        res_s: float = 0
        if relations_with_s_multiplicity:
            total_relations = len(relations_with_s_multiplicity)
            score: float = total_relations
            for rel_s in rel_with_s_multiplicity_match_map.values():
                if rel_s.s_multiplicity == "1":
                    score -= 1
            res_s = score
        
        res_d: float = 0
        if relations_with_d_multiplicity:
            total_relations = len(relations_with_d_multiplicity)
            score: float = total_relations
            for rel_s in rel_with_d_multiplicity_match_map.values():
                if rel_s.d_multiplicity == "1":
                    score -= 1
            res_d = score

        res_s_and_d: float = 0
        if relations_with_s_and_d_multiplicity:
            total_relations = len(relations_with_s_and_d_multiplicity)
            score: float = total_relations
            for rel_s in rel_with_s_and_d_multiplicity_match_map.values():
                if rel_s.s_multiplicity == "1" or rel_s.d_multiplicity == "1":
                    score -= 1
            res_s_and_d = score

        if rel_with_s_multiplicity_match_map or rel_with_d_multiplicity_match_map or rel_with_s_and_d_multiplicity_match_map:
            for rel_i in model.miss_relation_list:
                if rel_i.s_multiplicity != "1" or rel_i.d_multiplicity != "1":
                    score -= 1

        total_relations = len(relations_with_s_multiplicity) + len(relations_with_d_multiplicity) + len(relations_with_s_and_d_multiplicity)
        multiplicity_completeness_score: float = (res_s + res_d + res_s_and_d) / total_relations if total_relations > 0 else NO_STATEMENT
        criteria.score = multiplicity_completeness_score
        return criteria
    
    @staticmethod
    def evaluate_rel_description(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        description_completeness_score: float = NO_STATEMENT
        relations_with_description = [rel for rel in model.instructor_model.relation_list if rel.description != ""]
        rel_with_description_match_map: Dict[UMLRelationType, UMLRelationType] = {rel_i: rel_s for rel_i, rel_s in model.relation_match_map.items() if rel_i in relations_with_description}
        if relations_with_description:
            total_relations = len(relations_with_description)
            score: float = total_relations
            for rel_s in rel_with_description_match_map.values():
                if rel_s.description == "":
                    score -= 1
            for rel_i in model.miss_relation_list:
                if rel_i.description != "":
                    score -= 1
            description_completeness_score = score / total_relations if total_relations > 0 else NO_STATEMENT
        criteria.score = description_completeness_score
        return criteria
    
    @staticmethod
    def evaluate_relations_with_type(criteria: ScoringCriteria, model: EvalModel, rel_type: UMLRelationType) -> ScoringCriteria:
        relation_type_completeness_score: float = NO_STATEMENT
        relations_with_type = [rel for rel in model.instructor_model.relation_list if rel.type == rel_type]
        missing_relations_with_type = [rel for rel in model.miss_relation_list_loose if rel.type == rel_type]
        if relations_with_type:
            total_relations = len(relations_with_type)
            relation_type_completeness_score = (total_relations - len(missing_relations_with_type)) / total_relations if total_relations > 0 else NO_STATEMENT
        criteria.score = relation_type_completeness_score
        return criteria

    