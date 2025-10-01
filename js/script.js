// ---------------------------
// Robust Script for EME Frontend
// ---------------------------

document.addEventListener('DOMContentLoaded', () => {
    // ---------------------------
    // Mobile Menu Toggle
    // ---------------------------
    const menuToggle = document.getElementById('menuToggle');
    const navLinks = document.getElementById('navLinks');

    if (menuToggle && navLinks) {
        // Toggle menu
        menuToggle.addEventListener('click', () => {
            navLinks.classList.toggle('active');
            menuToggle.classList.toggle('active');
        });

        // Close menu on link click
        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                navLinks.classList.remove('active');
                menuToggle.classList.remove('active');
            });
        });
    }

    // ---------------------------
    // Contact Form Submission
    // ---------------------------
    const contactForm = document.getElementById('contactForm');
    const formMessage = document.getElementById('formMessage');

    // Show toast notification
    function showToast(message, type = 'success') {
        if (!formMessage) return;
        formMessage.textContent = message;
        formMessage.className = `form-message ${type}`;
        formMessage.style.display = 'block';

        setTimeout(() => {
            formMessage.style.display = 'none';
        }, 5000);
    }

    if (contactForm) {
        contactForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const formData = {
                name: contactForm.name?.value.trim() || '',
                email: contactForm.email?.value.trim() || '',
                phone: contactForm.phone?.value.trim() || '',
                service: contactForm.service?.value || '',
                message: contactForm.message?.value.trim() || ''
            };

            // Basic validation
            if (!formData.name || !formData.email || !formData.service || !formData.message) {
                showToast('Please fill in all required fields.', 'error');
                return;
            }

            try {
                const response = await fetch('https://eme-backend-3dw0.onrender.com/api/contact', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });

                const data = await response.json().catch(() => ({}));

                if (!response.ok || !data.success) {
                    throw new Error(data.message || 'Failed to send message.');
                }

                showToast(data.message || 'Message sent successfully!', 'success');
                contactForm.reset();

            } catch (err) {
                console.error('Error submitting contact form:', err);
                showToast(err.message || 'An error occurred. Please try again.', 'error');
            }
        });
    }
});
