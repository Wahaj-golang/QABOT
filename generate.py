from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from typing import List, Dict

def generate_pdf(report_data: Dict, output_path: str = "quality_report.pdf"):
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    flow = []
    
    # Title
    title = Paragraph("Software Quality Assurance Report", styles['Title'])
    flow.append(title)
    flow.append(Spacer(1, 24))
    
    # Code Quality
    quality_text = f"<b>Code Quality Rating:</b> {report_data['code_quality']}"
    flow.append(Paragraph(quality_text, styles['BodyText']))
    flow.append(Spacer(1, 12))
    
    # Tech Stack
    # tech_stack = "".join(report_data['tech_stack'][0][""]) if report_data['tech_stack'] else "No specific tech stack detected"
    tech_text = f"<b>Tech Stack:</b> {report_data['tech_stack']}"
    flow.append(Paragraph(tech_text, styles['BodyText']))
    flow.append(Spacer(1, 12))
    
    # Counts
    counts = [
        ("Total Functions", report_data['total_functions']),
        ("Total Loops", report_data['total_loops']),
        ("Total Classes", report_data['total_classes'])
    ]
    
    for label, value in counts:
        text = f"<b>{label}:</b> {value}"
        flow.append(Paragraph(text, styles['BodyText']))
        flow.append(Spacer(1, 8))
    
    doc.build(flow)