
    function toggleSidebar() {
        const sidebar = document.getElementById('sidebar');
        const toggleBtn = document.querySelector('.toggle-btn');

        // Alternar la clase 'open' en el menú y el botón
        sidebar.classList.toggle('open');
        toggleBtn.classList.toggle('open');
    }
