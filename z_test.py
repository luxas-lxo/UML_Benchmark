from tools.syntactic_check import SyntacticCheck

m1 = "*"
m2 = "0..22"
m3 = "1..*"
m4 = "*..*"
m5 = "*..30"
print(SyntacticCheck.is_valid_multiplicity(m1))  # True
print(SyntacticCheck.is_valid_multiplicity(m2))  # True
print(SyntacticCheck.replace_high_numbers_in_multiplicity(m1))  # "*"
print(SyntacticCheck.replace_high_numbers_in_multiplicity(m2))  # "0..22"
print(SyntacticCheck.replace_high_numbers_in_multiplicity(m3))  # "1..*"
print(SyntacticCheck.replace_high_numbers_in_multiplicity(m4))  # "*..*"
print(SyntacticCheck.replace_high_numbers_in_multiplicity(m5))  # "*..*"
print(SyntacticCheck.is_multiplicity_match_replace_high_numbers(m1, m2))  # True

print(SyntacticCheck.get_numbers_or_stars_from_multiplicity(m1))  # ("*", "*"
print(SyntacticCheck.get_numbers_or_stars_from_multiplicity(m2))  # ("0", "22"
print(SyntacticCheck.get_numbers_or_stars_from_multiplicity(m3))  # ("1", "*"
print(SyntacticCheck.get_numbers_or_stars_from_multiplicity(m4))  # ("*", "*"
print(SyntacticCheck.get_numbers_or_stars_from_multiplicity(m5))  # ("*", "*"
print(SyntacticCheck.get_numbers_or_stars_from_multiplicity("lol"))

print(SyntacticCheck.compare_multiplicities(m1, m2), m2)  # 0.0
print(SyntacticCheck.compare_multiplicities(m1, m3), m3)  # 0.0
print(SyntacticCheck.compare_multiplicities(m1, m4), m4)  # 0.0
print(SyntacticCheck.compare_multiplicities(m1, m5), m5)  # 0.0