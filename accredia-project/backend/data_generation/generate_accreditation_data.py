import os
import json
import random
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
import docx

INSTITUTION_NAME = "Vidyapath Institute of Technology"
INSTITUTION_SHORT = "VITEC"
LOCATION = "Hyderabad, Telangana, India"
TAGLINE = "AI-Powered Accreditation Evidence Repository"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ACCREDITATION_DIR = os.path.join(BASE_DIR, "data", "accreditation")
DOCS_DIR = os.path.join(ACCREDITATION_DIR, "documents")
METADATA_DIR = os.path.join(ACCREDITATION_DIR, "metadata")
TEST_QUERIES_DIR = os.path.join(ACCREDITATION_DIR, "test_queries")

os.makedirs(DOCS_DIR, exist_ok=True)
os.makedirs(METADATA_DIR, exist_ok=True)
os.makedirs(TEST_QUERIES_DIR, exist_ok=True)

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_elements(num_pages)
            super().showPage()
        super().save()

    def draw_page_elements(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#4c1d95"))
        # Header line
        self.drawString(54, 750, f"{INSTITUTION_NAME} ({INSTITUTION_SHORT}) — Accreditation Evidence Archive")
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#6b7280"))
        self.drawRightString(558, 750, "Internal Quality Assurance Cell (IQAC)")
        self.setStrokeColor(colors.HexColor("#e5e7eb"))
        self.setLineWidth(0.75)
        self.line(54, 742, 558, 742)

        # Footer line
        self.line(54, 45, 558, 45)
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#9ca3af"))
        self.drawString(54, 32, "Confidential — For Internal Quality Assessment & Accreditation Review Only")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 32, page_str)
        self.restoreState()

CRITERIA = [
    {
        "id": "Criterion 1",
        "name": "Curricular Aspects",
        "weightage": 100,
        "description": "Curriculum design, academic flexibility, value-added courses, and structured stakeholder feedback mechanisms.",
        "subcriteria": [
            {"id": "1.1", "name": "Curricular Planning and Implementation"},
            {"id": "1.2", "name": "Academic Flexibility and CBCS Electives"},
            {"id": "1.3", "name": "Curriculum Enrichment & Value-Added Courses"},
            {"id": "1.4", "name": "Feedback System on Institutional Curriculum"}
        ]
    },
    {
        "id": "Criterion 2",
        "name": "Teaching-Learning and Evaluation",
        "weightage": 350,
        "description": "Student diversity catering, experiential teaching methods, qualified faculty cadre, continuous internal evaluation, and CO-PO attainment.",
        "subcriteria": [
            {"id": "2.1", "name": "Student Enrollment & Reservation Profile"},
            {"id": "2.2", "name": "Catering to Diverse Learning Needs"},
            {"id": "2.3", "name": "Teaching-Learning Process & Experiential Pedagogy"},
            {"id": "2.4", "name": "Teacher Profile & Qualification Quality"},
            {"id": "2.5", "name": "Evaluation Process and Examination Reforms"},
            {"id": "2.6", "name": "Student Performance and Learning Outcomes (CO-PO)"},
            {"id": "2.7", "name": "Student Satisfaction Survey (SSS)"}
        ]
    },
    {
        "id": "Criterion 3",
        "name": "Research, Innovations and Extension",
        "weightage": 110,
        "description": "Resource mobilization for research, incubation ecosystem, Scopus publications, patents, community extension, and corporate collaborations.",
        "subcriteria": [
            {"id": "3.1", "name": "Resource Mobilization for Research & Seed Grants"},
            {"id": "3.2", "name": "Innovation Ecosystem & Startup Incubation"},
            {"id": "3.3", "name": "Research Publications, Books & Citations"},
            {"id": "3.4", "name": "Extension and Community Outreach Activities"},
            {"id": "3.5", "name": "Collaborations, MoUs & Linkages"}
        ]
    },
    {
        "id": "Criterion 4",
        "name": "Infrastructure and Learning Resources",
        "weightage": 100,
        "description": "Physical instructional facilities, modern central library automation, high-speed campus IT networks, and estate maintenance protocols.",
        "subcriteria": [
            {"id": "4.1", "name": "Physical Facilities & Smart Classrooms"},
            {"id": "4.2", "name": "Library as a Learning Resource & ILMS"},
            {"id": "4.3", "name": "IT Infrastructure, Bandwidth & Wi-Fi"},
            {"id": "4.4", "name": "Campus Infrastructure Maintenance"}
        ]
    },
    {
        "id": "Criterion 5",
        "name": "Student Support and Progression",
        "weightage": 140,
        "description": "Scholarships, proctorial mentoring, career placement training, competitive examination coaching, sports/cultural bodies, and active alumni chapters.",
        "subcriteria": [
            {"id": "5.1", "name": "Student Support & Scholarships"},
            {"id": "5.2", "name": "Student Progression & Career Placements"},
            {"id": "5.3", "name": "Student Participation in Sports & Culture"},
            {"id": "5.4", "name": "Alumni Engagement & Contribution"}
        ]
    },
    {
        "id": "Criterion 6",
        "name": "Governance, Leadership and Management",
        "weightage": 100,
        "description": "Institutional vision, strategic plan deployment, faculty empowerment initiatives (FDPs), transparent financial audits, and IQAC quality assurance.",
        "subcriteria": [
            {"id": "6.1", "name": "Institutional Vision and Participative Leadership"},
            {"id": "6.2", "name": "Strategy Development and Perspective Deployment"},
            {"id": "6.3", "name": "Faculty Empowerment Strategies & FDPs"},
            {"id": "6.4", "name": "Financial Management & Resource Mobilization"},
            {"id": "6.5", "name": "Internal Quality Assurance System (IQAC)"}
        ]
    },
    {
        "id": "Criterion 7",
        "name": "Institutional Values and Best Practices",
        "weightage": 100,
        "description": "Gender equity, rooftop solar power, water conservation, waste recycling, clean green campus, distinctiveness, and institutional best practices.",
        "subcriteria": [
            {"id": "7.1", "name": "Institutional Values & Environmental Responsibility"},
            {"id": "7.2", "name": "Best Practices in Institutional Excellence"},
            {"id": "7.3", "name": "Institutional Distinctiveness"}
        ]
    }
]

