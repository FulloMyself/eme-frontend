// script.js
document.addEventListener('DOMContentLoaded', () => {
    const contactForm = document.getElementById('contactForm');
    const formMessage = document.getElementById('formMessage');

    // Show toast notification
    function showToast(message, type = 'success') {
        if (!formMessage) return;

        formMessage.textContent = message;
        formMessage.className = `form-message ${type}`;
        formMessage.style.display = 'block';

        // Hide after 7 seconds
        setTimeout(() => {
            formMessage.style.display = 'none';
        }, 7000);
    }

    if (!contactForm) return;

    contactForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Gather form data
        const formData = {
            name: contactForm.name?.value.trim() || '',
            email: contactForm.email?.value.trim() || '',
            phone: contactForm.phone?.value.trim() || '',
            service: contactForm.service?.value || '',
            message: contactForm.message?.value.trim() || ''
        };

        // Validate required fields
        if (!formData.name || !formData.email || !formData.service || !formData.message) {
            showToast('Please fill all required fields.', 'error');
            return;
        }

        // Disable submit button while sending
        const submitButton = contactForm.querySelector('button[type="submit"]');
        if (submitButton) submitButton.disabled = true;

        try {
            const response = await fetch('https://eme-backend-3dw0.onrender.com/api/contact', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData),
            });

            let data;
            try {
                data = await response.json();
            } catch {
                data = {};
            }

            if (!response.ok) {
                throw new Error(data?.message || `Failed to send message (status ${response.status})`);
            }

            // Success notification
            showToast(data.message || 'Message sent successfully!', 'success');
            contactForm.reset();

        } catch (err) {
            console.error('Error submitting contact form:', err);
            showToast(err.message || 'An error occurred. Please try again later.', 'error');
        } finally {
            if (submitButton) submitButton.disabled = false;
        }
    });
});

// ===== Business Profile Modal =====
document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("profileModal");
  const openBtns = [document.getElementById("openProfile"), document.getElementById("openProfileHero")];
  const closeBtn = document.getElementById("closeProfile");
  const downloadBtn = document.getElementById("downloadProfile");

  openBtns.forEach(btn => {
    if (btn) {
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        modal.style.display = "block";
      });
    }
  });

  closeBtn.addEventListener("click", () => {
    modal.style.display = "none";
  });

  window.addEventListener("click", (e) => {
    if (e.target === modal) modal.style.display = "none";
  });

  // ✅ Trigger direct download of PDF file
  downloadBtn.addEventListener("click", () => {
    const link = document.createElement("a");
    link.href = "assets/Established Media & Enterprises - Business Profile2025.pdf"; // <-- your PDF path
    link.download = "EME-Business-Profile.pdf";    // suggested download filename
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  });
});



