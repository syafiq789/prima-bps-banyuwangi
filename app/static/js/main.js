// PRIMA - Pusat Arsip dan Manajemen AKIP Banyuwangi
// Master Single-Sidebar Navigation Handler

// 1. Toggle Master PRIMA Menu (Buka / Tutup seluruh fitur di bawah PRIMA)
window.togglePrimaMasterMenu = function() {
    const container = document.getElementById('container-prima-features');
    const chevron = document.getElementById('chevron-prima-master');
    const btn = document.getElementById('btn-prima-master');

    if (!container) return;

    const isClosed = container.classList.contains('closed');

    if (isClosed) {
        container.classList.remove('closed');
        if (chevron) chevron.classList.add('rotate');
        if (btn) btn.classList.add('border-orange-500/70', 'bg-orange-500/25');
    } else {
        container.classList.add('closed');
        if (chevron) chevron.classList.remove('rotate');
        if (btn) btn.classList.remove('border-orange-500/70', 'bg-orange-500/25');
    }
};

// 1.b Toggle Master MONITORING MITRA Menu
window.toggleMitraMasterMenu = function() {
    const container = document.getElementById('container-mitra-features');
    const chevron = document.getElementById('chevron-mitra-master');
    const btn = document.getElementById('btn-mitra-master');

    if (!container) return;

    const isClosed = container.classList.contains('closed');

    if (isClosed) {
        container.classList.remove('closed');
        if (chevron) chevron.classList.add('rotate');
        if (btn) btn.classList.add('border-orange-500/70', 'bg-orange-500/25');
    } else {
        container.classList.add('closed');
        if (chevron) chevron.classList.remove('rotate');
        if (btn) btn.classList.remove('border-orange-500/70', 'bg-orange-500/25');
    }
};

// 1.c Toggle Master KINERJA PEGAWAI Menu
window.togglePegawaiMasterMenu = function() {
    const container = document.getElementById('container-pegawai-features');
    const chevron = document.getElementById('chevron-pegawai-master');
    const btn = document.getElementById('btn-pegawai-master');

    if (!container) return;

    const isClosed = container.classList.contains('closed');

    if (isClosed) {
        container.classList.remove('closed');
        if (chevron) chevron.classList.add('rotate');
        if (btn) btn.classList.add('border-blue-500/70', 'bg-blue-500/25');
    } else {
        container.classList.add('closed');
        if (chevron) chevron.classList.remove('rotate');
        if (btn) btn.classList.remove('border-blue-500/70', 'bg-blue-500/25');
    }
};

// 1.d Toggle Master TRACKING KEUANGAN Menu
window.toggleKeuanganMasterMenu = function() {
    const container = document.getElementById('container-keuangan-features');
    const chevron = document.getElementById('chevron-keuangan-master');
    const btn = document.getElementById('btn-keuangan-master');

    if (!container) return;

    const isClosed = container.classList.contains('closed');

    if (isClosed) {
        container.classList.remove('closed');
        if (chevron) chevron.classList.add('rotate');
        if (btn) btn.classList.add('border-emerald-500/70', 'bg-emerald-500/25');
    } else {
        container.classList.add('closed');
        if (chevron) chevron.classList.remove('rotate');
        if (btn) btn.classList.remove('border-emerald-500/70', 'bg-emerald-500/25');
    }
};

