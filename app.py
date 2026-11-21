import os
import tempfile
from flask import Flask, request, render_template, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime
from pypdf import PdfReader, PdfWriter
from pypdf.errors import PdfReadError
from PIL import Image, UnidentifiedImageError
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
import cv_generator
import db
import sys

sys.path.insert(0, os.path.dirname(__file__))

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'uploads')
app.config['CV_FOLDER'] = os.path.join(BASE_DIR, 'generated_cvs')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'eme4you-cv-bot-2024')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# Create necessary folders
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['CV_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'templates'), exist_ok=True)

# Initialize database
db.init_db()

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({'success': False, 'error': 'Uploaded files exceed the 16MB request limit.'}), 413

# =========================================================
# SPECIFIC ROUTES FIRST (order matters!)
# =========================================================

@app.route('/')
def index():
    """Serve the main website"""
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/cv-maker')
@app.route('/cv-maker.html')
def cv_maker():
    """Serve the CV Maker page"""
    return send_from_directory(BASE_DIR, 'cv-maker.html')

@app.route('/css/<path:filename>')
def serve_css(filename):
    """Serve CSS files"""
    css_path = os.path.join(BASE_DIR, 'css', filename)
    if os.path.exists(css_path):
        return send_from_directory(os.path.join(BASE_DIR, 'css'), filename)
    return "CSS file not found", 404

@app.route('/js/<path:filename>')
def serve_js(filename):
    """Serve JavaScript files"""
    js_path = os.path.join(BASE_DIR, 'js', filename)
    if os.path.exists(js_path):
        return send_from_directory(os.path.join(BASE_DIR, 'js'), filename)
    return "JS file not found", 404

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    """Serve asset files"""
    asset_path = os.path.join(BASE_DIR, 'assets', filename)
    if os.path.exists(asset_path):
        return send_from_directory(os.path.join(BASE_DIR, 'assets'), filename)
    return "Asset not found", 404

@app.route('/screenshots/<path:filename>')
def serve_screenshots(filename):
    """Serve screenshot files"""
    shot_path = os.path.join(BASE_DIR, 'screenshots', filename)
    if os.path.exists(shot_path):
        return send_from_directory(os.path.join(BASE_DIR, 'screenshots'), filename)
    return "Screenshot not found", 404

# =========================================================
# CV GENERATION ROUTES
# =========================================================

def _save_uploaded_documents(temp_dir):
    documents = []
    for field_name, label in (
        ('certifiedId', 'Certified ID'),
        ('proofOfResidence', 'Proof of Residence'),
    ):
        upload = request.files.get(field_name)
        if not upload or not upload.filename:
            continue

        filename = secure_filename(upload.filename)
        extension = os.path.splitext(filename)[1].lower()
        if extension not in ('.pdf', '.jpg', '.jpeg', '.png'):
            raise ValueError(f'{label} must be a PDF, JPG, or PNG file.')

        path = os.path.join(temp_dir, field_name + extension)
        upload.save(path)
        if os.path.getsize(path) > 5 * 1024 * 1024:
            raise ValueError(f'{label} must be 5MB or smaller.')

        if extension == '.pdf':
            try:
                reader = PdfReader(path)
                if reader.is_encrypted:
                    raise ValueError(f'{label} PDF must not be password-protected.')
                if not reader.pages:
                    raise ValueError(f'{label} PDF must contain at least one page.')
            except PdfReadError as error:
                raise ValueError(f'{label} must be a valid PDF.') from error
        else:
            try:
                with Image.open(path) as image:
                    expected_format = 'JPEG' if extension in ('.jpg', '.jpeg') else 'PNG'
                    if image.format != expected_format:
                        raise ValueError(f'{label} file contents do not match its extension.')
                    image.verify()
            except (UnidentifiedImageError, OSError) as error:
                raise ValueError(f'{label} must be a valid image.') from error

        documents.append((label, extension, path))

    return documents


def _image_to_pdf(image_path, output_path):
    image = ImageReader(image_path)
    image_width, image_height = image.getSize()
    page_width, page_height = A4
    scale = min((page_width - 72) / image_width, (page_height - 72) / image_height)
    width = image_width * scale
    height = image_height * scale
    pdf = canvas.Canvas(output_path, pagesize=A4)
    pdf.drawImage(
        image,
        (page_width - width) / 2,
        (page_height - height) / 2,
        width=width,
        height=height,
    )
    pdf.save()


def _combine_documents(cv_path, documents, temp_dir, output_path):
    writer = PdfWriter()
    writer.append(PdfReader(cv_path))

    for index, (label, extension, path) in enumerate(documents):
        document_path = path
        if extension != '.pdf':
            document_path = os.path.join(temp_dir, f'document_{index}.pdf')
            _image_to_pdf(path, document_path)

        try:
            reader = PdfReader(document_path)
            if reader.is_encrypted:
                raise ValueError(f'{label} PDF must not be password-protected.')
            writer.append(reader)
        except PdfReadError as error:
            raise ValueError(f'{label} must be a valid PDF.') from error

    with open(output_path, 'wb') as output_file:
        writer.write(output_file)


@app.route('/generate-cv', methods=['POST'])
@app.route('/create_cv', methods=['POST'])
def create_cv():
    """Generate CV from form data"""
    import traceback
    
    try:
        # 1. Personal Information
        full_name = request.form.get('fullName', request.form.get('full_name', '')).strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        if not full_name or not email or not phone:
            return jsonify({'success': False, 'error': 'Name, email, and phone are required.'}), 400

        location = request.form.get('location', request.form.get('address', ''))
        linkedin = request.form.get('linkedin', '')
        portfolio = request.form.get('portfolio', '')

        personal_info = {
            'full_name': full_name,
            'email': email,
            'phone': phone,
            'address': location,
            'linkedin': linkedin,
            'portfolio': portfolio
        }
        
        # 2. Professional Summary
        professional_summary = request.form.get('professionalSummary', request.form.get('professional_summary', ''))
        
        # 3. Work Experience
        job_titles = request.form.getlist('jobTitle[]') or request.form.getlist('job_title[]')
        companies = request.form.getlist('company[]')
        start_dates = request.form.getlist('startDate[]') or request.form.getlist('start_date[]')
        end_dates = request.form.getlist('endDate[]') or request.form.getlist('end_date[]')
        responsibilities = request.form.getlist('responsibilities[]')
        
        work_experience = []
        for i in range(len(job_titles)):
            if job_titles[i] and i < len(companies) and companies[i]:
                work_experience.append({
                    'title': job_titles[i],
                    'company': companies[i],
                    'start_date': start_dates[i] if i < len(start_dates) else '',
                    'end_date': end_dates[i] if i < len(end_dates) else '',
                    'responsibilities': responsibilities[i] if i < len(responsibilities) else ''
                })
        
        # 4. Education
        degrees = request.form.getlist('qualification[]') or request.form.getlist('degree[]')
        institutions = request.form.getlist('institution[]')
        grad_years = request.form.getlist('yearCompleted[]') or request.form.getlist('grad_year[]')
        
        education = []
        for i in range(len(degrees)):
            if degrees[i] and i < len(institutions) and institutions[i]:
                education.append({
                    'degree': degrees[i],
                    'institution': institutions[i],
                    'grad_year': grad_years[i] if i < len(grad_years) else ''
                })
        
        # 5. Skills
        technical_skills = request.form.get('technicalSkills', request.form.get('skills', ''))
        soft_skills = request.form.get('softSkills', '')
        all_skills = technical_skills + ',' + soft_skills
        skills = [s.strip() for s in all_skills.split(',') if s.strip()]
        
        # 6. Generate timestamp and safe name
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        safe_name = secure_filename(full_name.replace(' ', '_')) or f"user_{timestamp}"
        
        # 7. Generate the CV and append any supplied documents.
        cv_data = {
            'personal_info': personal_info,
            'professional_summary': professional_summary,
            'work_experience': work_experience,
            'education': education,
            'skills': skills,
            'certifications': [],
            'languages': []
        }
        
        cv_filename = f"{safe_name}_{timestamp}.pdf"
        cv_path = os.path.join(app.config['CV_FOLDER'], cv_filename)

        with tempfile.TemporaryDirectory(dir=app.config['UPLOAD_FOLDER']) as temp_dir:
            documents = _save_uploaded_documents(temp_dir)
            if documents:
                source_cv_path = os.path.join(temp_dir, 'cv.pdf')
                combined_path = os.path.join(temp_dir, 'combined.pdf')
                cv_generator.generate_ats_cv(cv_data, source_cv_path)
                _combine_documents(source_cv_path, documents, temp_dir, combined_path)
                os.replace(combined_path, cv_path)
            else:
                cv_generator.generate_ats_cv(cv_data, cv_path)
        
        return jsonify({
            'success': True,
            'message': 'CV generated successfully',
            'cv_filename': cv_filename,
            'download_url': f'/download_cv/{cv_filename}'
        })
    
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/download_cv/<filename>')
def download_cv(filename):
    """Download generated CV"""
    return send_from_directory(app.config['CV_FOLDER'], filename, as_attachment=True)

@app.route('/admin')
def admin():
    """Admin dashboard"""
    conn = db.get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users ORDER BY submission_date DESC')
    users = cursor.fetchall()
    conn.close()
    return render_template('admin.html', users=users)

# =========================================================
# GENERIC STATIC FILE ROUTE (MUST BE LAST!)
# =========================================================

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve any other static files"""
    if os.path.exists(os.path.join(BASE_DIR, filename)):
        return send_from_directory(BASE_DIR, filename)
    return "File not found", 404

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)