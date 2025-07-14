from plantuml_eval.eval_model import EvalModel
from main_eval.eval_metrics import ScoringCriteria, ScoringScheme
from main_eval.eval_completeness import CompletenessEvaluator
from UML_model.uml_relation import UMLRelationType
from main_eval.eval_syntax import SyntaxEvaluator

from typing import List
class EvalHandler:
    def __init__(self, model: EvalModel):
        scheme = ScoringScheme()
        self.cpt_criteria: List[ScoringCriteria] = []
        self.syc_criteria: List[ScoringCriteria] = []
        self.sec_criteria: List[ScoringCriteria] = []
        for cpt in scheme.completeness_criteria:
            res = EvalHandler.evaluate_criteria(cpt, model)
            if res is not None:
                self.cpt_criteria.append(res)
        for syc in scheme.syntax_criteria:
            res = EvalHandler.evaluate_criteria(syc, model)
            if res is not None:
                self.syc_criteria.append(res)
        for sec in scheme.semantics_criteria:
            res = EvalHandler.evaluate_criteria(sec, model)
            if res is not None:
                self.sec_criteria.append(res)
        
        self.all_criteria = self.cpt_criteria + self.syc_criteria + self.sec_criteria
    
    def __repr__(self):
        output = ["EvalHandler Summary:"]
        output.append(f"Total Criteria: {len(self.all_criteria)}")
        output.append(f"Completeness Criteria: {len(self.cpt_criteria)} criteria")
        output.append("\t"+"\n\t".join([repr(c) for c in self.cpt_criteria]))
        output.append(f"Syntactic Correctness Criteria: {len(self.syc_criteria)} criteria")
        output.append("\t"+"\n\t".join([repr(c) for c in self.syc_criteria]))
        output.append(f"Semantic Correctness Criteria: {len(self.sec_criteria)} criteria")
        output.append("\t"+"\n\t".join([repr(c) for c in self.sec_criteria]))
        return "\n".join(output)
    
    def __str__(self):
        return f"EvalHandler with {len(self.all_criteria)} total criteria, {len(self.cpt_criteria)} completeness, {len(self.syc_criteria)} syntactic correctness, and {len(self.sec_criteria)} semantic correctness criteria."

    @staticmethod
    def evaluate_all_criteria(model: EvalModel) -> List[ScoringCriteria]:
        scheme = ScoringScheme()
        evaluated_criteria: List[ScoringCriteria] = []
        
        for criteria in scheme.criteria:
            evaluated_criteria.append(EvalHandler.evaluate_criteria(criteria, model))
        
        return evaluated_criteria

    @staticmethod
    def evaluate_criteria(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        if criteria.category == "Completeness":
            return EvalHandler.evaluate_completeness(criteria, model)
            
        elif criteria.category == "Syntactic Correctness":
            if criteria.id.endswith(".global"):
                return EvalHandler.evaluate_syntactic_correctness_global(criteria, model)
            else:
                return EvalHandler.evaluate_syntactic_correctness(criteria, model)
            
        elif criteria.category == "Semantic Correctness":
            return EvalHandler.evaluate_semantic_correctness(criteria, model)
        
        else:   
            raise ValueError(f"Unknown criteria category: {criteria.category}")
    
    @staticmethod
    def evaluate_completeness(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        if criteria.id == "CPT1":
            return CompletenessEvaluator.evaluate_classes(criteria, model)
        elif criteria.id == "CPT2":
            return CompletenessEvaluator.evaluate_attributes(criteria, model)
        elif criteria.id == "CPT3":
            return CompletenessEvaluator.evaluate_operations(criteria, model)
        elif criteria.id == "CPT4":
            return CompletenessEvaluator.evaluate_relations(criteria, model)
        elif criteria.id == "CPT5":
            return CompletenessEvaluator.evaluate_multiplicities(criteria, model)
        elif criteria.id == "CPT6":
            return CompletenessEvaluator.evaluate_relation_names(criteria, model)
        elif criteria.id == "CPT7":
            return CompletenessEvaluator.evaluate_role_names(criteria, model)
        elif criteria.id == "CPT8":
            return CompletenessEvaluator.evaluate_enumerations(criteria, model)
        elif criteria.id == "CPT9":
            return CompletenessEvaluator.evaluate_enum_values(criteria, model)
        else:
            raise ValueError(f"Unknown completeness criteria id: {criteria.id}")
        
    @staticmethod
    def evaluate_syntactic_correctness(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        if criteria.id == "SYC1":
            SyntaxEvaluator.evaluate_classes(criteria, model)
        elif criteria.id == "SYC2":
            return SyntaxEvaluator.evaluate_attributes(criteria, model)
        elif criteria.id == "SYC3":
            return SyntaxEvaluator.evaluate_operations(criteria, model)
        elif criteria.id == "SYC4":
            return SyntaxEvaluator.evaluate_relation(criteria, model, UMLRelationType.ASSOCIATION)
        elif criteria.id == "SYC5":
            return SyntaxEvaluator.evaluate_relation(criteria, model, UMLRelationType.AGGREGATION)
        elif criteria.id == "SYC6":
            return SyntaxEvaluator.evaluate_relation(criteria, model, UMLRelationType.COMPOSITION)
        elif criteria.id == "SYC7":
            # NOTE: generalisations are not implemented yet
            criteria.score = 1.0
            return criteria
        elif criteria.id == "SYC8":
            return SyntaxEvaluator.evaluate_multiplicities(criteria, model)
        elif criteria.id == "SYC9":
            return SyntaxEvaluator.evaluate_roles(criteria, model)
        elif criteria.id == "SYC10":
            return SyntaxEvaluator.evaluate_association_classes(criteria, model)
        elif criteria.id == "SYC11":
            return SyntaxEvaluator.evaluate_enumerations(criteria, model)
        elif criteria.id == "SYC12":
            return SyntaxEvaluator.evaluate_enum_values(criteria, model)
        else:
            raise ValueError(f"Unknown syntactic correctness criteria id: {criteria.id}")
        
    @staticmethod
    def evaluate_syntactic_correctness_global(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        if criteria.id == "SYC1.global":
            return SyntaxEvaluator.evaluate_formal_classes(criteria, model)
        elif criteria.id == "SYC2.global":
            return SyntaxEvaluator.evaluate_formal_attributes(criteria, model)
        elif criteria.id == "SYC3.global":
            return SyntaxEvaluator.evaluate_formal_operations(criteria, model)
        elif criteria.id == "SYC4.global":
            return SyntaxEvaluator.evaluate_formal_relations(criteria, model, UMLRelationType.ASSOCIATION)
        elif criteria.id == "SYC5.global":
            return SyntaxEvaluator.evaluate_formal_relations(criteria, model, UMLRelationType.AGGREGATION)
        elif criteria.id == "SYC6.global":
            return SyntaxEvaluator.evaluate_formal_relations(criteria, model, UMLRelationType.COMPOSITION)
        elif criteria.id == "SYC7.global":
            # NOTE: generalisations are not implemented yet
            criteria.score = 1.0
            return criteria
        elif criteria.id == "SYC8.global":
            pass
        elif criteria.id == "SYC9.global":
            pass
        elif criteria.id == "SYC10.global":
            pass
        elif criteria.id == "SYC11.global":
            pass
        elif criteria.id == "SYC12.global":
            pass
        elif criteria.id == "SYC20.global":
            return SyntaxEvaluator.evaluate_global_class_names(criteria, model)
        elif criteria.id == "SYC21.global":
            return SyntaxEvaluator.evaluate_global_attribute_names(criteria, model)
        elif criteria.id == "SYC22.global":
            return SyntaxEvaluator.evaluate_global_operation_names(criteria, model)
        elif criteria.id == "SYC23.global":
            return SyntaxEvaluator.evaluate_global_enum_names(criteria, model)
        elif criteria.id == "SYC24.global":
            return SyntaxEvaluator.evaluate_global_enum_values(criteria, model)
        elif criteria.id == "SYC25.global":
            return SyntaxEvaluator.evaluate_all_relations(criteria, model)
        else:
            raise ValueError(f"Unknown syntactic correctness criteria id: {criteria.id}")
    
    @staticmethod
    def evaluate_semantic_correctness(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        return None
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