// 2. Toggle Subkelompok Fitur di dalam PRIMA (Menu Utama, Perencanaan, Pengukuran, dll)
window.toggleSubFeature = function(targetId, triggerElement) {
    const targetContent = document.getElementById(targetId);
    if (!targetContent) return;

    const chevron = triggerElement ? triggerElement.querySelector('.subgroup-chevron') : null;
    const isCurrentlyOpen = targetContent.classList.contains('open');

    // Tutup subkelompok lain agar rapi (Single Accordion dalam PRIMA)
    const allContents = document.querySelectorAll('.subgroup-content');
    const allTriggers = document.querySelectorAll('.subgroup-trigger');
    const allChevrons = document.querySelectorAll('.subgroup-chevron');

    allContents.forEach(content => {
        if (content.id !== targetId && content.classList.contains('open')) {
            content.classList.remove('open');
            content.style.maxHeight = null;
        }
    });

    allTriggers.forEach(t => {
        if (t !== triggerElement) {
            t.classList.remove('bg-slate-800/80', 'text-orange-400');
        }
    });

    allChevrons.forEach(c => {
        if (!triggerElement || !triggerElement.contains(c)) {
            c.classList.remove('rotate');
        }
    });

    // Toggle subkelompok yang diklik
    if (isCurrentlyOpen) {
        targetContent.classList.remove('open');
        targetContent.style.maxHeight = null;
        if (chevron) chevron.classList.remove('rotate');
        if (triggerElement) triggerElement.classList.remove('bg-slate-800/80', 'text-orange-400');
    } else {
        targetContent.classList.add('open');
        targetContent.style.maxHeight = (targetContent.scrollHeight + 40) + "px";
        if (chevron) chevron.classList.add('rotate');
        if (triggerElement) triggerElement.classList.add('bg-slate-800/80', 'text-orange-400');
    }
};

