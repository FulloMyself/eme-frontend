// CV Maker - Standalone Script
(function() {
  let currentStep = 1;
  const totalSteps = 5;
  let form, steps, progressSteps, prevBtn;

  function init() {
    form = document.getElementById('cvForm');
    steps = document.querySelectorAll('.form-step');
    progressSteps = document.querySelectorAll('.progress-step');
    prevBtn = document.getElementById('prevStep');
    
    if (!form) {
      console.error('CV Form not found');
      return;
    }
    
    setupProgressClicks();
    setupPrevButton();
    setupSubmitButton();
    setupExperienceButtons();
    setupEducationButtons();
    setupFileInputs();
    form.addEventListener('input', updateReviewWhenVisible);
    form.addEventListener('change', updateReviewWhenVisible);
    form.addEventListener('submit', event => event.preventDefault());
    
    showStep(1);
    console.log('CV Maker initialized successfully');
  }

  function showStep(stepNumber) {
    if (!steps.length) return;
    
    steps.forEach(step => step.classList.remove('active'));
    progressSteps.forEach(p => p.classList.remove('active'));
    
    const targetStep = document.querySelector(`.form-step[data-step="${stepNumber}"]`);
    if (targetStep) {
      targetStep.classList.add('active');
    }
    
    const targetProgress = document.querySelector(`.progress-step[data-step="${stepNumber}"]`);
    if (targetProgress) {
      targetProgress.classList.add('active');
    }
    
    progressSteps.forEach(p => {
      const step = parseInt(p.dataset.step);
      if (step < stepNumber) {
        p.classList.add('completed');
      } else if (step > stepNumber) {
        p.classList.remove('completed');
      }
    });
    
    if (prevBtn) {
      prevBtn.style.display = stepNumber === 1 ? 'none' : 'inline-flex';
    }
    
    const submitLabel = document.getElementById('submitLabel');
    if (submitLabel) {
      submitLabel.textContent = stepNumber === totalSteps ? 'Generate CV' : 'Next →';
    }
    
    currentStep = stepNumber;
    if (currentStep === totalSteps) renderPreview();
  }

  function validateCurrentStep() {
    const activeStep = document.querySelector(`.form-step[data-step="${currentStep}"]`);
    if (!activeStep) return true;

    const invalidField = Array.from(activeStep.querySelectorAll('input, textarea, select'))
      .find(field => !field.disabled && !field.checkValidity());
    if (invalidField) {
      invalidField.reportValidity();
      return false;
    }

    return true;
  }

  function setupProgressClicks() {
    progressSteps.forEach(step => {
      step.addEventListener('click', () => {
        const stepNumber = parseInt(step.dataset.step);
        if (stepNumber < currentStep) {
          showStep(stepNumber);
          return;
        }

        while (currentStep < stepNumber) {
          if (!validateCurrentStep()) return;
          showStep(currentStep + 1);
        }
      });
    });
  }

  function setupPrevButton() {
    if (prevBtn) {
      prevBtn.addEventListener('click', () => {
        if (currentStep > 1) {
          showStep(currentStep - 1);
        }
      });
    }
  }

  function setupSubmitButton() {
    const submitBtn = document.getElementById('submitCV');
    if (submitBtn) {
      submitBtn.addEventListener('click', () => {
        if (currentStep < totalSteps) {
          if (!validateCurrentStep()) return;
          showStep(currentStep + 1);
        } else {
          generateCV();
        }
      });
    }
  }

  function setupExperienceButtons() {
    const addBtn = document.getElementById('addExperience');
    const container = document.getElementById('experienceContainer');
    let count = 1;

    if (addBtn && container) {
      container.addEventListener('click', event => {
        const removeButton = event.target.closest('.btn-remove-entry');
        if (removeButton) removeButton.closest('.experience-entry').remove();
      });

      addBtn.addEventListener('click', () => {
        count++;
        const newEntry = document.createElement('div');
        newEntry.className = 'experience-entry';
        newEntry.innerHTML = `
          <div class="entry-header">
            <span class="entry-number">${String(count).padStart(2, '0')}</span>
            <button type="button" class="btn-remove-entry">×</button>
          </div>
          <div class="cv-field-row">
            <div class="cv-field">
              <label>Job Title *</label>
              <input type="text" name="jobTitle[]" required placeholder="Software Developer">
            </div>
            <div class="cv-field">
              <label>Company *</label>
              <input type="text" name="company[]" required placeholder="Tech Corp Ltd">
            </div>
          </div>
          <div class="cv-field-row">
            <div class="cv-field">
              <label>Start Date *</label>
              <input type="month" name="startDate[]" required>
            </div>
            <div class="cv-field">
              <label>End Date</label>
              <input type="month" name="endDate[]">
            </div>
          </div>
          <div class="cv-field">
            <label>Responsibilities</label>
            <textarea name="responsibilities[]" rows="3" placeholder="• Achievement 1&#10;• Achievement 2"></textarea>
          </div>
        `;
        container.appendChild(newEntry);
      });
    }
  }

  function setupEducationButtons() {
    const addBtn = document.getElementById('addEducation');
    const container = document.getElementById('educationContainer');
    let count = 1;

    if (addBtn && container) {
      container.addEventListener('click', event => {
        const removeButton = event.target.closest('.btn-remove-entry');
        if (removeButton) removeButton.closest('.education-entry').remove();
      });

      addBtn.addEventListener('click', () => {
        count++;
        const newEntry = document.createElement('div');
        newEntry.className = 'education-entry';
        newEntry.innerHTML = `
          <div class="entry-header">
            <span class="entry-number">${String(count).padStart(2, '0')}</span>
            <button type="button" class="btn-remove-entry">×</button>
          </div>
          <div class="cv-field-row">
            <div class="cv-field">
              <label>Qualification *</label>
              <input type="text" name="qualification[]" required placeholder="Bachelor of Science">
            </div>
            <div class="cv-field">
              <label>Institution *</label>
              <input type="text" name="institution[]" required placeholder="University">
            </div>
          </div>
          <div class="cv-field">
            <label>Year Completed</label>
            <input type="text" name="yearCompleted[]" placeholder="2020">
          </div>
        `;
        container.appendChild(newEntry);
      });
    }
  }

  function setupFileInputs() {
    document.querySelectorAll('.file-input').forEach(input => {
      input.addEventListener('change', (e) => {
        const file = e.target.files[0];
        const nameSpan = document.getElementById(input.id + 'Name');
        input.setCustomValidity('');
        if (file && file.size > 5 * 1024 * 1024) {
          input.setCustomValidity('Each document must be 5MB or smaller.');
        }
        if (nameSpan) {
          nameSpan.textContent = input.validationMessage || (file ? file.name : 'No file chosen');
        }
      });
    });
  }

  function updateReviewWhenVisible() {
    const error = document.getElementById('cvFormError');
    if (error) error.textContent = '';
    if (currentStep === totalSteps) renderPreview();
  }

  function addPreviewText(parent, tagName, text, className) {
    if (!text) return;
    const element = document.createElement(tagName);
    if (className) element.className = className;
    element.textContent = text;
    parent.appendChild(element);
  }

  function addPreviewSection(parent, title, values) {
    const entries = values.filter(Boolean);
    if (!entries.length) return;
    addPreviewText(parent, 'h3', title);
    entries.forEach(value => addPreviewText(parent, 'p', value));
  }

  function renderPreview() {
    const preview = document.getElementById('cvPreview');
    if (!preview) return;
    preview.innerHTML = '';

    const formData = new FormData(form);
    addPreviewText(preview, 'h2', formData.get('fullName') || 'Your Name');
    addPreviewText(preview, 'p', [
      formData.get('email'),
      formData.get('phone'),
      formData.get('location'),
      formData.get('linkedin'),
      formData.get('portfolio')
    ].filter(Boolean).join(' · '));
    addPreviewSection(preview, 'Professional Summary', [formData.get('professionalSummary')]);

    const experience = Array.from(document.querySelectorAll('.experience-entry'))
      .map(entry => {
        const title = entry.querySelector('[name="jobTitle[]"]').value;
        const company = entry.querySelector('[name="company[]"]').value;
        const start = entry.querySelector('[name="startDate[]"]').value;
        const end = entry.querySelector('[name="endDate[]"]').value || 'Present';
        const responsibilities = entry.querySelector('[name="responsibilities[]"]').value;
        const lines = [title && company ? `${title} — ${company}` : title || company];
        if (start) lines.push(`${start} – ${end}`);
        if (responsibilities) lines.push(responsibilities);
        return lines.filter(Boolean).join('\n');
      });
    addPreviewSection(preview, 'Work Experience', experience);

    const education = Array.from(document.querySelectorAll('.education-entry'))
      .map(entry => {
        const qualification = entry.querySelector('[name="qualification[]"]').value;
        const institution = entry.querySelector('[name="institution[]"]').value;
        const year = entry.querySelector('[name="yearCompleted[]"]').value;
        return [qualification && institution ? `${qualification} — ${institution}` : qualification || institution, year]
          .filter(Boolean).join(' · ');
      });
    addPreviewSection(preview, 'Education', education);
    addPreviewSection(preview, 'Technical Skills', [formData.get('technicalSkills')]);
    addPreviewSection(preview, 'Soft Skills', [formData.get('softSkills')]);

    const documents = Array.from(document.querySelectorAll('.file-input'))
      .map(input => input.files[0] && input.files[0].name)
      .filter(Boolean);
    addPreviewSection(preview, 'Documents to append', documents);
  }

  function generateCV() {
    const formData = new FormData(form);
    const submitBtn = document.getElementById('submitCV');
    const formError = document.getElementById('cvFormError');
    if (formError) formError.textContent = '';
    
    if (submitBtn) {
      submitBtn.disabled = true;
    }
    const submitLabel = document.getElementById('submitLabel');
    if (submitLabel) submitLabel.textContent = 'Generating...';
    
    fetch('/create_cv', {
      method: 'POST',
      body: formData,
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(async response => {
      const data = await response.json();
      if (!response.ok || !data.success) {
        throw new Error(data.error || `Server error: ${response.status}`);
      }
      window.location.href = data.download_url;
    })
    .catch(requestError => {
      console.error('Error:', requestError);
      if (formError) formError.textContent = requestError.message;
    })
    .finally(() => {
      if (submitBtn) {
        submitBtn.disabled = false;
      }
      if (submitLabel) submitLabel.textContent = 'Generate CV';
    });
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();