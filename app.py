import os
import sqlite3
from flask import Flask, request, render_template, redirect, url_for, flash, send_file, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime
import cv_generator
import db
import sys

sys.path.insert(0, os.path.dirname(__file__))

app = Flask(__name__)

# Fix for Render's filesystem (ephemeral)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['CV_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'generated_cvs')
app.config['SECRET_KEY'] = 'eme4you-cv-bot-2024'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['CV_FOLDER'] = 'generated_cvs'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# Create necessary folders
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['CV_FOLDER'], exist_ok=True)
os.makedirs('templates', exist_ok=True)

# Initialize database
db.init_db()

# =========================================================
# SPECIFIC ROUTES FIRST (order matters!)
# =========================================================

@app.route('/')
def index():
    """Serve the main website"""
    return send_from_directory('.', 'index.html')

@app.route('/cv-maker')
@app.route('/cv-maker.html')
def cv_maker():
    """Serve the CV Maker page"""
    return send_from_directory('.', 'cv-maker.html')

@app.route('/css/<path:filename>')
def serve_css(filename):
    """Serve CSS files"""
    css_path = os.path.join('css', filename)
    if os.path.exists(css_path):
        return send_from_directory('css', filename)
    return "CSS file not found", 404

@app.route('/js/<path:filename>')
def serve_js(filename):
    """Serve JavaScript files"""
    js_path = os.path.join('js', filename)
    if os.path.exists(js_path):
        return send_from_directory('js', filename)
    return "JS file not found", 404

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    """Serve asset files"""
    asset_path = os.path.join('assets', filename)
    if os.path.exists(asset_path):
        return send_from_directory('assets', filename)
    return "Asset not found", 404

@app.route('/screenshots/<path:filename>')
def serve_screenshots(filename):
    """Serve screenshot files"""
    shot_path = os.path.join('screenshots', filename)
    if os.path.exists(shot_path):
        return send_from_directory('screenshots', filename)
    return "Screenshot not found", 404

# =========================================================
# CV GENERATION ROUTES
# =========================================================

@app.route('/generate-cv', methods=['POST'])
@app.route('/create_cv', methods=['POST'])
def create_cv():
    """Generate CV from form data"""
    import traceback
    
    try:
        print("=" * 50)
        print("CREATE_CV ROUTE CALLED")
        print("Form data:", dict(request.form))
        print("Files:", list(request.files.keys()))
        print("=" * 50)
        
        # 1. Personal Information
        full_name = request.form.get('fullName', request.form.get('full_name', ''))
        email = request.form.get('email', '')
        phone = request.form.get('phone', '')
        location = request.form.get('location', request.form.get('address', ''))
        linkedin = request.form.get('linkedin', '')
        portfolio = request.form.get('portfolio', '')
        
        print(f"Name: {full_name}, Email: {email}")
        
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
            if job_titles[i] and companies[i]:
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
            if degrees[i] and institutions[i]:
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
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_name = secure_filename(full_name.replace(' ', '_')) if full_name else f"user_{timestamp}"
        
        print(f"Safe name: {safe_name}, Timestamp: {timestamp}")
        
        # 7. Generate CV directly (skip database for now)
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
        
        print(f"Generating CV at: {cv_path}")
        
        cv_generator.generate_ats_cv(cv_data, cv_path)
        
        print("CV generated successfully!")
        
        return jsonify({
            'success': True,
            'message': 'CV generated successfully',
            'cv_filename': cv_filename,
            'download_url': f'/download_cv/{cv_filename}'
        })
    
    except Exception as e:
        print("=" * 50)
        print("ERROR IN CREATE_CV:")
        traceback.print_exc()
        print("=" * 50)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/download_cv/<filename>')
def download_cv(filename):
    """Download generated CV"""
    cv_path = os.path.join(app.config['CV_FOLDER'], filename)
    if os.path.exists(cv_path):
        return send_file(cv_path, as_attachment=True, download_name=filename)
    return "CV file not found", 404

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
    if os.path.exists(filename):
        return send_from_directory('.', filename)
    return "File not found", 404

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)