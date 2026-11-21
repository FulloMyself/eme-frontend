import io
import os
import tempfile
import unittest

from docx import Document
from pypdf import PdfReader
from reportlab.pdfgen import canvas

import app as cv_app


class CvFormatTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_cv_folder = cv_app.app.config['CV_FOLDER']
        self.original_upload_folder = cv_app.app.config['UPLOAD_FOLDER']
        cv_app.app.config['CV_FOLDER'] = os.path.join(self.temp_dir.name, 'cvs')
        cv_app.app.config['UPLOAD_FOLDER'] = os.path.join(self.temp_dir.name, 'uploads')
        os.makedirs(cv_app.app.config['CV_FOLDER'])
        os.makedirs(cv_app.app.config['UPLOAD_FOLDER'])
        cv_app.app.config['TESTING'] = True
        self.client = cv_app.app.test_client()

    def tearDown(self):
        cv_app.app.config['CV_FOLDER'] = self.original_cv_folder
        cv_app.app.config['UPLOAD_FOLDER'] = self.original_upload_folder
        cv_app.app.config['TESTING'] = False
        self.temp_dir.cleanup()

    @staticmethod
    def make_attachment():
        attachment = io.BytesIO()
        pdf = canvas.Canvas(attachment)
        pdf.drawString(72, 720, 'Supporting document page')
        pdf.save()
        attachment.seek(0)
        return attachment

    def submission(self, template, output_format, attachment=None):
        data = {
            'fullName': 'Taylor Sample',
            'email': 'taylor@example.com',
            'phone': '+27123456789',
            'cvTemplate': template,
            'outputFormat': output_format,
            'professionalSummary': 'Experienced project coordinator.',
        }
        if attachment:
            data['certifiedId'] = (attachment, 'supporting.pdf')
        return self.client.post(
            '/create_cv',
            data=data,
            content_type='multipart/form-data',
        )

    def test_docx_choice_returns_editable_cv_and_appended_pdf(self):
        response = self.submission(
            'modern', 'docx', self.make_attachment()
        )
        self.assertEqual(response.status_code, 200)
        result = response.get_json()
        response.close()
        self.assertTrue(result['download_url'].endswith('.docx'))
        self.assertIn('combined_pdf_url', result)

        word_response = self.client.get(result['download_url'])
        word_data = word_response.data
        word_response.close()
        document = Document(io.BytesIO(word_data))
        text = '\n'.join(paragraph.text for paragraph in document.paragraphs)
        self.assertIn('TAYLOR SAMPLE', text)

        combined_response = self.client.get(result['combined_pdf_url'])
        combined_data = combined_response.data
        combined_response.close()
        combined_pdf = PdfReader(io.BytesIO(combined_data))
        self.assertEqual(len(combined_pdf.pages), 2)
        self.assertIn(
            'Supporting document page',
            combined_pdf.pages[1].extract_text(),
        )

    def test_pdf_choice_keeps_uploaded_document_appended(self):
        response = self.submission(
            'executive', 'pdf', self.make_attachment()
        )
        self.assertEqual(response.status_code, 200)
        result = response.get_json()
        response.close()
        self.assertTrue(result['download_url'].endswith('.pdf'))
        self.assertNotIn('combined_pdf_url', result)

        pdf_response = self.client.get(result['download_url'])
        pdf_data = pdf_response.data
        pdf_response.close()
        generated_pdf = PdfReader(io.BytesIO(pdf_data))
        self.assertEqual(len(generated_pdf.pages), 2)
        self.assertIn(
            'Supporting document page',
            generated_pdf.pages[1].extract_text(),
        )

    def test_invalid_layout_and_download_format_are_rejected(self):
        for field, value in (
            ('cvTemplate', 'unknown-layout'),
            ('outputFormat', 'unknown-format'),
        ):
            with self.subTest(field=field):
                data = {
                    'fullName': 'Taylor Sample',
                    'email': 'taylor@example.com',
                    'phone': '+27123456789',
                    'cvTemplate': 'classic',
                    'outputFormat': 'pdf',
                }
                data[field] = value
                response = self.client.post('/create_cv', data=data)
                self.assertEqual(response.status_code, 400)
                self.assertFalse(response.get_json()['success'])


if __name__ == '__main__':
    unittest.main()
