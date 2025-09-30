document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Animate elements on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
            }
        });
    }, observerOptions);
    
    // Observe cards and important elements
    document.querySelectorAll('.card, .timeline-item').forEach(el => {
        observer.observe(el);
    });
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Form validation enhancement
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                
                // Focus on first invalid field
                const firstInvalid = form.querySelector(':invalid');
                if (firstInvalid) {
                    firstInvalid.focus();
                }
            } else {
                // Add loading state to submit button
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Processing...';
                    submitBtn.disabled = true;
                }
            }
            form.classList.add('was-validated');
        });
        
        // Real-time validation
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                if (this.checkValidity()) {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                } else {
                    this.classList.remove('is-valid');
                    this.classList.add('is-invalid');
                }
            });
        });
    });
    
    // Auto-save form data to localStorage (fallback for demo)
    const autoSaveForms = document.querySelectorAll('form[data-autosave]');
    autoSaveForms.forEach(form => {
        const formId = form.getAttribute('data-autosave');
        
        // Load saved data
        const savedData = localStorage.getItem(`form_${formId}`);
        if (savedData) {
            const data = JSON.parse(savedData);
            Object.keys(data).forEach(key => {
                const input = form.querySelector(`[name="${key}"]`);
                if (input) {
                    input.value = data[key];
                }
            });
        }
        
        // Save data on input
        form.addEventListener('input', function() {
            const formData = new FormData(form);
            const data = {};
            for (let [key, value] of formData.entries()) {
                data[key] = value;
            }
            localStorage.setItem(`form_${formId}`, JSON.stringify(data));
        });
    });
    
    // Enhanced QR code scanner simulation
    const qrInputs = document.querySelectorAll('input[placeholder*="QR"]');
    qrInputs.forEach(input => {
        // Add QR scan button
        const scanBtn = document.createElement('button');
        scanBtn.className = 'btn btn-outline-secondary';
        scanBtn.type = 'button';
        scanBtn.innerHTML = '<i class="bi bi-camera"></i>';
        scanBtn.title = 'Simulate QR Scan';
        
        scanBtn.addEventListener('click', function() {
            // Simulate QR code scan
            const sampleCodes = ['ASH-2024-001', 'TUL-2024-002', 'BRA-2024-003'];
            const randomCode = sampleCodes[Math.floor(Math.random() * sampleCodes.length)];
            
            // Animate the scan process
            scanBtn.innerHTML = '<i class="bi bi-hourglass-split"></i>';
            scanBtn.disabled = true;
            
            setTimeout(() => {
                input.value = randomCode;
                input.dispatchEvent(new Event('input'));
                scanBtn.innerHTML = '<i class="bi bi-camera"></i>';
                scanBtn.disabled = false;
                
                // Show success message
                const toast = document.createElement('div');
                toast.className = 'toast show position-fixed top-0 end-0 m-3';
                toast.innerHTML = `
                    <div class="toast-header">
                        <i class="bi bi-qr-code text-success me-2"></i>
                        <strong class="me-auto">QR Code Scanned</strong>
                        <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
                    </div>
                    <div class="toast-body">
                        Successfully scanned: ${randomCode}
                    </div>
                `;
                document.body.appendChild(toast);
                
                setTimeout(() => {
                    toast.remove();
                }, 3000);
            }, 1500);
        });
        
        // Add to input group
        const inputGroup = input.closest('.input-group');
        if (inputGroup) {
            inputGroup.appendChild(scanBtn);
        }
    });
});

// Utility functions
const utils = {
    // Format date for display
    formatDate: function(dateString) {
        const options = { year: 'numeric', month: 'long', day: 'numeric' };
        return new Date(dateString).toLocaleDateString('en-US', options);
    },
    
    // Generate random batch ID
    generateBatchId: function(species = 'GEN') {
        const year = new Date().getFullYear();
        const random = Math.floor(Math.random() * 1000).toString().padStart(3, '0');
        return `${species.substring(0,3).toUpperCase()}-${year}-${random}`;
    },
    
    // Show loading state
    showLoading: function(element) {
        element.classList.add('loading');
    },
    
    // Hide loading state
    hideLoading: function(element) {
        element.classList.remove('loading');
    },
    
    // Show toast notification
    showToast: function(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast show position-fixed top-0 end-0 m-3 bg-${type}`;
        toast.innerHTML = `
            <div class="toast-body text-white">
                ${message}
                <button type="button" class="btn-close btn-close-white float-end" data-bs-dismiss="toast"></button>
            </div>
        `;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 4000);
    }
};
