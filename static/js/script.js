// Mobile nav toggle
const hamburger = document.querySelector('.hamburger');
const navMenu = document.querySelector('.nav-menu');

hamburger.addEventListener('click', () => {
    hamburger.classList.toggle('active');
    navMenu.classList.toggle('active');
});

// Close nav on link click
document.querySelectorAll('.nav-menu a').forEach(link => {
    link.addEventListener('click', () => {
        hamburger.classList.remove('active');
        navMenu.classList.remove('active');
    });
});

// Smooth scroll
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Form enhancements (AJAX OTP if needed)
document.addEventListener('DOMContentLoaded', function() {
    // Progress anim sim
    const progresses = document.querySelectorAll('.progress');
    progresses.forEach(progress => {
        const width = progress.style.width;
        progress.style.width = '0%';
        setTimeout(() => {
            progress.style.width = width;
        }, 100);
    });
});

// Back button confirm if needed
function goBack() {
    if (window.history.length > 1) {
        window.history.back();
    } else {
        window.location.href = '/';
    }
}

// OTP auto focus next input if fields separate, but sim 1 field

console.log('Gravity JS loaded');
