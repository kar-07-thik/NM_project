document.addEventListener('DOMContentLoaded', () => {
    // 1. Image Upload Preview
    const fileInput = document.getElementById('outfit_image');
    const previewWrapper = document.getElementById('image-preview');
    const previewImg = document.getElementById('preview-img');
    const uploadWrapper = document.getElementById('file-upload-wrapper');
    const removeBtn = document.getElementById('remove-img');

    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(event) {
                    previewImg.src = event.target.result;
                    previewWrapper.classList.remove('hidden');
                    uploadWrapper.classList.add('hidden');
                }
                reader.readAsDataURL(file);
            }
        });

        removeBtn.addEventListener('click', function() {
            fileInput.value = '';
            previewImg.src = '';
            previewWrapper.classList.add('hidden');
            uploadWrapper.classList.remove('hidden');
        });
    }

    // 2. Form Loading State
    const forms = document.querySelectorAll('#planner-form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const btn = this.querySelector('#submit-btn');
            if (btn) {
                // Keep the width same
                btn.style.width = btn.offsetWidth + 'px';
                btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Processing with AI...';
                btn.style.opacity = '0.8';
                btn.style.cursor = 'not-allowed';
                // Don't disable completely to ensure form submits
                setTimeout(() => {
                    btn.disabled = true;
                }, 10);
            }
        });
    });

    // 3. Auto-hide flash messages
    const alerts = document.querySelectorAll('.alert');
    if (alerts.length > 0) {
        setTimeout(() => {
            alerts.forEach(alert => {
                alert.style.opacity = '0';
                setTimeout(() => {
                    alert.remove();
                }, 300);
            });
        }, 5000);
    }

    // 4. Modal interactions (for History page)
    const modal = document.getElementById('history-modal');
    const detailBtns = document.querySelectorAll('.view-details-btn');
    const closeBtn = document.querySelector('.close-modal');

    if (modal && detailBtns) {
        detailBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                modal.classList.remove('hidden');
            });
        });

        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                modal.classList.add('hidden');
            });
        }

        window.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.add('hidden');
            }
        });
    }
});
