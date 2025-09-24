
/**
 * Site-wide helpers & progressive enhancements
 * - fadeIn helper for cards (if desired)
 * - lore sidebar mobile toggle
 */

(function() {
  // Lore Sidebar: add a toggle button on small screens if .lore-sidebar exists
  function setupLoreSidebarToggle() {
    const sidebar = document.querySelector('.lore-sidebar');
    if (!sidebar) return;

    const btnId = 'loreToggleBtn';
    if (document.getElementById(btnId)) return; // avoid duplicates

    const toggleBtn = document.createElement('button');
    toggleBtn.id = btnId;
    toggleBtn.type = 'button';
    toggleBtn.className = 'btn btn-outline-light d-md-none lore-toggle-btn';
    toggleBtn.innerHTML = '📜 Lore';
    document.body.appendChild(toggleBtn);

    // Start hidden on mobile
    if (window.innerWidth < 768) {
      sidebar.classList.add('collapsed');
    }

    toggleBtn.addEventListener('click', () => {
      sidebar.classList.toggle('collapsed');
    });

    // Handle resize
    window.addEventListener('resize', () => {
      if (window.innerWidth >= 768) {
        sidebar.classList.remove('collapsed');
      } else {
        sidebar.classList.add('collapsed');
      }
    });
  }

  document.addEventListener('DOMContentLoaded', setupLoreSidebarToggle);
})();
