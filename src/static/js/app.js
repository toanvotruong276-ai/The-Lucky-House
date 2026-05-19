// Sidebar toggle for mobile
document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    const toggle = document.getElementById('sidebar-toggle');

    if (toggle) {
        toggle.addEventListener('click', function(e) {
            e.stopPropagation();
            sidebar.classList.toggle('open');
            overlay.classList.toggle('active');
        });
    }

    if (overlay) {
        overlay.addEventListener('click', function() {
            sidebar.classList.remove('open');
            overlay.classList.remove('active');
        });
    }

    // Close sidebar when clicking a nav link (mobile)
    document.querySelectorAll('.sidebar-nav .nav-link').forEach(function(link) {
        link.addEventListener('click', function() {
            if (window.innerWidth <= 768) {
                sidebar.classList.remove('open');
                overlay.classList.remove('active');
            }
        });
    });

    // Delete confirmation
    document.querySelectorAll('.btn-delete').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            if (!confirm('Bạn có chắc chắn muốn xóa?')) {
                e.preventDefault();
            }
        });
    });

    // Auto-hide flash messages after 5s
    document.querySelectorAll('.alert').forEach(function(alert) {
        setTimeout(function() {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(function() { alert.remove(); }, 300);
        }, 5000);
    });
});
