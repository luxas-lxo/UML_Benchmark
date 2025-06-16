from pyecore.ecore import *

# Metamodell
GradeModel = EPackage('grademodel', ns_prefix='gm', ns_uri='http://grading/metamodel')

# Klassen
EObjectGrade = EClass('EObjectGrade')
EStructuralFeatureGrade = EClass('EStructuralFeatureGrade')

# Attribute
EObjectGrade.eStructuralFeatures.append(EAttribute('points', EDouble))
EStructuralFeatureGrade.eStructuralFeatures.append(EAttribute('points', EDouble))

# Referenz hinzufügen – das hast du vergessen:
EObjectGrade.structuralgrades = EReference(
    'structuralgrades',
    EStructuralFeatureGrade,
    upper=-1,
    containment=True
)
EObjectGrade.eStructuralFeatures.append(EObjectGrade.structuralgrades)

# EPackage füllen
GradeModel.eClassifiers.extend([EObjectGrade, EStructuralFeatureGrade])
