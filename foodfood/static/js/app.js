function showToast(message, type = 'success') {
  const container = document.getElementById('toast-container');
  if (!container) return;
  const wrapper = document.createElement('div');
  wrapper.className = 'toast align-items-center text-bg-' + (type === 'success' ? 'success' : 'danger') + ' border-0';
  wrapper.setAttribute('role', 'alert');
  wrapper.setAttribute('aria-live', 'assertive');
  wrapper.setAttribute('aria-atomic', 'true');
  wrapper.innerHTML = `
    <div class="d-flex">
      <div class="toast-body">${message}</div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
    </div>`;
  container.appendChild(wrapper);
  const toast = new bootstrap.Toast(wrapper, { delay: 1800 });
  toast.show();
  wrapper.addEventListener('hidden.bs.toast', () => wrapper.remove());
}

document.addEventListener('click', (e) => {
  const addBtn = e.target.closest('a[data-add-to-cart]');
  if (addBtn) {
    showToast('Article ajouté au panier');
  }
});

