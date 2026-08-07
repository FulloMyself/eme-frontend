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
    
    const submitBtn = form.querySelector('#submitCV');
    if (submitBtn) {
      submitBtn.textContent = stepNumber === totalSteps ? 'Generate CV' : 'Next →';
    }
    
    currentStep = stepNumber;
  }

  function setupProgressClicks() {
    progressSteps.forEach(step => {
      step.addEventListener('click', () => {
        const stepNumber = parseInt(step.dataset.step);
        if (stepNumber <= currentStep + 1) {
          showStep(stepNumber);
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
              <input type="text" name="jobTitle[]" placeholder="Software Developer">
            </div>
            <div class="cv-field">
              <label>Company *</label>
              <input type="text" name="company[]" placeholder="Tech Corp Ltd">
            </div>
          </div>
          <div class="cv-field-row">
            <div class="cv-field">
              <label>Start Date *</label>
              <input type="month" name="startDate[]">
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
        newEntry.querySelector('.btn-remove-entry').addEventListener('click', () => {
          newEntry.remove();
        });
      });
    }
  }

  function setupEducationButtons() {
    const addBtn = document.getElementById('addEducation');
    const container = document.getElementById('educationContainer');
    let count = 1;

    if (addBtn && container) {
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
              <input type="text" name="qualification[]" placeholder="Bachelor of Science">
            </div>
            <div class="cv-field">
              <label>Institution *</label>
              <input type="text" name="institution[]" placeholder="University">
            </div>
          </div>
          <div class="cv-field">
            <label>Year Completed</label>
            <input type="text" name="yearCompleted[]" placeholder="2020">
          </div>
        `;
        container.appendChild(newEntry);
        newEntry.querySelector('.btn-remove-entry').addEventListener('click', () => {
          newEntry.remove();
        });
      });
    }
  }

  function setupFileInputs() {
    document.querySelectorAll('.file-input').forEach(input => {
      input.addEventListener('change', (e) => {
        const fileName = e.target.files[0]?.name || 'No file chosen';
        const nameSpan = document.getElementById(input.id + 'Name');
        if (nameSpan) nameSpan.textContent = fileName;
      });
    });
  }

  function generateCV() {
    const formData = new FormData(form);
    const submitBtn = document.getElementById('submitCV');
    
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = 'Generating...';
    }
    
    fetch('/create_cv', {
      method: 'POST',
      body: formData,
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(response => {
      // Check if response is OK
      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }
      // Get the text first, then try to parse as JSON
      return response.text();
    })
    .then(text => {
      console.log('Server response:', text);
      try {
        const data = JSON.parse(text);
        if (data.success) {
          window.location.href = data.download_url;
        } else {
          alert('Error: ' + (data.error || 'Failed to generate CV'));
        }
      } catch (e) {
        console.error('JSON parse error:', e);
        alert('Error parsing server response. Check the terminal for errors.');
      }
    })
    .catch(error => {
      console.error('Error:', error);
      alert('Error: ' + error.message + '\n\nMake sure the Flask server is running and check the terminal for Python errors.');
    })
    .finally(() => {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = currentStep === totalSteps ? 'Generate CV' : 'Next →';
      }
    });
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();