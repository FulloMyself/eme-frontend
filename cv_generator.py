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
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor


def _paragraph_text(value):
    return escape(str(value)).replace('\n', '<br/>')

CV_TEMPLATES = {
    'classic': {
        'accent': '#000000',
        'title_color': '#000000',
        'title_size': 16,
        'title_alignment': 0,
        'contact_alignment': 0,
        'margin': 72,
    },
    'modern': {
        'accent': '#0B6E75',
        'title_color': '#123B55',
        'title_size': 22,
        'title_alignment': 0,
        'contact_alignment': 0,
        'margin': 54,
    },
    'executive': {
        'accent': '#17365D',
        'title_color': '#17365D',
        'title_size': 22,
        'title_alignment': 1,
        'contact_alignment': 1,
        'margin': 66,
    },
}


def _template_config(template):
    try:
        return CV_TEMPLATES[template]
    except KeyError as error:
        raise ValueError('Choose a valid CV layout.') from error


def generate_ats_cv(cv_data, output_path, template='classic'):
    """
    Generate an ATS-compliant CV PDF
    ATS-friendly features:
    - Simple, clean layout
    - Standard fonts
    - No columns, graphics, or tables for critical info
    - Clear section headings
    - Proper keyword placement
    """
    template_config = _template_config(template)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=template_config['margin'],
        leftMargin=template_config['margin'],
        topMargin=template_config['margin'],
        bottomMargin=template_config['margin']
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles for ATS compliance
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=template_config['title_size'],
        textColor=colors.HexColor(template_config['title_color']),
        spaceAfter=6,
        fontName='Helvetica-Bold',
        leading=template_config['title_size'] + 4,
        alignment=template_config['title_alignment']
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor(template_config['accent']),
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
    contact_style = ParagraphStyle(
        'CustomContact',
        parent=normal_style,
        alignment=template_config['contact_alignment']
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
        story.append(Paragraph(contact_text, contact_style))
    
    story.append(Spacer(1, 0.2 * inch))
    story.append(HRFlowable(
        width="100%",
        thickness=1,
        color=colors.HexColor(template_config['accent'])
    ))
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
        print(f"ATS-compliant CV generated: {output_path}")
        return True
    except Exception as e:
        print(f"Error generating CV: {str(e)}")
        raise


def generate_docx_cv(cv_data, output_path, template='classic'):
    template_config = _template_config(template)
    accent = RGBColor.from_string(template_config['accent'].lstrip('#'))
    alignment = (
        WD_ALIGN_PARAGRAPH.CENTER
        if template_config['title_alignment']
        else WD_ALIGN_PARAGRAPH.LEFT
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    document = Document()
    section = document.sections[0]
    margin = Inches(template_config['margin'] / 72)
    section.top_margin = margin
    section.bottom_margin = margin
    section.left_margin = margin
    section.right_margin = margin

    normal_style = document.styles['Normal']
    normal_style.font.name = 'Arial'
    normal_style.font.size = Pt(10)

    personal = cv_data.get('personal_info', {})
    name = document.add_paragraph()
    name.alignment = alignment
    name.paragraph_format.space_after = Pt(4)
    name_run = name.add_run(str(personal.get('full_name', 'Your Name')).upper())
    name_run.bold = True
    name_run.font.name = 'Arial'
    name_run.font.size = Pt(template_config['title_size'])
    name_run.font.color.rgb = RGBColor.from_string(
        template_config['title_color'].lstrip('#')
    )

    contact_parts = [
        f'{label}: {personal[key]}'
        for key, label in (
            ('phone', 'Phone'),
            ('email', 'Email'),
            ('address', 'Address'),
            ('linkedin', 'LinkedIn'),
            ('portfolio', 'Portfolio'),
        )
        if personal.get(key)
    ]
    if contact_parts:
        contact = document.add_paragraph(' | '.join(contact_parts))
        contact.alignment = alignment
        contact.paragraph_format.space_after = Pt(12)

    def add_section(title):
        paragraph = document.add_paragraph()
        paragraph.paragraph_format.space_before = Pt(10)
        paragraph.paragraph_format.space_after = Pt(4)
        run = paragraph.add_run(title.upper())
        run.bold = True
        run.font.name = 'Arial'
        run.font.size = Pt(12)
        run.font.color.rgb = accent

    summary = cv_data.get('professional_summary', '')
    if summary and summary.strip():
        add_section('Professional Summary')
        document.add_paragraph(summary.strip())

    work_experience = cv_data.get('work_experience', [])
    if work_experience:
        add_section('Work Experience')
        for experience in work_experience:
            if not isinstance(experience, dict):
                continue
            title = experience.get('title', '')
            company = experience.get('company', '')
            if title or company:
                paragraph = document.add_paragraph()
                run = paragraph.add_run(
                    f'{title}{f" | {company}" if company else ""}'
                )
                run.bold = True
            start_date = experience.get('start_date', '')
            end_date = experience.get('end_date', '') or 'Present'
            if start_date or experience.get('end_date'):
                document.add_paragraph(
                    f'{start_date} - {end_date}' if start_date else end_date
                )
            responsibilities = experience.get('responsibilities', '')
            if responsibilities:
                for line in responsibilities.strip().splitlines():
                    clean_line = line.lstrip('•-*> ').strip()
                    if clean_line:
                        document.add_paragraph(clean_line, style='List Bullet')

    education = cv_data.get('education', [])
    if education:
        add_section('Education')
        for item in education:
            if not isinstance(item, dict):
                continue
            degree = item.get('degree', '')
            institution = item.get('institution', '')
            if degree or institution:
                paragraph = document.add_paragraph()
                run = paragraph.add_run(
                    f'{degree}{f" - {institution}" if institution else ""}'
                )
                run.bold = True
            if item.get('grad_year'):
                document.add_paragraph(f"Graduated: {item['grad_year']}")

    skills = cv_data.get('skills', [])
    if skills:
        add_section('Skills')
        document.add_paragraph(', '.join(skills))

    certifications = cv_data.get('certifications', [])
    if certifications:
        add_section('Certifications')
        for certification in certifications:
            if not isinstance(certification, dict):
                continue
            details = [
                certification.get('name', ''),
                certification.get('issuer', ''),
                certification.get('year', ''),
            ]
            text = ' | '.join(value for value in details if value)
            if text:
                document.add_paragraph(text)

    languages = cv_data.get('languages', [])
    if languages:
        add_section('Languages')
        document.add_paragraph(', '.join(languages))

    document.save(output_path)