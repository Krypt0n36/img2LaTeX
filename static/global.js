const uploadArea = document.getElementById('uploadArea');
const uploadText = document.getElementById('uploadText');
const uploadedImage = document.getElementById('uploadedImage');
const removeButton = document.getElementById('removeButton');
const convertButton = document.getElementById('convertButton');
const codeSnippet = document.getElementById('codeSnippet');
const imageContainer = document.getElementById('imageContainer');
const convertedImage = document.getElementById('convertedImage');

let selectedFile = null;

// Open file dialog when upload area is clicked
uploadArea.addEventListener('click', () => {
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = 'image/*';
    fileInput.onchange = (e) => {
        selectedFile = e.target.files[0];
        if (selectedFile) {
            const reader = new FileReader();
            reader.onload = (event) => {
                uploadedImage.src = event.target.result;
                uploadedImage.style.display = 'block';
                uploadText.style.display = 'none';
                removeButton.style.display = 'block';
                convertButton.disabled = false;
            };
            reader.readAsDataURL(selectedFile);
        }
    };
    fileInput.click();
});

// Remove uploaded image
removeButton.addEventListener('click', (e) => {
    e.stopPropagation(); // Prevent triggering the upload area click event
    uploadedImage.src = '#';
    uploadedImage.style.display = 'none';
    uploadText.style.display = 'block';
    removeButton.style.display = 'none';
    convertButton.disabled = true;
    selectedFile = null;
});

// Handle convert button click
convertButton.addEventListener('click', async () => {
    if (!selectedFile) return;
    convertButton.innerHTML = "Loading.."


    const formData = new FormData();
    formData.append('image', selectedFile);

    try {
        const response = await fetch('/api/convert', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            throw new Error('Server error');
        }

        const result = await response.json();

        // Update code snippet
        codeSnippet.textContent = result.latex;
    } catch (error) {
        console.error('Error:', error);
        document.querySelector(".error-alert").hidden = false;
    }
    convertButton.innerHTML = "Convert"

});