document.addEventListener('DOMContentLoaded', () => {
    // 3. Initialize Lucide Icons
    if (window.lucide) {
        lucide.createIcons();
    }

    // 4. Desktop Sidebar Collapse Toggle
    const sidebar = document.getElementById('sidebar');
    const sidebarToggleBtn = document.getElementById('sidebar-toggle');
    const mainContent = document.getElementById('main-content');

    if (sidebarToggleBtn && sidebar) {
        sidebarToggleBtn.addEventListener('click', () => {
            sidebar.classList.toggle('collapsed');
            if (mainContent) {
                mainContent.classList.toggle('lg:ml-20');
                mainContent.classList.toggle('lg:ml-72');
            }
            if (window.lucide) lucide.createIcons();
        });
    }

    // 5. Mobile Drawer Off-Canvas Toggle
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mobileCloseBtn = document.getElementById('mobile-close-btn');
    const sidebarOverlay = document.getElementById('sidebar-overlay');

    if (mobileMenuBtn && sidebar && sidebarOverlay) {
        mobileMenuBtn.addEventListener('click', () => {
            sidebar.classList.remove('-translate-x-full');
            sidebarOverlay.classList.remove('hidden');
            document.body.classList.add('overflow-hidden');
        });
    }

    const closeMobileSidebar = () => {
        if (sidebar && sidebarOverlay) {
            sidebar.classList.add('-translate-x-full');
            sidebarOverlay.classList.add('hidden');
            document.body.classList.remove('overflow-hidden');
        }
    };

    if (mobileCloseBtn) mobileCloseBtn.addEventListener('click', closeMobileSidebar);
    if (sidebarOverlay) sidebarOverlay.addEventListener('click', closeMobileSidebar);

    // 6. Auto-Open Active Menu in PRIMA based on current URL path
    const currentPath = window.location.pathname;
    let foundActive = false;

    const subitems = document.querySelectorAll('.nav-subitem');
    subitems.forEach(item => {
        const href = item.getAttribute('href');
        if (href && (currentPath === href || (href !== '/' && currentPath.startsWith(href)))) {
            item.classList.add('bg-orange-500', 'text-white', 'font-semibold', 'shadow-sm');
            item.classList.remove('text-slate-400');

            // Open parent subgroup inside PRIMA
            const parentSubgroup = item.closest('.subgroup-content');
            if (parentSubgroup) {
                parentSubgroup.classList.add('open');
                parentSubgroup.style.maxHeight = (parentSubgroup.scrollHeight + 50) + "px";
                const trigger = parentSubgroup.previousElementSibling;
                if (trigger) {
                    const chevron = trigger.querySelector('.subgroup-chevron');
                    if (chevron) chevron.classList.add('rotate');
                    trigger.classList.add('bg-slate-800/80', 'text-orange-400');
                }
                foundActive = true;
            }
        }
    });

    // Default open Menu Utama on home/dashboard if nothing else matched
    if (!foundActive && (currentPath === '/' || currentPath === '/dashboard')) {
        const utamaContent = document.getElementById('subcontent-utama');
        const triggerUtama = document.getElementById('trigger-sub-utama');
        if (utamaContent) {
            utamaContent.classList.add('open');
            utamaContent.style.maxHeight = (utamaContent.scrollHeight + 30) + "px";
            if (triggerUtama) {
                const chevron = triggerUtama.querySelector('.subgroup-chevron');
                if (chevron) chevron.classList.add('rotate');
                triggerUtama.classList.add('bg-slate-800/80', 'text-orange-400');
            }
        }
    }

    // Pastikan master container terbuka sesuai modul yang sedang aktif
    const primaContainer = document.getElementById('container-prima-features');
    const primaChevron = document.getElementById('chevron-prima-master');
    const btnPrima = document.getElementById('btn-prima-master');

    const mitraContainer = document.getElementById('container-mitra-features');
    const mitraChevron = document.getElementById('chevron-mitra-master');
    const btnMitra = document.getElementById('btn-mitra-master');

    const pegawaiContainer = document.getElementById('container-pegawai-features');
    const pegawaiChevron = document.getElementById('chevron-pegawai-master');
    const btnPegawai = document.getElementById('btn-pegawai-master');

    const keuanganContainer = document.getElementById('container-keuangan-features');
    const keuanganChevron = document.getElementById('chevron-keuangan-master');
    const btnKeuangan = document.getElementById('btn-keuangan-master');

    if (currentPath.startsWith('/mitra')) {
        if (mitraContainer) mitraContainer.classList.remove('closed');
        if (mitraChevron) mitraChevron.classList.add('rotate');
        if (btnMitra) btnMitra.classList.add('border-orange-500/70', 'bg-orange-500/25');
        if (primaContainer) primaContainer.classList.add('closed');
        if (primaChevron) primaChevron.classList.remove('rotate');
        if (btnPrima) btnPrima.classList.remove('border-orange-500/70', 'bg-orange-500/25');
    } else if (currentPath.startsWith('/pegawai')) {
        if (pegawaiContainer) pegawaiContainer.classList.remove('closed');
        if (pegawaiChevron) pegawaiChevron.classList.add('rotate');
        if (btnPegawai) btnPegawai.classList.add('border-blue-500/70', 'bg-blue-500/25');
        if (primaContainer) primaContainer.classList.add('closed');
        if (primaChevron) primaChevron.classList.remove('rotate');
        if (btnPrima) btnPrima.classList.remove('border-orange-500/70', 'bg-orange-500/25');
    } else if (currentPath.startsWith('/keuangan')) {
        if (keuanganContainer) keuanganContainer.classList.remove('closed');
        if (keuanganChevron) keuanganChevron.classList.add('rotate');
        if (btnKeuangan) btnKeuangan.classList.add('border-emerald-500/70', 'bg-emerald-500/25');
        if (primaContainer) primaContainer.classList.add('closed');
        if (primaChevron) primaChevron.classList.remove('rotate');
        if (btnPrima) btnPrima.classList.remove('border-orange-500/70', 'bg-orange-500/25');
    } else {
        if (primaContainer && !primaContainer.classList.contains('closed') && primaChevron) {
            primaChevron.classList.add('rotate');
        }
    }

    // 7. User Profile Dropdown
    const userMenuBtn = document.getElementById('user-menu-btn');
    const userDropdown = document.getElementById('user-dropdown');

    if (userMenuBtn && userDropdown) {
        userMenuBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            userDropdown.classList.toggle('hidden');
        });

        document.addEventListener('click', (e) => {
            if (!userDropdown.contains(e.target) && !userMenuBtn.contains(e.target)) {
                userDropdown.classList.add('hidden');
            }
        });
    }

    // 7.1 Global Search Focus with Ctrl + K / Cmd + K
    const searchInput = document.getElementById('global-search-input');
    if (searchInput) {
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
                e.preventDefault();
                searchInput.focus();
                searchInput.select();
            }
        });
    }

    // 8. Auto-dismiss Flash Alerts
    const alerts = document.querySelectorAll('.flash-alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });

    // 9. Document Preview Modal Helper
    window.openPreviewModal = function(url, title, type) {
        const modal = document.getElementById('preview-modal');
        const modalTitle = document.getElementById('preview-modal-title');
        const modalContainer = document.getElementById('preview-modal-container');
        const modalDownloadBtn = document.getElementById('preview-modal-download');

        if (!modal || !modalContainer) return;

        modalTitle.textContent = title || 'Pratinjau Dokumen';
        if (modalDownloadBtn) {
            modalDownloadBtn.href = url.replace('/preview', '/download');
        }

        modalContainer.innerHTML = '';

        if (type === 'pdf') {
            modalContainer.innerHTML = `
                <iframe src="${url}#toolbar=1" class="w-full h-full min-h-[500px] rounded-lg border border-slate-200"></iframe>
            `;
        } else if (['jpg', 'jpeg', 'png', 'webp', 'svg'].includes(type)) {
            modalContainer.innerHTML = `
                <div class="flex items-center justify-center p-4 h-full">
                    <img src="${url}" alt="${title}" class="max-h-[550px] max-w-full object-contain rounded shadow">
                </div>
            `;
        } else {
            modalContainer.innerHTML = `
                <div class="flex flex-col items-center justify-center p-8 text-center bg-slate-50 rounded-xl my-6">
                    <div class="w-16 h-16 bg-blue-50 text-navy-main rounded-2xl flex items-center justify-center mb-4">
                        <i data-lucide="file-text" class="w-8 h-8 text-blue-600"></i>
                    </div>
                    <h4 class="text-base font-semibold text-slate-800 mb-2">Pratinjau langsung tidak tersedia untuk format .${type.toUpperCase()}</h4>
                    <p class="text-sm text-slate-500 max-w-md mb-6">File dokumen Microsoft Office (DOCX, XLSX, PPTX) dapat diunduh untuk dibuka langsung menggunakan aplikasi pengolah dokumen di perangkat Anda.</p>
                    <a href="${url.replace('/preview', '/download')}" class="inline-flex items-center gap-2 px-5 py-2.5 bg-orange-prima hover:bg-orange-hover text-white text-sm font-semibold rounded-lg shadow-sm transition">
                        <i data-lucide="download" class="w-4 h-4"></i> Unduh File Sekarang
                    </a>
                </div>
            `;
        }

        modal.classList.remove('hidden');
        document.body.classList.add('overflow-hidden');
        if (window.lucide) lucide.createIcons();
    };

    window.closePreviewModal = function() {
        const modal = document.getElementById('preview-modal');
        if (modal) {
            modal.classList.add('hidden');
            document.body.classList.remove('overflow-hidden');
        }
    };

    // 10. Navbar Quick Drive Menu Toggle (Titik 3 Akses Cepat Folder Google Drive)
    window.toggleQuickDriveNavbar = function(e) {
        if (e) e.stopPropagation();
        const dropdown = document.getElementById('quick-drive-dropdown');
        if (dropdown) {
            dropdown.classList.toggle('hidden');
            if (window.lucide) lucide.createIcons();
        }
    };

    document.addEventListener('click', function(e) {
        const dropdown = document.getElementById('quick-drive-dropdown');
        const btn = document.getElementById('btn-quick-drive-menu');
        if (dropdown && !dropdown.classList.contains('hidden')) {
            if (!dropdown.contains(e.target) && (!btn || !btn.contains(e.target))) {
                dropdown.classList.add('hidden');
            }
        }
    });
});
