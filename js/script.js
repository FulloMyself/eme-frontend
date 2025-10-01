contactForm.addEventListener('submit', async (e) => {
    e.preventDefault(); // prevent default form submission

    // Gather form data
    const formData = {
        name: contactForm.name.value,
        email: contactForm.email.value,
        phone: contactForm.phone.value,
        service: contactForm.service.value,
        message: contactForm.message.value
    };

    try {
        const response = await fetch('https://your-backend.com/api/contact', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (response.ok) {
            showToast('Message sent successfully!', 'success');
            contactForm.reset();
        } else {
            showToast(data.message || 'Failed to send message.', 'error');
        }
    } catch (err) {
        console.error(err);
        showToast('An error occurred. Please try again.', 'error');
    }
});

// ---------------------------
// Mobile Menu Toggle
// ---------------------------
const menuToggle = document.getElementById('menuToggle');
const navLinks = document.getElementById('navLinks');

menuToggle.addEventListener('click', () => {
    navLinks.classList.toggle('active');
    menuToggle.classList.toggle('active');
});

// Close menu when clicking on a link
navLinks.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
        navLinks.classList.remove('active');
        menuToggle.classList.remove('active');
    });
});

// ---------------------------
// Contact Form Submission
// ---------------------------
const contactForm = document.getElementById('contactForm');
const formMessage = document.getElementById('formMessage');

// Function to show toast notification
function showToast(message, type = 'success') {
    formMessage.textContent = message;
    formMessage.className = `form-message ${type}`;
    formMessage.style.display = 'block';
    setTimeout(() => {
        formMessage.style.display = 'none';
    }, 5000);
}

contactForm.addEventListener('submit', async (e) => {
    e.preventDefault(); // Prevent default form submission

    // Gather form data
    const formData = {
        name: contactForm.name.value.trim(),
        email: contactForm.email.value.trim(),
        phone: contactForm.phone.value.trim(),
        service: contactForm.service.value,
        message: contactForm.message.value.trim()
    };

    // Basic front-end validation
    if (!formData.name || !formData.email || !formData.service || !formData.message) {
        showToast('Please fill in all required fields.', 'error');
        return;
    }

    try {
        // Update this URL to your actual deployed backend
        const response = await fetch('https://your-backend-url.onrender.com/api/contact', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (response.ok && data.success) {
            showToast(data.message || 'Message sent successfully!', 'success');
            contactForm.reset();
        } else {
            showToast(data.message || 'Failed to send message.', 'error');
        }
    } catch (err) {
        console.error('Error submitting contact form:', err);
        showToast('An error occurred. Please try again.', 'error');
    }
});
