// ===============================
// CONTACT FORM HANDLING
// ===============================
document.addEventListener("DOMContentLoaded", () => {
  const contactForm = document.getElementById("contactForm");
  const formMessage = document.getElementById("formMessage");

  // Show toast notification
  function showToast(message, type = "success") {
    if (!formMessage) return;

    formMessage.textContent = message;
    formMessage.className = `form-message ${type}`;
    formMessage.style.display = "block";

    // Hide after 7 seconds
    setTimeout(() => {
      formMessage.style.display = "none";
    }, 7000);
  }

  if (contactForm) {
    contactForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      // Gather form data
      const formData = {
        name: contactForm.name?.value.trim() || "",
        email: contactForm.email?.value.trim() || "",
        phone: contactForm.phone?.value.trim() || "",
        service: contactForm.service?.value || "",
        message: contactForm.message?.value.trim() || "",
      };

      // Validate required fields
      if (!formData.name || !formData.email || !formData.service || !formData.message) {
        showToast("Please fill all required fields.", "error");
        return;
      }

      // Disable submit button while sending
      const submitButton = contactForm.querySelector('button[type="submit"]');
      if (submitButton) submitButton.disabled = true;

      try {
        const response = await fetch("https://eme-backend-3dw0.onrender.com/api/contact", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(formData),
        });

        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
          throw new Error(data?.message || `Failed to send message (status ${response.status})`);
        }

        showToast(data.message || "Message sent successfully!", "success");
        contactForm.reset();
      } catch (err) {
        console.error("Error submitting contact form:", err);
        showToast(err.message || "An error occurred. Please try again later.", "error");
      } finally {
        if (submitButton) submitButton.disabled = false;
      }
    });
  }
});

// ===============================
// BUSINESS PROFILE MODAL HANDLING
// ===============================
document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("profileModal");
  const openBtns = [
    document.getElementById("openProfile"),
    document.getElementById("openProfileHero"),
  ];
  const closeBtn = document.getElementById("closeProfile");
  const downloadBtn = document.getElementById("downloadProfile");

  // SAFETY: Exit if modal not found
  if (!modal) return;

  // Open modal
  openBtns.forEach((btn) => {
    if (btn) {
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        modal.classList.add("show");
      });
    }
  });

  // Close modal (with fade-out transition)
  if (closeBtn) {
    closeBtn.addEventListener("click", () => {
      modal.classList.remove("show");
    });
  }

  // Close when clicking outside modal content
  window.addEventListener("click", (e) => {
    if (e.target.classList.contains("modal")) {
      e.target.classList.remove("show");
    }
  });


  // ✅ Direct PDF Download
  if (downloadBtn) {
    downloadBtn.addEventListener("click", () => {
      const link = document.createElement("a");
      link.href = "assets/Established Media & Enterprises - Business Profile2025.pdf"; // path to your file
      link.download = "EME-Business-Profile.pdf";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    });
  }
});
