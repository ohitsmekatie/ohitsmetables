// loadNavigation.js
document.addEventListener("DOMContentLoaded", function () {
    fetch('nav.html') // Adjust the path if `nav.html` is in a different directory
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.text();
        })
        .then(data => {
            // Insert the navigation HTML into the placeholder
            document.getElementById('navigation').innerHTML = data;
        })
        .catch(error => {
            console.error('Error loading navigation:', error);
        });
});
