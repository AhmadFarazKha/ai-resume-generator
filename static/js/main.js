document.addEventListener('DOMContentLoaded', function() {
    const documentForm = document.getElementById('document-form');
    const formContainer = document.getElementById('form-container');
    const loadingContainer = document.getElementById('loading-container');
    const previewContainer = document.getElementById('preview-container');
    const previewContent = document.getElementById('preview-content');
    const downloadBtn = document.getElementById('download-btn');
    const newDocumentBtn = document.getElementById('new-document-btn');

    let currentFilename = null;

    documentForm.addEventListener('submit', function(e) {
        e.preventDefault();

        // Show loading
        formContainer.classList.add('d-none');
        loadingContainer.classList.remove('d-none');

        // Get form data
        const formData = new FormData(documentForm);

        // Make API call
        fetch('/generate', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Hide loading
                loadingContainer.classList.add('d-none');

                // Store filename for download
                currentFilename = data.filename;

                // Generate preview HTML
                renderPreview(data.preview_data);

                // Show preview
                previewContainer.classList.remove('d-none');
            } else {
                // Handle error
                alert(data.message);
                formContainer.classList.remove('d-none');
                loadingContainer.classList.add('d-none');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
            formContainer.classList.remove('d-none');
            loadingContainer.classList.add('d-none');
        });
    });

    // Render preview HTML
    function renderPreview(data) {
        let html = `
            <h1>${data.name || ''}</h1>
            <p class="email">${data.email || ''}</p>
        `;

        // Add sections
        if (data.sections) {
            for (const [sectionTitle, content] of Object.entries(data.sections)) {
                html += `<h2>${sectionTitle || ''}</h2>`;

                if (Array.isArray(content)) {
                    if (typeof content[0] === 'object' && content[0] !== null) {
                        // For sections with title and description (e.g., Experience, Education)
                        content.forEach(item => {
                            html += `
                                <h3>${item.title || ''}</h3>
                                <p>${item.description || ''}</p>
                            `;
                        });
                    } else {
                        // For skills or other list-type sections
                        html += '<ul>';
                        content.forEach(item => {
                            html += `<li>${item || ''}</li>`;
                        });
                        html += '</ul>';
                    }
                } else {
                    // For text sections like Summary
                    html += `<p>${content || ''}</p>`;
                }
            }
        }
        //Add image if provided
        if (data.image){
          html += `<img src="${data.image}" style="max-width:200px;">`
        }

        previewContent.innerHTML = html;
    }

    // Download button handler
    downloadBtn.addEventListener('click', function() {
        if (currentFilename) {
            window.location.href = `/download/${currentFilename}`;
        }
    });

    // New document button handler
    newDocumentBtn.addEventListener('click', function() {
        // Reset form
        documentForm.reset();

        // Show form, hide preview
        formContainer.classList.remove('d-none');
        previewContainer.classList.add('d-none');

        // Clear current filename
        currentFilename = null;
    });
});