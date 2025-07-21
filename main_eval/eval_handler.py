from plantuml_eval.eval_model import EvalModel
from main_eval.eval_metrics import ScoringCriteria, ScoringScheme, COMPLETENESS, SYNTAX, SYNTAX_GLOBAL, SEMANTICS, NAMING, NAMING_GLOBAL
from main_eval.eval_completeness import CompletenessEvaluator
from UML_model.uml_relation import UMLRelationType
from main_eval.eval_syntax import SyntaxEvaluator

from typing import List, Dict, Tuple, Optional
class EvalHandler:
    def __init__(self, model: EvalModel):
        self.scheme = ScoringScheme()
        self.completeness_criteria: Dict[str, Tuple[ScoringCriteria, Optional[List[ScoringCriteria]], Optional[List[ScoringCriteria]]]] = self.scheme.completeness_criteria
        self.syntax_criteria: Dict[str, Tuple[ScoringCriteria, Optional[List[ScoringCriteria]], Optional[List[ScoringCriteria]]]] = self.scheme.syntax_criteria
        self.global_syntax_criteria: Dict[str, Tuple[ScoringCriteria, Optional[List[ScoringCriteria]], Optional[List[ScoringCriteria]]]] = self.scheme.global_syntax_criteria
        self.semantics_criteria: Dict[str, Tuple[ScoringCriteria, Optional[List[ScoringCriteria]], Optional[List[ScoringCriteria]]]] = self.scheme.semantics_criteria
        self.naming_criteria: Dict[str, ScoringCriteria] = self.scheme.naming_criteria
        self.global_naming_criteria: Dict[str, ScoringCriteria] = self.scheme.global_naming_criteria

        for tuple in self.completeness_criteria.values():
            criteria, sub_criteria_1, sub_criteria_2 = tuple
            self.evaluate_completeness(criteria, model)
            if sub_criteria_1:
                for sub_criteria in sub_criteria_1:
                    self.evaluate_completeness(sub_criteria, model)
            if sub_criteria_2:
                for sub_criteria in sub_criteria_2:
                    self.evaluate_completeness(sub_criteria, model)

        for tuple in self.syntax_criteria.values():
            criteria, sub_criteria_1, sub_criteria_2 = tuple
            self.evaluate_criteria(criteria, model)
            if sub_criteria_1:
                for sub_criteria in sub_criteria_1:
                    self.evaluate_criteria(sub_criteria, model)
            if sub_criteria_2:
                for sub_criteria in sub_criteria_2:
                    self.evaluate_criteria(sub_criteria, model)
        
        for tuple in self.global_syntax_criteria.values():
            criteria, sub_criteria_1, sub_criteria_2 = tuple
            self.evaluate_criteria(criteria, model)
            if sub_criteria_1:
                for sub_criteria in sub_criteria_1:
                    self.evaluate_criteria(sub_criteria, model)
            if sub_criteria_2:
                for sub_criteria in sub_criteria_2:
                    self.evaluate_criteria(sub_criteria, model)
    
    def __repr__(self):
        output = ["Eval Summary:"]
        output.append(f"Completeness Criteria: {len(self.completeness_criteria)}")
        for name, (criteria, sub_1, sub_2) in self.completeness_criteria.items():
            output.append(f"{name}")
            output.append(f"\t{repr(criteria)}")
            if sub_1:
                for sub in sub_1:
                    output.append(f"\t\tSub-criteria: {repr(sub)}")
            if sub_2:
                for sub in sub_2:
                    output.append(f"\t\tSub-criteria: {repr(sub)}")
        output.append(f"Syntax Criteria: {len(self.syntax_criteria)}")
        for name, (criteria, sub_1, sub_2) in self.syntax_criteria.items():
            output.append(f"{name}")
            output.append(f"\t{repr(criteria)}")
            if sub_1:
                for sub in sub_1:
                    output.append(f"\t\tSub-criteria: {repr(sub)}")
            if sub_2:
                for sub in sub_2:
                    output.append(f"\t\tSub-criteria: {repr(sub)}")
        output.append(f"Global Syntax Criteria: {len(self.global_syntax_criteria)}")
        for name, (criteria, sub_1, sub_2) in self.global_syntax_criteria.items():
            output.append(f"{name}")
            output.append(f"\t{repr(criteria)}")
            if sub_1:
                for sub in sub_1:
                    output.append(f"\t\tSub-criteria: {repr(sub)}")
            if sub_2:
                for sub in sub_2:
                    output.append(f"\t\tSub-criteria: {repr(sub)}")
        output.append(f"Semantics Criteria: {len(self.semantics_criteria)}")
        output.append(f"Naming Criteria: {len(self.naming_criteria)}")
        output.append(f"Global Naming Criteria: {len(self.global_naming_criteria)}")
        return "\n".join(output)
    
    def __str__(self):
        return "EvalHandler()"

    @staticmethod
    def evaluate_criteria(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        if criteria.category == COMPLETENESS:
            return EvalHandler.evaluate_completeness(criteria, model)
        elif criteria.category == SYNTAX:
            return EvalHandler.evaluate_syntactic_correctness(criteria, model)
        elif criteria.category == SYNTAX_GLOBAL:
            return EvalHandler.evaluate_syntactic_correctness_global(criteria, model)
        elif criteria.category == SEMANTICS:
            return EvalHandler.evaluate_semantic_correctness(criteria, model)
        elif criteria.category == NAMING:
            return EvalHandler.evaluate_naming(criteria, model)
        elif criteria.category == NAMING_GLOBAL:
            return EvalHandler.evaluate_naming_global(criteria, model)
        else:   
            raise ValueError(f"Unknown criteria category: {criteria.category}")
    
    @staticmethod
    def evaluate_completeness(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        if criteria.id == "CPT.CLS":
            return CompletenessEvaluator.evaluate_classes(criteria, model)
        
        elif criteria.id == "CPT.ATT":
            return CompletenessEvaluator.evaluate_attributes(criteria, model)
        elif criteria.id == "CPT.ATT.VIS":
            return CompletenessEvaluator.evaluate_att_visibility(criteria, model)
        elif criteria.id == "CPT.ATT.TYP":
            return CompletenessEvaluator.evaluate_att_data_type(criteria, model)
        elif criteria.id == "CPT.ATT.INT":
            return CompletenessEvaluator.evaluate_att_initial_value(criteria, model)
        
        elif criteria.id == "CPT.OPR":
            return CompletenessEvaluator.evaluate_operations(criteria, model)
        elif criteria.id == "CPT.OPR.VIS":
            return CompletenessEvaluator.evaluate_op_visibility(criteria, model)
        elif criteria.id == "CPT.OPR.PAR":
            return CompletenessEvaluator.evaluate_op_parameters(criteria, model)
        elif criteria.id == "CPT.OPR.RET":
            return CompletenessEvaluator.evaluate_op_return_types(criteria, model)
        
        elif criteria.id == "CPT.ENM":
            return CompletenessEvaluator.evaluate_enumerations(criteria, model)
        elif criteria.id == "CPT.VAL":
            return CompletenessEvaluator.evaluate_enum_values(criteria, model)
        
        elif criteria.id == "CPT.REL":
            return CompletenessEvaluator.evaluate_relations(criteria, model)
        elif criteria.id == "CPT.REL.MUL":
            return CompletenessEvaluator.evaluate_rel_multiplicity(criteria, model)
        elif criteria.id == "CPT.REL.DSC":
            return CompletenessEvaluator.evaluate_rel_description(criteria, model)
        elif criteria.id == "CPT.ASS":
            return CompletenessEvaluator.evaluate_relations_with_type(criteria, model, UMLRelationType.ASSOCIATION)
        elif criteria.id == "CPT.AGG":
            return CompletenessEvaluator.evaluate_relations_with_type(criteria, model, UMLRelationType.AGGREGATION)
        elif criteria.id == "CPT.COM":
            return CompletenessEvaluator.evaluate_relations_with_type(criteria, model, UMLRelationType.COMPOSITION)
        elif criteria.id == "CPT.GEN":
            return CompletenessEvaluator.evaluate_relations_with_type(criteria, model, UMLRelationType.GENERALIZATION)
        elif criteria.id == "CPT.ACR":
            return CompletenessEvaluator.evaluate_relations_with_type(criteria, model, UMLRelationType.ASSOCIATION_LINK)
        else:
            raise ValueError(f"Unknown completeness criteria id: {criteria.id}")
        
    @staticmethod
    def evaluate_syntactic_correctness(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        if criteria.id == "SYC.CLS":
            return SyntaxEvaluator.evaluate_classes(criteria, model)
        
        elif criteria.id == "SYC.ATT":
            return SyntaxEvaluator.evaluate_attributes(criteria, model)
        elif criteria.id == "SYC.ATT.NAM":
            return SyntaxEvaluator.evaluate_att_name(criteria, model)
        elif criteria.id == "SYC.ATT.VIS":
            return SyntaxEvaluator.evaluate_att_visibility(criteria, model)
        elif criteria.id == "SYC.ATT.TYP":
            return SyntaxEvaluator.evaluate_att_data_type(criteria, model)
        elif criteria.id == "SYC.ATT.INT":
            return SyntaxEvaluator.evaluate_att_initial_value(criteria, model)
        
        elif criteria.id == "SYC.OPR":
            return SyntaxEvaluator.evaluate_operations(criteria, model)
        elif criteria.id == "SYC.OPR.NAM":
            return SyntaxEvaluator.evaluate_op_name(criteria, model)
        elif criteria.id == "SYC.OPR.VIS":
            return SyntaxEvaluator.evaluate_op_visibility(criteria, model)
        elif criteria.id == "SYC.OPR.PAR":
            return SyntaxEvaluator.evaluate_op_parameters(criteria, model)
        elif criteria.id == "SYC.OPR.RET":
            return SyntaxEvaluator.evaluate_op_return_types(criteria, model)
        
        elif criteria.id == "SYC.ENM":
            return SyntaxEvaluator.evaluate_enumerations(criteria, model)
        elif criteria.id == "SYC.VAL":
            return SyntaxEvaluator.evaluate_enum_values(criteria, model)
        
        elif criteria.id == "SYC.REL":
            return SyntaxEvaluator.evaluate_relations(criteria, model)
        elif criteria.id == "SYC.REL.TYP":
            return SyntaxEvaluator.evaluate_rel_type(criteria, model)
        elif criteria.id == "SYC.REL.MUL":
            return SyntaxEvaluator.evaluate_rel_multiplicity(criteria, model)
        elif criteria.id == "SYC.REL.DSC":
            return SyntaxEvaluator.evaluate_rel_description(criteria, model)
        elif criteria.id == "SYC.ASS":
            return SyntaxEvaluator.evaluate_relations_with_type(criteria, model, UMLRelationType.ASSOCIATION)
        elif criteria.id == "SYC.AGG":
            return SyntaxEvaluator.evaluate_relations_with_type(criteria, model, UMLRelationType.AGGREGATION)
        elif criteria.id == "SYC.COM":
            return SyntaxEvaluator.evaluate_relations_with_type(criteria, model, UMLRelationType.COMPOSITION)
        elif criteria.id == "SYC.GEN":
            return SyntaxEvaluator.evaluate_relations_with_type(criteria, model, UMLRelationType.GENERALIZATION)
        elif criteria.id == "SYC.ACR":
            return SyntaxEvaluator.evaluate_relations_with_type(criteria, model, UMLRelationType.ASSOCIATION_LINK)
        else:
            raise ValueError(f"Unknown syntactic correctness criteria id: {criteria.id}")
        
    @staticmethod
    def evaluate_syntactic_correctness_global(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        if criteria.id == "SYG.CLS":
            return SyntaxEvaluator.evaluate_classes_global(criteria, model)
        
        elif criteria.id == "SYG.ATT":
            return SyntaxEvaluator.evaluate_attributes_global(criteria, model)
        elif criteria.id == "SYG.ATT.NAM":
            return SyntaxEvaluator.evaluate_att_name_global(criteria, model)
        elif criteria.id == "SYG.ATT.VIS":
            return SyntaxEvaluator.evaluate_att_visibility_global(criteria, model)
        elif criteria.id == "SYG.ATT.TYP":
            return SyntaxEvaluator.evaluate_att_data_type_global(criteria, model)
        elif criteria.id == "SYG.ATT.INT":
            return SyntaxEvaluator.evaluate_att_initial_value_global(criteria, model)
        
        elif criteria.id == "SYG.OPR":
            return SyntaxEvaluator.evaluate_operations_global(criteria, model)
        elif criteria.id == "SYG.OPR.NAM":
            return SyntaxEvaluator.evaluate_op_name_global(criteria, model)
        elif criteria.id == "SYG.OPR.VIS":
            return SyntaxEvaluator.evaluate_op_visibility_global(criteria, model)
        elif criteria.id == "SYG.OPR.PAR":
            return SyntaxEvaluator.evaluate_op_parameters_global(criteria, model)
        elif criteria.id == "SYG.OPR.RET":
            return SyntaxEvaluator.evaluate_op_return_types_global(criteria, model)
        
        elif criteria.id == "SYG.ENM":
            return SyntaxEvaluator.evaluate_enumerations_global(criteria, model)
        elif criteria.id == "SYG.VAL":
            return SyntaxEvaluator.evaluate_enum_values_global(criteria, model)
        
        elif criteria.id == "SYG.REL":
            return SyntaxEvaluator.evaluate_relations_global(criteria, model)
        elif criteria.id == "SYG.REL.TYP":
            return SyntaxEvaluator.evaluate_rel_type_global(criteria, model)
        elif criteria.id == "SYG.REL.MUL":
            return SyntaxEvaluator.evaluate_rel_multiplicity_global(criteria, model)
        elif criteria.id == "SYG.REL.DSC":
            return SyntaxEvaluator.evaluate_rel_description_global(criteria, model)
        elif criteria.id == "SYG.ASS":
            return SyntaxEvaluator.evaluate_relations_with_type_global(criteria, model, UMLRelationType.ASSOCIATION)
        elif criteria.id == "SYG.AGG":
            return SyntaxEvaluator.evaluate_relations_with_type_global(criteria, model, UMLRelationType.AGGREGATION)
        elif criteria.id == "SYG.COM":
            return SyntaxEvaluator.evaluate_relations_with_type_global(criteria, model, UMLRelationType.COMPOSITION)
        elif criteria.id == "SYG.GEN":
            return SyntaxEvaluator.evaluate_relations_with_type_global(criteria, model, UMLRelationType.GENERALIZATION)
        elif criteria.id == "SYG.ACR":
            return SyntaxEvaluator.evaluate_relations_with_type_global(criteria, model, UMLRelationType.ASSOCIATION_LINK)
        else:
            raise ValueError(f"Unknown global syntactic correctness criteria id: {criteria.id}")
    
    @staticmethod
    def evaluate_semantic_correctness(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        pass

    @staticmethod
    def evaluate_naming(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        pass

    @staticmethod
    def evaluate_naming_global(criteria: ScoringCriteria, model: EvalModel) -> ScoringCriteria:
        pass