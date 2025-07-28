from typing import List, Dict, Tuple, Optional, Union

COMPLETENESS = "Completeness"
SYNTAX = "Syntactic Correctness"
SYNTAX_GLOBAL = "Syntactic Correctness Global"
SEMANTICS = "Semantic Correctness"
NAMING = "Naming Conventions"
NAMING_GLOBAL = "Naming Conventions Global"
NO_STATEMENT: float = 777

class ScoringCriteria:
    def __init__(self, category: str, id: str, description: str, weight: float = 0, score: float = 0.0):
        self.category: str = category
        self.id: str = id
        self.description: str = description
        self.weight: float = weight
        self.score: float = score

    def __repr__(self):
        return f"ScoringCriteria(category={self.category}, id={self.id}, description={self.description}, weight={self.weight}, score={self.score})"
    
    def __str__(self):
        return f"ScoringCriteria({self.id})"
    
class ScoringScheme:
    def __init__(self):

        self.completeness_criteria: Dict[str, Tuple[ScoringCriteria, Optional[List[ScoringCriteria]], Optional[List[ScoringCriteria]]]] = {}
        self.init_completeness()
        self.set_weight_in_criteria(self.completeness_criteria)
        self.cpt = ScoringCriteria(COMPLETENESS, "CPT", "All necessary elements exist", 1.0)

        self.syntax_criteria: Dict[str, Tuple[ScoringCriteria, Optional[List[ScoringCriteria]], Optional[List[ScoringCriteria]]]] = {}
        self.init_syntax()
        self.set_weight_in_criteria(self.syntax_criteria)
        self.syc = ScoringCriteria(SYNTAX, "SYC", "All matched elements are syntactically correct", 1.0)

        self.global_syntax_criteria: Dict[str, Tuple[ScoringCriteria, Optional[List[ScoringCriteria]], Optional[List[ScoringCriteria]]]] = {}
        self.init_syntax_global()
        self.set_weight_in_criteria(self.global_syntax_criteria)
        self.syg = ScoringCriteria(SYNTAX_GLOBAL, "SYG", "All elements are syntactically correct", 1.0)
        
        self.semantics_criteria: Dict[str, Tuple[ScoringCriteria, Optional[List[ScoringCriteria]], Optional[List[ScoringCriteria]]]] = {}
        self.init_semantics()
        self.set_weight_in_criteria(self.semantics_criteria)
        self.sec = ScoringCriteria(SEMANTICS, "SEC", "All matched elements are semantically correct", 1.0)

        self.naming_criteria: Dict[str, ScoringCriteria] = {}
        self.init_naming()
        self.set_weight_in_criteria(self.naming_criteria)
        self.nam = ScoringCriteria(NAMING, "NAM", "All matched elements follow the naming conventions", 1.0)

        self.global_naming_criteria: Dict[str, ScoringCriteria] = {}
        self.init_naming_global()
        self.set_weight_in_criteria(self.global_naming_criteria)
        self.nmg = ScoringCriteria(NAMING_GLOBAL, "NMG", "All elements follow the naming conventions", 1.0)

    def init_completeness(self):
        COMPLETENESS = "Completeness"
        cpt_cls = ScoringCriteria(COMPLETENESS, "CPT.CLS", "All necessary classes are included")
        
        cpt_att = ScoringCriteria(COMPLETENESS, "CPT.ATT", "Classes include all necessary attributes")
        cpt_att_der = ScoringCriteria(COMPLETENESS, "CPT.ATT.DER", "Attributes include all necessary derivation state indicators")
        cpt_att_vis = ScoringCriteria(COMPLETENESS, "CPT.ATT.VIS", "Attributes include all necessary visibility modifiers")
        cpt_att_mul = ScoringCriteria(COMPLETENESS, "CPT.ATT.MUL", "Attributes include all necessary multiplicities")
        cpt_att_typ = ScoringCriteria(COMPLETENESS, "CPT.ATT.TYP", "Attributes include all necessary data types")
        cpt_att_int = ScoringCriteria(COMPLETENESS, "CPT.ATT.INT", "Attributes include all necessary initial values")
        attribute_criteria = [cpt_att_der,cpt_att_vis, cpt_att_mul, cpt_att_typ, cpt_att_int]

        cpt_opr = ScoringCriteria(COMPLETENESS, "CPT.OPR", "Classes include all necessary operations")
        cpt_opr_vis = ScoringCriteria(COMPLETENESS, "CPT.OPR.VIS", "Operations include all necessary visibility modifiers")
        cpt_opr_par = ScoringCriteria(COMPLETENESS, "CPT.OPR.PAR", "Operations include all necessary parameters")
        cpt_opr_ret = ScoringCriteria(COMPLETENESS, "CPT.OPR.RET", "Operations include all necessary return values")
        operation_criteria = [cpt_opr_vis, cpt_opr_par, cpt_opr_ret] 

        cpt_enm = ScoringCriteria(COMPLETENESS, "CPT.ENM", "All necessary enumerations are included")
        cpt_val = ScoringCriteria(COMPLETENESS, "CPT.VAL", "Enumerations include all necessary values")

        cpt_rel = ScoringCriteria(COMPLETENESS, "CPT.REL", "All necessary relations are included")
        cpt_mul = ScoringCriteria(COMPLETENESS, "CPT.REL.MUL", "Multiplicities are included in relations")
        # NOTE: role names are not implemented as of now
        #cpt_rol = ScoringCriteria(COMPLETENESS, "CPT.REL.ROL", "Role names are included")
        cpt_dsc = ScoringCriteria(COMPLETENESS, "CPT.REL.DSC", "Descriptions are included in relations")
        relation_criteria = [cpt_mul, cpt_dsc]
        
        cpt_ass = ScoringCriteria(COMPLETENESS, "CPT.ASS", "All necessary associations are included")
        cpt_agg = ScoringCriteria(COMPLETENESS, "CPT.AGG", "All necessary aggregations are included")
        cpt_com = ScoringCriteria(COMPLETENESS, "CPT.COM", "All necessary compositions are included")
        cpt_gen = ScoringCriteria(COMPLETENESS, "CPT.GEN", "All necessary generalizations are included")
        cpt_acr = ScoringCriteria(COMPLETENESS, "CPT.ACR", "All necessary association class relations are included")
        relation_type_criteria = [cpt_ass, cpt_agg, cpt_com, cpt_gen, cpt_acr]
        self.completeness_criteria: Dict[str, Tuple[ScoringCriteria, Optional[List[ScoringCriteria]], Optional[List[ScoringCriteria]]]] = {
            "CLS": (cpt_cls, None, None),
            "ATT": (cpt_att, attribute_criteria, None),
            "OPR": (cpt_opr, operation_criteria, None),
            "ENM": (cpt_enm, None, None),
            "VAL": (cpt_val, None, None),
            "REL": (cpt_rel, relation_criteria, relation_type_criteria),
        }

    def init_syntax(self):
        syc_cls = ScoringCriteria(SYNTAX, "SYC.CLS", "Classes are correctly represented")

        syc_att = ScoringCriteria(SYNTAX, "SYC.ATT", "Class attributes are correctly represented")
        syc_att_nam = ScoringCriteria(SYNTAX, "SYC.ATT.NAM", "Attribute names are correctly represented")
        # NOTE: at the moment nothing can be syntactically wrong with derivation state either it is there or not so we only evaluate that in the semantics
        #syc_att_der = ScoringCriteria(SYNTAX, "SYC.ATT.DER", "Deriviation state of attributes is correctly represented")
        syc_att_vis = ScoringCriteria(SYNTAX, "SYC.ATT.VIS", "Visibility of attributes is correctly represented")
        syc_att_mul = ScoringCriteria(SYNTAX, "SYC.ATT.MUL", "Multiplicity of attributes is correctly represented")
        syc_att_typ = ScoringCriteria(SYNTAX, "SYC.ATT.TYP", "Data types of attributes are correctly represented")
        syc_att_int = ScoringCriteria(SYNTAX, "SYC.ATT.INT", "Initial values of attributes are correctly represented")
        att_criteria = [syc_att_nam, syc_att_vis, syc_att_mul, syc_att_typ, syc_att_int]

        syc_opr = ScoringCriteria(SYNTAX, "SYC.OPR", "Class operations are correctly represented")
        syc_opr_nam = ScoringCriteria(SYNTAX, "SYC.OPR.NAM", "Operation names are correctly represented")
        syc_opr_vis = ScoringCriteria(SYNTAX, "SYC.OPR.VIS", "Visibility of operations is correctly represented")
        syc_opr_par = ScoringCriteria(SYNTAX, "SYC.OPR.PAR", "Parameters of operations are correctly represented")
        syc_opr_ret = ScoringCriteria(SYNTAX, "SYC.OPR.RET", "Return values of operations are correctly represented")
        opr_criteria = [syc_opr_nam, syc_opr_vis, syc_opr_par, syc_opr_ret]

        syc_enm = ScoringCriteria(SYNTAX, "SYC.ENM", "Enumerations are correctly represented")
        syc_val = ScoringCriteria(SYNTAX, "SYC.VAL", "Enumeration values are correctly represented")

        syc_rel = ScoringCriteria(SYNTAX, "SYC.REL", "Relations are correctly represented")
        syc_rel_typ = ScoringCriteria(SYNTAX, "SYC.REL.TYP", "Relation types are correctly represented")
        syc_rel_mul = ScoringCriteria(SYNTAX, "SYC.REL.MUL", "Relation multiplicities are correctly represented")
        # NOTE: role names are not implemented as of now
        #syc_rel_rol = ScoringCriteria(SYNTAX, "SYC.REL.ROL", "Roles are correctly represented")
        syc_rel_dsc = ScoringCriteria(SYNTAX, "SYC.REL.DSC", "Descriptions are correctly represented")
        relation_criteria = [syc_rel_typ, syc_rel_mul, syc_rel_dsc]

        # NOTE: the paper proposes a differentiation between different types of relation but in general it is the same as the relation criteria
        syc_ass = ScoringCriteria(SYNTAX, "SYC.ASS", "Simple associations are correctly represented")
        syc_agg = ScoringCriteria(SYNTAX, "SYC.AGG", "Aggregation relations are correctly represented")
        syc_com = ScoringCriteria(SYNTAX, "SYC.COM", "Composition relations are correctly represented")
        syc_gen = ScoringCriteria(SYNTAX, "SYC.GEN", "Generalization relations are correctly represented")
        syc_acr = ScoringCriteria(SYNTAX, "SYC.ACR", "Association class relations are correctly represented")
        relation_type_criteria: List[ScoringCriteria] = [syc_ass, syc_agg, syc_com, syc_gen, syc_acr]
        
        self.syntax_criteria: Dict[str, Tuple[ScoringCriteria, Optional[List[ScoringCriteria]], Optional[List[ScoringCriteria]]]] = {
            "CLS": (syc_cls, None, None),
            "ATT": (syc_att, att_criteria, None),
            "OPR": (syc_opr, opr_criteria, None),
            "ENM": (syc_enm, None, None),
            "VAL": (syc_val, None, None),
            "REL": (syc_rel, relation_criteria, relation_type_criteria),
        }
    
    def init_syntax_global(self):
        syg_cls = ScoringCriteria(SYNTAX_GLOBAL, "SYG.CLS", "Classes are correctly represented")

        syg_att = ScoringCriteria(SYNTAX_GLOBAL, "SYG.ATT", "Class attributes are correctly represented")
        syg_att_nam = ScoringCriteria(SYNTAX_GLOBAL, "SYG.ATT.NAM", "Attribute names are correctly represented")
        #syg_att_der = ScoringCriteria(SYNTAX_GLOBAL, "SYG.ATT.DER", "Deriviation state of attributes is correctly represented")
        syg_att_vis = ScoringCriteria(SYNTAX_GLOBAL, "SYG.ATT.VIS", "Visibility of attributes is correctly represented")
        syg_att_mul = ScoringCriteria(SYNTAX_GLOBAL, "SYG.ATT.MUL", "Multiplicity of attributes is correctly represented")
        syg_att_typ = ScoringCriteria(SYNTAX_GLOBAL, "SYG.ATT.TYP", "Data types of attributes are correctly represented")
        syg_att_int = ScoringCriteria(SYNTAX_GLOBAL, "SYG.ATT.INT", "Initial values of attributes are correctly represented")
        att_criteria = [syg_att_nam, syg_att_vis, syg_att_mul, syg_att_typ, syg_att_int]

        syg_opr = ScoringCriteria(SYNTAX_GLOBAL, "SYG.OPR", "Class operations are correctly represented")
        syg_opr_nam = ScoringCriteria(SYNTAX_GLOBAL, "SYG.OPR.NAM", "Operation names are correctly represented")
        syg_opr_vis = ScoringCriteria(SYNTAX_GLOBAL, "SYG.OPR.VIS", "Visibility of operations is correctly represented")
        syg_opr_par = ScoringCriteria(SYNTAX_GLOBAL, "SYG.OPR.PAR", "Parameters of operations are correctly represented")
        syg_opr_ret = ScoringCriteria(SYNTAX_GLOBAL, "SYG.OPR.RET", "Return values of operations are correctly represented")
        opr_criteria = [syg_opr_nam, syg_opr_vis, syg_opr_par, syg_opr_ret]

        syg_enm = ScoringCriteria(SYNTAX_GLOBAL, "SYG.ENM", "Enumerations are correctly represented")
        syg_val = ScoringCriteria(SYNTAX_GLOBAL, "SYG.VAL", "Enumeration values are correctly represented")

        syg_rel = ScoringCriteria(SYNTAX_GLOBAL, "SYG.REL", "Relations are correctly represented")
        syg_rel_typ = ScoringCriteria(SYNTAX_GLOBAL, "SYG.REL.TYP", "Relation types are correctly represented")
        syg_rel_mul = ScoringCriteria(SYNTAX_GLOBAL, "SYG.REL.MUL", "Relation multiplicities are correctly represented")
        #syg_rel_rol = ScoringCriteria(SYNTAX_GLOBAL, "SYG.REL.ROL", "Roles are correctly represented")
        syg_rel_dsc = ScoringCriteria(SYNTAX_GLOBAL, "SYG.REL.DSC", "Descriptions are correctly represented")
        relation_criteria = [syg_rel_typ, syg_rel_mul, syg_rel_dsc]

        syg_ass = ScoringCriteria(SYNTAX_GLOBAL, "SYG.ASS", "Simple associations are correctly represented")
        syg_agg = ScoringCriteria(SYNTAX_GLOBAL, "SYG.AGG", "Aggregation relations are correctly represented")
        syg_com = ScoringCriteria(SYNTAX_GLOBAL, "SYG.COM", "Composition relations are correctly represented")
        syg_gen = ScoringCriteria(SYNTAX_GLOBAL, "SYG.GEN", "Generalization relations are correctly represented")
        syg_acr = ScoringCriteria(SYNTAX_GLOBAL, "SYG.ACR", "Association class relations are correctly represented")
        relation_type_criteria = [syg_ass, syg_agg, syg_com, syg_gen, syg_acr]

        self.global_syntax_criteria: Dict[str, Tuple[ScoringCriteria, Optional[List[ScoringCriteria]], Optional[List[ScoringCriteria]]]] = {
            "CLS": (syg_cls, None, None),
            "ATT": (syg_att, att_criteria, None),
            "OPR": (syg_opr, opr_criteria, None),
            "ENM": (syg_enm, None, None),
            "VAL": (syg_val, None, None),
            "REL": (syg_rel, relation_criteria, relation_type_criteria),
        }

    def init_semantics(self):
        sec_cls = ScoringCriteria(SEMANTICS, "SEC.CLS", "Classes are appropriate")
        sec_cls_nam = ScoringCriteria(SEMANTICS, "SEC.CLS.NAM", "Classes are named appropriate")
        # NOTE: could also be considered attribute/operation criteria
        sec_cls_att = ScoringCriteria(SEMANTICS, "SEC.CLS.ATT", "Classes attributes are placed appropriate")
        sec_cls_opr = ScoringCriteria(SEMANTICS, "SEC.CLS.OPR", "Classes operations are placed appropriate")
        cls_criteria = [sec_cls_nam, sec_cls_att, sec_cls_opr]

        sec_att = ScoringCriteria(SEMANTICS, "SEC.ATT", "Attribute content is appropriate")
        sec_att_nam = ScoringCriteria(SEMANTICS, "SEC.ATT.NAM", "Attribute names are appropriate")
        sec_att_der = ScoringCriteria(SEMANTICS, "SEC.ATT.DER", "Derivation state of attributes is appropriate")
        sec_att_vis = ScoringCriteria(SEMANTICS, "SEC.ATT.VIS", "Visibility of attributes is appropriate")
        sec_att_mul = ScoringCriteria(SEMANTICS, "SEC.ATT.MUL", "Multiplicity of attributes is appropriate")
        sec_att_typ = ScoringCriteria(SEMANTICS, "SEC.ATT.TYP", "Data types of attributes are appropriate")
        sec_att_int = ScoringCriteria(SEMANTICS, "SEC.ATT.INT", "Initial values of attributes are appropriate")
        att_criteria = [sec_att_nam, sec_att_der, sec_att_vis, sec_att_mul, sec_att_typ, sec_att_int]

        sec_opr = ScoringCriteria(SEMANTICS, "SEC.OPR", "Operation content is appropriate")
        sec_opr_nam = ScoringCriteria(SEMANTICS, "SEC.OPR.NAM", "Operation names are appropriate")
        sec_opr_vis = ScoringCriteria(SEMANTICS, "SEC.OPR.VIS", "Visibility of operations is appropriate")
        sec_opr_par = ScoringCriteria(SEMANTICS, "SEC.OPR.PAR", "Parameters of operations are appropriate")
        sec_opr_ret = ScoringCriteria(SEMANTICS, "SEC.OPR.RET", "Return values of operations are appropriate")
        opr_criteria = [sec_opr_nam, sec_opr_vis, sec_opr_par, sec_opr_ret]

        sec_enm = ScoringCriteria(SEMANTICS, "SEC.ENM", "Enumerations are appropriate")
        sec_enm_nam = ScoringCriteria(SEMANTICS, "SEC.ENM.NAM", "Enumeration names are appropriate")
        sec_enm_val = ScoringCriteria(SEMANTICS, "SEC.ENM.VAL", "Enumeration values are appropriate")
        enm_criteria = [sec_enm_nam, sec_enm_val]

        sec_val = ScoringCriteria(SEMANTICS, "SEC.VAL", "Enumeration values are appropriate")

        sec_rel = ScoringCriteria(SEMANTICS, "SEC.REL", "Relations are appropriate")
        sec_rel_typ = ScoringCriteria(SEMANTICS, "SEC.REL.TYP", "Relation types are appropriate")
        sec_rel_mul = ScoringCriteria(SEMANTICS, "SEC.REL.MUL", "Multiplicities are correct")
        #sec_rel_rol = ScoringCriteria(SEMANTICS, "SEC.REL.ROL", "Role names are appropriate")
        sec_rel_dsc = ScoringCriteria(SEMANTICS, "SEC.REL.DSC", "Relation names are appropriate")
        relation_criteria = [sec_rel, sec_rel_typ, sec_rel_mul, sec_rel_dsc]

        sec_ass = ScoringCriteria(SEMANTICS, "SEC.ASS", "Associations are appropriate")
        sec_agg = ScoringCriteria(SEMANTICS, "SEC.AGG", "Aggregations are appropriate")
        sec_com = ScoringCriteria(SEMANTICS, "SEC.COM", "Compositions are appropriate")
        sec_gen = ScoringCriteria(SEMANTICS, "SEC.GEN", "Generalizations are appropriate")
        sec_acr = ScoringCriteria(SEMANTICS, "SEC.ACR", "Association class relations are appropriate")
        relation_type_criteria = [sec_ass, sec_agg, sec_com, sec_gen, sec_acr]
        
        #sec8 = ScoringCriteria(SEMANTICS, "SEC8", "There are no redundant classes")
        #sec9 = ScoringCriteria(SEMANTICS, "SEC9", "There are no redundant attributes")
        #sec10 = ScoringCriteria(SEMANTICS, "SEC10", "There are no redundant operations")
        #sec11 = ScoringCriteria(SEMANTICS, "SEC11", "There are no redundant relations")  

        self.semantics_criteria: Dict[str, Tuple[ScoringCriteria, Optional[List[ScoringCriteria]], Optional[List[ScoringCriteria]]]] = {
            "CLS": (sec_cls, cls_criteria, None),
            "ATT": (sec_att, att_criteria, None),
            "OPR": (sec_opr, opr_criteria, None),
            "ENM": (sec_enm, enm_criteria, None),
            "VAL": (sec_val, None, None),
            "REL": (sec_rel, relation_criteria, relation_type_criteria),
        } 

    def init_naming(self):
        nam_cls = ScoringCriteria(NAMING, "NAM.CLS", "All classes are in UpperCamelCase")
        nam_att = ScoringCriteria(NAMING, "NAM.ATT", "All attributes are in lowerCamelCase")
        nam_opr = ScoringCriteria(NAMING, "NAM.OPR", "All operations are in lowerCamelCase")
        nam_enm = ScoringCriteria(NAMING, "NAM.ENM", "All enumeration names are in UpperCamelCase")
        nam_val = ScoringCriteria(NAMING, "NAM.VAL", "All enumeration values are in ALL_UPPER_CASE")

        self.naming_criteria: Dict[str, ScoringCriteria] = {
            "CLS": nam_cls,
            "ATT": nam_att,
            "OPR": nam_opr,
            "ENM": nam_enm,
            "VAL": nam_val,
        }

    def init_naming_global(self):
        nmg_cls = ScoringCriteria(NAMING_GLOBAL, "NMG.CLS", "All classes are in UpperCamelCase")
        nmg_att = ScoringCriteria(NAMING_GLOBAL, "NMG.ATT", "All attributes are in lowerCamelCase")
        nmg_opr = ScoringCriteria(NAMING_GLOBAL, "NMG.OPR", "All operations are in lowerCamelCase")
        nmg_enm = ScoringCriteria(NAMING_GLOBAL, "NMG.ENM", "All enumeration names are in UpperCamelCase")
        nmg_val = ScoringCriteria(NAMING_GLOBAL, "NMG.VAL", "All enumeration values are in ALL_UPPER_CASE")

        self.global_naming_criteria: Dict[str, ScoringCriteria] = {
            "CLS": nmg_cls,
            "ATT": nmg_att,
            "OPR": nmg_opr,
            "ENM": nmg_enm,
            "VAL": nmg_val,
        }

    def set_weight_in_criteria(self, criteria_dict: Union[Dict[str, ScoringCriteria], Dict[str, Tuple[ScoringCriteria, Optional[List[ScoringCriteria]], Optional[List[ScoringCriteria]]]]]):
        dict_len = len(criteria_dict)
        if dict_len == 0:
            raise ValueError("Criteria dictionary is empty. Cannot set weights.")
        for value in criteria_dict.values():
            if isinstance(value, ScoringCriteria):
                value.weight = 1 / dict_len
            elif isinstance(value, tuple) and len(value) == 3:
                criteria, sub_criteria_1, sub_criteria_2 = value
                criteria.weight = 1 / dict_len
                if sub_criteria_1 and len(sub_criteria_1) > 0:
                    for sub_crit in sub_criteria_1:
                        sub_crit.weight = 1 / len(sub_criteria_1)
                if sub_criteria_2 and len(sub_criteria_2) > 0:
                    for sub_crit in sub_criteria_2:
                        sub_crit.weight = 1 / len(sub_criteria_2)
            else:
                raise ValueError("Invalid value in criteria dictionary. Expected ScoringCriteria or tuple with ScoringCriteria and optional lists.")

        