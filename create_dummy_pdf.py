
from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)

text = """
PROTOCOL TITLE: A Phase 3 Study of Drug X in Oncology.
SPONSOR: Leevin Pharma.

1. OBJECTIVES
To evaluate the safety and efficacy of Drug X.

2. STUDY DESIGN
This is a randomized, double-blind study.

3. VISIT SCHEDULE
- Screening (Day -28 to -1): Informed Consent, Demographics, HIV Test.
- Baseline (Day 1): Randomization, Dosing, PK Blood Draw.
- Visit 1 (Week 4): Vitals, Safety Labs.
- Visit 2 (Week 8): Vitals, Safety Labs, Tumor Assessment.

4. INCLUSION CRITERIA
1. Age >= 18 years.
2. Histologically confirmed solid tumor.

5. EXCLUSION CRITERIA
1. Pregnancy.
2. Active infection.
"""

pdf.multi_cell(0, 10, text)
pdf.output("test_protocol.pdf")
print("✅ Test PDF Created: test_protocol.pdf")
