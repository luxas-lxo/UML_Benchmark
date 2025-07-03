from plantuml_eval.eval_model import EvalModel
from main_eval.eval_metrics import ScoringCriteria
from main_eval.eval_completeness import CompletenessEvaluator
class EvalHandler:
    @staticmethod
    def evaluate_criteria(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        if criteria.category == "Completeness":
            return EvalHandler.evaluate_completeness(criteria, model)
            
        elif criteria.category == "Syntactic Correctness":
            return EvalHandler.evaluate_syntactic_correctness(criteria, model)
            
        elif criteria.category == "Semantic Correctness":
            return EvalHandler.evaluate_semantic_correctness(criteria, model)
        
        else:   
            raise ValueError(f"Unknown criteria category: {criteria.category}")
    
    @staticmethod
    def evaluate_completeness(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        if criteria.id == "CPT1":
            return CompletenessEvaluator.evaluate_classes()
        elif criteria.id == "CPT2":
            return CompletenessEvaluator.evaluate_attributes()
        elif criteria.id == "CPT3":
            return CompletenessEvaluator.evaluate_operations()
        elif criteria.id == "CPT4":
            return CompletenessEvaluator.evaluate_relations()
        # NOTE: the folowing criteria are not implemented since they are bound to their respective relations and no matching method is implemented yet
        elif criteria.id == "CPT5":
            return CompletenessEvaluator.evaluate_multiplicities()
        elif criteria.id == "CPT6":
            return criteria
            #return CompletenessEvaluator.evaluate_relation_names()
        elif criteria.id == "CPT7":
            return criteria
            #return CompletenessEvaluator.evaluate_role_names()
        # NOTE: note end
        elif criteria.id == "CPT8":
            return CompletenessEvaluator.evaluate_enumerations()
        elif criteria.id == "CPT9":
            return CompletenessEvaluator.evaluate_enum_values()
        else:
            raise ValueError(f"Unknown completeness criteria id: {criteria.id}")
        
    @staticmethod
    def evaluate_syntactic_correctness(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        if criteria.id == "SYC1":
            return EvalHandler.evaluate_syntax_class_attributes()
        elif criteria.id == "SYC2":
            return EvalHandler.evaluate_syntax_class_operations()
        elif criteria.id == "SYC3":
            return EvalHandler.evaluate_syntax_simple_associations()
        elif criteria.id == "SYC4":
            return EvalHandler.evaluate_syntax_aggregation_relations()
        elif criteria.id == "SYC5":
            return EvalHandler.evaluate_syntax_composition_relations()
        elif criteria.id == "SYC6":
            return EvalHandler.evaluate_syntax_generalisation_relations()
        elif criteria.id == "SYC7":
            return EvalHandler.evaluate_syntax_relation_multiplicities()
        elif criteria.id == "SYC8":
            return EvalHandler.evaluate_syntax_roles()
        else:
            raise ValueError(f"Unknown syntactic correctness criteria id: {criteria.id}")
    
    @staticmethod
    def evaluate_semantic_correctness(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        if criteria.id == "SEC1":
            return EvalHandler.evaluate_semantics_class_names()
        elif criteria.id == "SEC2":
            return EvalHandler.evaluate_semantics_attribute_names()
        elif criteria.id == "SEC3":
            return EvalHandler.evaluate_semantics_operation_names()
        elif criteria.id == "SEC4":
            return EvalHandler.evaluate_semantics_relation_names()
        elif criteria.id == "SEC5":
            EvalHandler.evaluate_semantics_multiplicities()
        elif criteria.id == "SEC6":
            return EvalHandler.evaluate_semantics_role_names()
        elif criteria.id == "SEC7":
            return EvalHandler.evaluate_semantics_no_redundant_classes()
        elif criteria.id == "SEC8":
            return EvalHandler.evaluate_semantics_no_redundant_attributes()
        elif criteria.id == "SEC9":
            return EvalHandler.evaluate_semantics_no_redundant_operations()
        elif criteria.id == "SEC10":
            return EvalHandler.evaluate_semantics_no_redundant_relations()
        else:
            raise ValueError(f"Unknown semantic correctness criteria id: {criteria.id}")