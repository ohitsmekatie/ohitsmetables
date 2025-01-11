// static/js/loadComponents.js
document.addEventListener("DOMContentLoaded", function () {
    // Load the navigation
    fetch('static/html/nav.html')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.text();
        })
        .then(data => {
            document.getElementById('navigation').innerHTML = data;
        })
        .catch(error => {
            console.error('Error loading navigation:', error);
        });

    // Load the footer
    fetch('static/html/footer.html')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.text();
        })
        .then(data => {
            document.getElementById('footer').innerHTML = data;
        })
        .catch(error => {
            console.error('Error loading footer:', error);
        });
});
