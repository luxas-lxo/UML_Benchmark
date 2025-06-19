from pyecore.ecore import *

GradeModel = EClass('GradeModel')
EObjectGrade = EClass('EObjectGrade')
EStructuralFeatureGrade = EClass('EStructuralFeatureGrade')

EObjectGrade.eStructuralFeatures.append(EAttribute('points', EDouble))
EStructuralFeatureGrade.eStructuralFeatures.append(EAttribute('points', EDouble))

# Referenzen wie im Metamodell
EObjectGrade.eStructuralFeatures.append(EReference('element', EObject)) 
EStructuralFeatureGrade.eStructuralFeatures.append(EReference('feature', EStructuralFeature))  

# Beziehungen
GradeModel.eStructuralFeatures.append(EReference('grade', EObjectGrade, upper=-1, containment=True))
EObjectGrade.eStructuralFeatures.append(EReference('grade', EStructuralFeatureGrade, upper=-1, containment=True))



# === Beispielinstanzen ===
# Dummy-Objekte, um UML-Elemente zu simulieren
# Statt EObject(): → EClass('Person')
Person = EClass('Person')
NameAttribute = EAttribute('name', EString)
Person.eStructuralFeatures.append(NameAttribute)

HasFriendReference = EReference('hasFriend', Person)  # ✅ jetzt korrekt
Person.eStructuralFeatures.append(HasFriendReference)

# Danach kannst du eine Instanz von Person erzeugen
person_instance = Person()  # das ist jetzt dein 'EObject'


# Bewertungsobjekte
person_grade = EObjectGrade()
person_grade.element = person_instance
person_grade.points = 5.0

name_feature_grade = EStructuralFeatureGrade()
name_feature_grade.feature = NameAttribute
name_feature_grade.points = 2.0

hasfriend_feature_grade = EStructuralFeatureGrade()
hasfriend_feature_grade.feature = HasFriendReference
hasfriend_feature_grade.points = 3.0

# FeatureGrades zur Objektbewertung hinzufügen
person_grade.grade.extend([name_feature_grade, hasfriend_feature_grade])

# GradeModel anlegen und Bewertung hinzufügen
model = GradeModel()
model.grade.append(person_grade)

for obj_grade in model.grade:
        print(f"Objekt: {obj_grade.element}, Punkte: {obj_grade.points}")
        for feat_grade in obj_grade.grade:
            print(f"  ↳ Feature: {feat_grade.feature.name}, Punkte: {feat_grade.points}")