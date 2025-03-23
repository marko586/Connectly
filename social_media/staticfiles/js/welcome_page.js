// Dynamic Text Animation
const dynamicText = document.getElementById("dynamic-text");
const phrases = ["Welcome to Connectly", "Connect. Share. Discover.", "Your Journey Starts Here"];
let phraseIndex = 0;
let charIndex = 0;
let isDeleting = false;

function typeEffect() {
    // Add or remove characters from the text
    if (charIndex <= phrases[phraseIndex].length && !isDeleting) {
        dynamicText.textContent = phrases[phraseIndex].substring(0, charIndex + 1);
        charIndex++;
    } else if (isDeleting) {
        dynamicText.textContent = phrases[phraseIndex].substring(0, charIndex - 1);
        charIndex--;
    }

    // Handle transitions between typing and deleting states
    if (charIndex === phrases[phraseIndex].length && !isDeleting) {
        isDeleting = true;
        setTimeout(typeEffect, 1000); // Pause before deleting
        return;
    } else if (charIndex === 0 && isDeleting) {
        isDeleting = false;
        phraseIndex = (phraseIndex + 1) % phrases.length; // Move to the next phrase
    }

    // Set the typing/deleting speed
    const typingSpeed = isDeleting ? 100 : 200;
    setTimeout(typeEffect, typingSpeed);
}

typeEffect();

// Smooth scrolling to sections
function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    section.scrollIntoView({ behavior: 'smooth' });
}
