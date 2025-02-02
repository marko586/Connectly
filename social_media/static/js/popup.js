document.addEventListener('DOMContentLoaded', function () {
    const popup = document.getElementById('popup');

    // If there are messages, show and animate the popup
    if (popup) {
        // Slide in the popup
        popup.style.display = 'block';
        setTimeout(() => {
            popup.style.left = '20px'; // Slide into view
        }, 10);

        // Hide the popup after 3 seconds
        setTimeout(() => {
            popup.classList.add('hide'); // Fade out
        }, 3000);

        // Reset and hide the popup fully after the fade-out
        setTimeout(() => {
            popup.style.display = 'none';
            popup.style.left = '-300px'; // Reset position off-screen
            popup.classList.remove('hide'); // Reset opacity
        }, 3500);
    }
});
