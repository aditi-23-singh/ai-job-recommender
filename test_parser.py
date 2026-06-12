from backend.ml.resume_parser import ResumeParser

# Test with dummy text (simulating a resume)
sample = """
Aditi Singh
aditi@example.com | github.com/aditi-23-singh | linkedin.com/in/aditi-singh

Summary
Final year ECE student at NIT Sikkim with experience in VLSI and embedded systems.

Skills
Python, Verilog, SystemVerilog, VLSI, FPGA, RTL, STM32, Embedded Systems,
Machine Learning, NumPy, Pandas, Git, C++

Education
B.Tech Electronics and Communication Engineering
NIT Sikkim, 2022 - 2026

Experience
VLSI Design Intern, 2024 - 2025
Worked on RTL design and verification using Verilog.

Certifications
Coursera - Machine Learning Specialization
"""

parser = ResumeParser()
result = parser.parse_text(sample)
d = result.to_dict()

print("Name:", d["name"])
print("Email:", d["email"])
print("GitHub:", d["github"])
print("Experience years:", d["experience_years"])
print("\nSkills found:", d["skills"])
print("\nSkills by category:")
for cat, skills in d["skills_by_category"].items():
    print(f"  {cat}: {skills}")
print("\nEducation:", d["education"])
print("Certifications:", d["certifications"])