DEPARTMENTS = [
    {"name": "IQAC", "head": "Dr. Rameshwar Rao", "code": "IQAC"},
    {"name": "Research Cell", "head": "Dr. Meenakshi Sundaram", "code": "RCELL"},
    {"name": "Academic Office", "head": "Dr. K. S. Murthy", "code": "ACAD"},
    {"name": "Training & Placement Cell", "head": "Prof. S. R. V. Prasad", "code": "TPC"},
    {"name": "Student Affairs", "head": "Dr. V. Lalitha Devi", "code": "SAFF"},
    {"name": "Library", "head": "Dr. G. Satyanarayana", "code": "LIB"},
    {"name": "Examination Cell", "head": "Prof. B. Prabhakar", "code": "EXAM"},
    {"name": "Administration", "head": "Sri K. Raghavan, Registrar", "code": "ADMIN"},
    {"name": "CSE Department", "head": "Dr. T. Venkat Reddy", "code": "CSE"},
    {"name": "ECE Department", "head": "Dr. M. Sridevi", "code": "ECE"},
    {"name": "Mechanical Department", "head": "Dr. P. V. Ramana", "code": "MECH"},
    {"name": "Civil Department", "head": "Dr. Ch. Krishna", "code": "CIVIL"},
    {"name": "EEE Department", "head": "Dr. A. Sudhir", "code": "EEE"},
    {"name": "Estate Office", "head": "Er. D. Madhav Rao", "code": "EST"}
]

# Write criteria and departments JSON
with open(os.path.join(METADATA_DIR, "criteria.json"), "w", encoding="utf-8") as f:
    json.dump(CRITERIA, f, indent=2)

with open(os.path.join(METADATA_DIR, "departments.json"), "w", encoding="utf-8") as f:
    json.dump(DEPARTMENTS, f, indent=2)

print("Criteria and Departments metadata saved.")
