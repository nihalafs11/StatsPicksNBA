// navbar.js
document.addEventListener('DOMContentLoaded', function() {
    const hamburger = document.querySelector('.hamburger-menu');
    const navLinks = document.querySelector('.navbar-links');

    hamburger.addEventListener('click', function() {
        navLinks.classList.toggle('active'); // This toggles the 'active' class
    });
});