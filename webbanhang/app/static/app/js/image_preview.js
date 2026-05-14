document.addEventListener('DOMContentLoaded', function() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(function(input) {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                let previewContainer = input.parentElement.querySelector('.live-preview-container');
                if (!previewContainer) {
                    previewContainer = document.createElement('div');
                    previewContainer.className = 'live-preview-container';
                    previewContainer.style.marginTop = '10px';
                    input.parentElement.appendChild(previewContainer);
                }
                
                const reader = new FileReader();
                reader.onload = function(e) {
                    previewContainer.innerHTML = `<p style="margin-bottom: 5px; font-weight: bold;">Ảnh xem trước (chưa lưu):</p><img src="${e.target.result}" style="max-height: 150px; border-radius: 5px; border: 1px solid #ccc;" />`;
                }
                reader.readAsDataURL(file);
            } else {
                let previewContainer = input.parentElement.querySelector('.live-preview-container');
                if (previewContainer) {
                    previewContainer.innerHTML = '';
                }
            }
        });
    });
});
