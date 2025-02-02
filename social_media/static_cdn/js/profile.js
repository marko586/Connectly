function openModal(imageSrc) {
    const modal = document.getElementById('post-modal');
    const modalImage = document.getElementById('modal-image');
    modalImage.src = imageSrc;
    modal.classList.add('open');
}
function closeModal() {
    const modal = document.getElementById('post-modal');
    modal.classList.remove('open');
}