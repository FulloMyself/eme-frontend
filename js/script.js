document.addEventListener("DOMContentLoaded", () => {
  // =========================================================
  // MOBILE MENU TOGGLE
  // =========================================================
  const menuToggle = document.getElementById("menuToggle");
  const navLinks = document.getElementById("navLinks");
  
  if (menuToggle && navLinks) {
    menuToggle.addEventListener("click", () => {
      menuToggle.classList.toggle("active");
      navLinks.classList.toggle("active");
    });
    
    navLinks.querySelectorAll("a").forEach(a => a.addEventListener("click", () => {
      menuToggle.classList.remove("active");
      navLinks.classList.remove("active");
    }));
  }

  // =========================================================
  // PROFILE MODAL
  // =========================================================
  const modal = document.getElementById("profileModal");
  const openBtns = [document.getElementById("openProfile"), document.getElementById("openProfileHero")].filter(Boolean);
  const closeBtn = document.getElementById("closeProfile");
  const downloadBtn = document.getElementById("downloadProfile");

  if (modal && closeBtn) {
    openBtns.forEach(btn => {
      btn.addEventListener("click", e => { 
        e.preventDefault(); 
        modal.classList.add("show"); 
      });
    });
    
    closeBtn.addEventListener("click", () => modal.classList.remove("show"));
    
    window.addEventListener("click", e => { 
      if (e.target === modal) modal.classList.remove("show"); 
    });
    
    window.addEventListener("keydown", e => { 
      if (e.key === "Escape" && modal.classList.contains("show")) {
        modal.classList.remove("show");
      }
    });
  }

  if (downloadBtn) {
    downloadBtn.addEventListener("click", () => {
      const link = document.createElement("a");
      link.href = "assets/Established Media & Enterprises - Business Profile2025.pdf";
      link.download = "EME-Business-Profile.pdf";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    });
  }

  // =========================================================
  // CONTACT FORM
  // =========================================================
  const contactForm = document.getElementById("contactForm");
  const formMessage = document.getElementById("formMessage");
  
  function showToast(message, type = "success") {
    if (!formMessage) return;
    formMessage.textContent = message;
    formMessage.className = `form-message ${type}`;
    formMessage.style.display = "block";
    setTimeout(() => { 
      formMessage.style.display = "none"; 
    }, 7000);
  }
  
  if (contactForm) {
    contactForm.addEventListener("submit", async e => {
      e.preventDefault();
      
      const formData = {
        name: contactForm.name.value.trim(),
        email: contactForm.email.value.trim(),
        phone: contactForm.phone.value.trim(),
        service: contactForm.service.value,
        message: contactForm.message.value.trim(),
      };
      
      if (!formData.name || !formData.email || !formData.service || !formData.message) {
        showToast("Please fill all required fields.", "error");
        return;
      }
      
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
        showToast(err.message || "An error occurred. Please try again later.", "error");
      } finally {
        if (submitButton) submitButton.disabled = false;
      }
    });
  }

  // =========================================================
  // LIVE SYSTEM MONITOR
  // =========================================================
  class SystemMonitor {
    constructor() {
      this.activityFeed = document.getElementById('activityFeed');
      this.activities = [
        { time: '2 min ago', message: 'Ticket #2024-0148 opened: Email server configuration' },
        { time: '15 min ago', message: 'Deployment completed: MSB Finance Portal v2.1' },
        { time: '1 hour ago', message: 'CIPC registration completed: New client onboarding' },
        { time: '2 hours ago', message: 'SSL certificate renewed: korundum.co.za' },
        { time: '3 hours ago', message: 'Automated backup completed: All client sites' },
        { time: '4 hours ago', message: 'Security scan passed: tasselgroup.co.za' },
        { time: '5 hours ago', message: 'DNS propagation verified: New domain setup' }
      ];
      this.activityIndex = 0;
      this.startMonitoring();
    }
    
    startMonitoring() {
      this.updateStatusTime();
      setInterval(() => this.updateStatusTime(), 30000);
      setInterval(() => this.simulateMetrics(), 5000);
      setInterval(() => this.addActivity(), 8000);
      this.populateInitialActivities();
    }
    
    updateStatusTime() {
      const statusTimeElement = document.getElementById('statusTime');
      if (!statusTimeElement) return;
      
      const now = new Date();
      statusTimeElement.textContent = now.toLocaleTimeString('en-ZA', { 
        hour: '2-digit', 
        minute: '2-digit' 
      });
    }
    
    simulateMetrics() {
      document.querySelectorAll('.metric-value').forEach(el => {
        el.style.transform = 'scale(1.05)';
        el.style.transition = 'transform 0.2s ease';
        setTimeout(() => {
          el.style.transform = 'scale(1)';
        }, 200);
      });
    }
    
    populateInitialActivities() {
      if (!this.activityFeed) return;
      this.activityFeed.innerHTML = '';
      this.activities.slice(0, 4).forEach(activity => {
        this.appendActivity(activity);
      });
    }
    
    addActivity() {
      if (!this.activityFeed) return;
      const activity = this.activities[this.activityIndex % this.activities.length];
      this.appendActivity(activity);
      this.activityIndex++;
      
      if (this.activityFeed.children.length > 5) {
        this.activityFeed.removeChild(this.activityFeed.firstChild);
      }
    }
    
    appendActivity(activity) {
      const item = document.createElement('div');
      item.className = 'feed-item';
      item.innerHTML = `
        <span class="feed-time">${activity.time}</span>
        <span class="feed-message">${activity.message}</span>
      `;
      this.activityFeed.appendChild(item);
      this.activityFeed.scrollTop = this.activityFeed.scrollHeight;
    }
  }
  
  const monitor = new SystemMonitor();

  // =========================================================
  // ENHANCED PROJECT ESTIMATOR
  // =========================================================
  class ProjectEstimator {
    constructor() {
      this.complexitySlider = document.getElementById('complexity');
      this.projectTypeSelect = document.getElementById('projectType');
      this.estimateDisplay = document.getElementById('estimateDisplay');
      this.costDisplay = document.getElementById('costDisplay');
      
      if (this.complexitySlider && this.projectTypeSelect) {
        this.init();
      }
    }
    
    init() {
      this.complexitySlider.addEventListener('input', () => this.updateEstimate());
      this.projectTypeSelect.addEventListener('change', () => this.updateEstimate());
      this.updateEstimate();
    }
    
    updateEstimate() {
      const type = this.projectTypeSelect.value;
      const complexity = parseInt(this.complexitySlider.value);
      
      const timelines = {
        website: ['3-5 business days', '7-10 business days', '14-21 business days'],
        ecommerce: ['7-10 business days', '14-21 business days', '21-30 business days'],
        portal: ['14-21 business days', '21-30 business days', '30-45 business days'],
        registration: ['5-7 business days', '7-10 business days', '10-14 business days']
      };
      
      const costs = {
        website: ['R3,500 - R5,000', 'R5,000 - R8,000', 'R8,000 - R15,000'],
        ecommerce: ['R8,000 - R12,000', 'R12,000 - R20,000', 'R20,000 - R35,000'],
        portal: ['R15,000 - R25,000', 'R25,000 - R40,000', 'R40,000 - R65,000'],
        registration: ['R1,500 - R2,500', 'R2,500 - R4,000', 'R4,000 - R6,000']
      };
      
      const timeline = timelines[type] ? timelines[type][complexity - 1] : 'Contact us for quote';
      const cost = costs[type] ? costs[type][complexity - 1] : 'Contact us for quote';
      
      if (this.estimateDisplay) {
        this.estimateDisplay.textContent = timeline;
        this.animateValue(this.estimateDisplay);
      }
      
      if (this.costDisplay) {
        this.costDisplay.textContent = cost;
        this.animateValue(this.costDisplay);
      }
    }
    
    animateValue(element) {
      element.style.transform = 'scale(1.1)';
      element.style.transition = 'transform 0.3s ease';
      setTimeout(() => {
        element.style.transform = 'scale(1)';
      }, 300);
    }
  }
  
  const estimator = new ProjectEstimator();

  // =========================================================
  // SCROLL ANIMATIONS
  // =========================================================
  function initScrollAnimations() {
    const animatedElements = document.querySelectorAll('.sheet, .spec-card, .doc-card, .tech-row');
    
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry, index) => {
        if (entry.isIntersecting) {
          setTimeout(() => {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
          }, index * 100);
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });
    
    animatedElements.forEach(el => {
      el.style.opacity = '0';
      el.style.transform = 'translateY(20px)';
      el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
      observer.observe(el);
    });
  }
  
  initScrollAnimations();

  // =========================================================
  // KEYBOARD SHORTCUTS
  // =========================================================
  document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      document.getElementById('contact')?.scrollIntoView({ behavior: 'smooth' });
    }
    
    if (e.key === 'Escape' && modal && modal.classList.contains('show')) {
      modal.classList.remove('show');
    }
    
    if (e.key === 'h' && !e.ctrlKey && !e.metaKey && !e.altKey) {
      const activeElement = document.activeElement;
      if (activeElement && activeElement.tagName !== 'INPUT' && activeElement.tagName !== 'TEXTAREA' && activeElement.tagName !== 'SELECT') {
        window.location.hash = '#home';
      }
    }
  });

  // =========================================================
  // DYNAMIC YEAR UPDATE
  // =========================================================
  const yearElements = document.querySelectorAll('.current-year');
  const currentYear = new Date().getFullYear();
  yearElements.forEach(el => {
    el.textContent = currentYear;
  });

  // =========================================================
  // CONSOLE EASTER EGG
  // =========================================================
  console.log(`
  ╔══════════════════════════════════════╗
  ║   EME — Established Media & Ent.    ║
  ║   Built to spec. Drawn with care.   ║
  ║   Like what you see? Let's talk:    ║
  ║   info@eme4you.co.za               ║
  ║   Tel: 063 246 2802                ║
  ╚══════════════════════════════════════╝
  
  Commands available in console:
  - eme.status()  : View system status
  - eme.stack()   : View our tech stack
  - eme.contact() : Get contact details
  `);

  window.eme = {
    status: () => {
      console.log(`
  ▸ System Status: Operational
  ▸ Uptime: 99.9%
  ▸ Active Projects: 12
  ▸ Response Time: <2 hours
  ▸ Server Load: 23%
      `);
    },
    stack: () => {
      console.log(`
  ▸ Frontend: HTML5, CSS3, JavaScript, React.js
  ▸ Backend: Node.js, REST APIs
  ▸ Infrastructure: Linux, Cloud Hosting
  ▸ Integrations: Payment Gateways, Booking Systems, CRM
      `);
    },
    contact: () => {
      console.log(`
  ▸ Phone: 063 246 2802
  ▸ Email: info@eme4you.co.za
  ▸ Web: www.eme4you.co.za
  ▸ Location: 21 Korundum Avenue, Waldrift, Vereeniging, Gauteng, 1939
      `);
    }
  };

  // =========================================================
  // PERFORMANCE MONITORING
  // =========================================================
  window.addEventListener('load', () => {
    if (window.performance && window.performance.timing) {
      const timing = window.performance.timing;
      const loadTime = timing.loadEventEnd - timing.navigationStart;
      if (loadTime > 0) {
        console.log(`EME site loaded in ${loadTime}ms — drawn to spec.`);
      }
    }
  });

  // =========================================================
  // SMOOTH SCROLL FOR ALL ANCHOR LINKS
  // =========================================================
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      const href = this.getAttribute('href');
      if (href === '#') return;
      
      const target = document.querySelector(href);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    });
  });
});