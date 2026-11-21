from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.fonts import addMapping
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from xml.sax.saxutils import escape


def _paragraph_text(value):
    return escape(str(value)).replace('\n', '<br/>')

def generate_ats_cv(cv_data, output_path):
    """
    Generate an ATS-compliant CV PDF
    ATS-friendly features:
    - Simple, clean layout
    - Standard fonts
    - No columns, graphics, or tables for critical info
    - Clear section headings
    - Proper keyword placement
    """
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles for ATS compliance
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.black,
        spaceAfter=6,
        fontName='Helvetica-Bold',
        leading=20
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.black,
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold',
        leading=16
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.black,
        spaceAfter=6,
        fontName='Helvetica',
        leading=14
    )
    
    bullet_style = ParagraphStyle(
        'BulletStyle',
        parent=normal_style,
        leftIndent=20,
        bulletIndent=10,
        spaceBefore=2,
        spaceAfter=2
    )
    
    story = []
    
    # Get personal info safely
    personal = cv_data.get('personal_info', {})
    
    # Header - Name
    full_name = personal.get('full_name', 'Your Name')
    story.append(Paragraph(_paragraph_text(full_name.upper()), title_style))
    
    # Contact Information (using plain text for ATS compatibility)
    contact_parts = []
    if personal.get('phone'):
        contact_parts.append(f"Phone: {_paragraph_text(personal['phone'])}")
    if personal.get('email'):
        contact_parts.append(f"Email: {_paragraph_text(personal['email'])}")
    if personal.get('address'):
        contact_parts.append(f"Address: {_paragraph_text(personal['address'])}")
    if personal.get('linkedin'):
        contact_parts.append(f"LinkedIn: {_paragraph_text(personal['linkedin'])}")
    if personal.get('portfolio'):
        contact_parts.append(f"Portfolio: {_paragraph_text(personal['portfolio'])}")
    
    if contact_parts:
        contact_text = " | ".join(contact_parts)
        story.append(Paragraph(contact_text, normal_style))
    
    story.append(Spacer(1, 0.2 * inch))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.black))
    story.append(Spacer(1, 0.2 * inch))
    
    # Professional Summary
    professional_summary = cv_data.get('professional_summary', '')
    if professional_summary and professional_summary.strip():
        story.append(Paragraph("PROFESSIONAL SUMMARY", heading_style))
        story.append(Paragraph(_paragraph_text(professional_summary.strip()), normal_style))
        story.append(Spacer(1, 0.1 * inch))
    
    # Work Experience
    work_experience = cv_data.get('work_experience', [])
    if work_experience:
        story.append(Paragraph("WORK EXPERIENCE", heading_style))
        for exp in work_experience:
            if not isinstance(exp, dict):
                continue
                
            # Job title and company
            title = exp.get('title', '')
            company = exp.get('company', '')
            
            if title:
                title_text = f"<b>{_paragraph_text(title)}</b>"
                if company:
                    title_text += f" | {_paragraph_text(company)}"
                story.append(Paragraph(title_text, normal_style))
            
            # Dates
            start_date = exp.get('start_date', '')
            end_date = exp.get('end_date', '')
            
            if start_date or end_date:
                end_display = end_date if end_date else 'Present'
                date_text = f"{_paragraph_text(start_date)} - {_paragraph_text(end_display)}" if start_date else _paragraph_text(end_display)
                story.append(Paragraph(date_text, normal_style))
            
            # Responsibilities
            responsibilities = exp.get('responsibilities', '')
            if responsibilities and responsibilities.strip():
                # Split by newlines and create bullet points
                lines = responsibilities.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if line:
                        # Remove leading bullet characters if present
                        clean_line = line.lstrip('•-*> ').strip()
                        if clean_line:
                            story.append(Paragraph(f"• {_paragraph_text(clean_line)}", bullet_style))
            
            story.append(Spacer(1, 0.1 * inch))
    
    # Education
    education = cv_data.get('education', [])
    if education:
        story.append(Paragraph("EDUCATION", heading_style))
        for edu in education:
            if not isinstance(edu, dict):
                continue
                
            degree = edu.get('degree', '')
            institution = edu.get('institution', '')
            grad_year = edu.get('grad_year', '')
            
            if degree:
                degree_text = f"<b>{_paragraph_text(degree)}</b>"
                if institution:
                    degree_text += f" - {_paragraph_text(institution)}"
                story.append(Paragraph(degree_text, normal_style))
            
            if grad_year:
                story.append(Paragraph(f"Graduated: {_paragraph_text(grad_year)}", normal_style))
            
            story.append(Spacer(1, 0.1 * inch))
    
    # Skills
    skills = cv_data.get('skills', [])
    if skills:
        story.append(Paragraph("SKILLS", heading_style))
        skills_text = _paragraph_text(", ".join(skills))
        story.append(Paragraph(skills_text, normal_style))
        story.append(Spacer(1, 0.1 * inch))
    
    # Certifications
    certifications = cv_data.get('certifications', [])
    if certifications:
        story.append(Paragraph("CERTIFICATIONS", heading_style))
        for cert in certifications:
            if not isinstance(cert, dict):
                continue
                
            cert_name = cert.get('name', '')
            issuer = cert.get('issuer', '')
            year = cert.get('year', '')
            
            if cert_name:
                cert_text = f"<b>{_paragraph_text(cert_name)}</b>"
                if issuer:
                    cert_text += f" | {_paragraph_text(issuer)}"
                if year:
                    cert_text += f" | {_paragraph_text(year)}"
                story.append(Paragraph(cert_text, normal_style))
        story.append(Spacer(1, 0.1 * inch))
    
    # Languages
    languages = cv_data.get('languages', [])
    if languages:
        story.append(Paragraph("LANGUAGES", heading_style))
        languages_text = _paragraph_text(", ".join(languages))
        story.append(Paragraph(languages_text, normal_style))
    
    # Build PDF
    try:
        doc.build(story)
        print(f"✅ ATS-Compliant CV generated: {output_path}")
        return True
    except Exception as e:
        print(f"❌ Error generating CV: {str(e)}")
        raise