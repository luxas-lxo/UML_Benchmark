from plantuml_eval.eval_model import EvalModel
from main_eval.eval_metrics import ScoringCriteria
from UML_model.uml_relation import UMLRelationType
from tools.UML_parser import ERROR_FLAG

class CompletenessEvaluator:
    @staticmethod
    def evaluate_classes(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        # NOTE: here we also consider classes that are missrepresented in the student model
        # e.g. a merged or split class
        # this is since the completeness does not check for semantics or syntax, just for existence
        class_completeness_score: float = 1.0
        if model.instructor_model.class_list:
            class_completeness_score = (len(model.instructor_model.class_list) - len(model.temp_missing_classes)) / len(model.instructor_model.class_list)
        criteria.score = class_completeness_score
        return criteria
    
    @staticmethod
    def evaluate_attributes(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        attribute_completeness_score: float = 1.0
        if model.instructor_model.class_list:
            total_attributes = sum(len(cls.attributes) for cls in model.instructor_model.class_list)
            attribute_completeness_score = (len(model.attr_match_map) + len(model.misplaced_attr_map)) / total_attributes if total_attributes > 0 else 1.0
        criteria.score = attribute_completeness_score
        return criteria
    
    @staticmethod
    def evaluate_operations(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        operation_completeness_score: float = 1.0
        if model.instructor_model.class_list:
            total_operations = sum(len(cls.operations) for cls in model.instructor_model.class_list)
            operation_completeness_score = (len(model.oper_matched_map) + len(model.misplaced_oper_map)) / total_operations if total_operations > 0 else 1.0
        criteria.score = operation_completeness_score
        return criteria
    
    @staticmethod
    def evaluate_relations(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        # NOTE: same as for classes, we consider relations that are missrepresented in the student model
        # e.g. a faslse representation of an association link or associations through not mapped classes
        relation_completeness_score: float = 1.0
        if model.instructor_model.relation_list:
            relation_completeness_score = (len(model.instructor_model.relation_list) - len(model.miss_relation_list)) / len(model.instructor_model.relation_list)
        criteria.score = relation_completeness_score
        return criteria
    
    @staticmethod
    def evaluate_multiplicities(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        # NOTE: This criterion evaluates multiplicities only for relations that have already been mapped (a true match not a) between the instructor and student models.
        # Evaluating all relations regardless of mapping would make this metric overlap with the general relation completeness metric (evaluate_relations)
        # and could distort the completeness calculation, as unmapped relations are already penalized in the relation completeness score.
        # Therefore, multiplicity completeness is assessed only for those relations that are matched, ensuring a clear separation of concerns.
        # NOTE: I think this test is not necessary since the parsing of multiplicities from PlantUML already ensures that every relation has 2 multiplicities.
        # so the test for existence is irrelevant
        multiplicity_completeness_score: float = 1.0
        if model.relation_match_map:
            inst_rel_without_asso_link = [relation for relation in model.relation_match_map.keys() if relation.type != UMLRelationType.ASSOCIATION_LINK]
            stud_rel_without_asso_link = [relation for relation in model.relation_match_map.values() if relation.type != UMLRelationType.ASSOCIATION_LINK]
            total_inst_multiplicities = len(inst_rel_without_asso_link) * 2
            matched_stud_multiplicities = sum(
                (relation.s_multiplicity != "") +
                (relation.d_multiplicity != "")
                for relation in stud_rel_without_asso_link
            )
            multiplicity_completeness_score = matched_stud_multiplicities / total_inst_multiplicities if total_inst_multiplicities > 0 else 1.0
        criteria.score = multiplicity_completeness_score
        return criteria
    
    @staticmethod
    def evaluate_relation_names(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        relation_name_completeness_score: float = 1.0
        if model.instructor_model.relation_list:
            total_relations_with_names = len([rel for rel in model.relation_match_map.keys() if rel.description != "" and rel.description != ERROR_FLAG])
            matched_relations_with_names = len([rel for rel in model.relation_match_map.values() if rel.description != "" and rel.description != ERROR_FLAG])
            relation_name_completeness_score = matched_relations_with_names / total_relations_with_names if total_relations_with_names > 0 else 1.0
        criteria.score = relation_name_completeness_score
        return criteria
    
    @staticmethod
    def evaluate_role_names(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        # NOTE: role names are not implemented in the PlantUML parser, so this method is a placeholder.
        criteria.score = 1.0
        return criteria 

    @staticmethod
    def evaluate_enumerations(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        enumeration_completeness_score: float = 1.0
        if model.instructor_model.enum_list:
            enumeration_completeness_score = len(model.enum_match_map) / len(model.instructor_model.enum_list)
        criteria.score = enumeration_completeness_score
        return criteria
    
    @staticmethod
    def evaluate_enum_values(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        enum_value_completeness_score: float = 1.0
        if model.instructor_model.enum_list:
            total_values = sum(len(enum.values) for enum in model.instructor_model.enum_list)
            enum_value_completeness_score = (len(model.value_match_map) + len(model.misplaced_value_map)) / total_values if total_values > 0 else 1.0
        criteria.score = enum_value_completeness_score
        return criteria