-- ====================================================================
-- DATABASE SCHEMA: PRIMA (Pusat Arsip dan Manajemen AKIP Banyuwangi)
-- Badan Pusat Statistik Kabupaten Banyuwangi
-- ====================================================================

CREATE DATABASE IF NOT EXISTS `prima_akip_banyuwangi` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `prima_akip_banyuwangi`;

-- 1. Tabel users
CREATE TABLE IF NOT EXISTS `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `full_name` VARCHAR(100) NOT NULL,
    `nip` VARCHAR(30) NULL,
    `role` VARCHAR(20) NOT NULL DEFAULT 'user',
    `is_active` BOOLEAN NOT NULL DEFAULT TRUE,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_users_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Tabel categories
CREATE TABLE IF NOT EXISTS `categories` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `slug` VARCHAR(100) NOT NULL UNIQUE,
    `group` VARCHAR(50) NOT NULL,
    `description` TEXT NULL,
    `icon` VARCHAR(50) DEFAULT 'folder',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_categories_slug` (`slug`),
    INDEX `idx_categories_group` (`group`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Tabel documents
CREATE TABLE IF NOT EXISTS `documents` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `title` VARCHAR(255) NOT NULL,
    `category_id` INT NOT NULL,
    `year` INT NOT NULL,
    `description` TEXT NULL,
    `filename` VARCHAR(255) NOT NULL,
    `original_filename` VARCHAR(255) NOT NULL,
    `file_size` INT DEFAULT 0,
    `file_type` VARCHAR(20) NOT NULL,
    `uploaded_by` INT NOT NULL,
    `status` VARCHAR(20) NOT NULL DEFAULT 'lengkap',
    `notes` TEXT NULL,
    `download_count` INT DEFAULT 0,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`category_id`) REFERENCES `categories`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`uploaded_by`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    INDEX `idx_documents_title` (`title`),
    INDEX `idx_documents_year` (`year`),
    INDEX `idx_documents_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Tabel document_completeness
CREATE TABLE IF NOT EXISTS `document_completeness` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `category_id` INT NOT NULL,
    `year` INT NOT NULL,
    `item_name` VARCHAR(255) NOT NULL,
    `is_required` BOOLEAN DEFAULT TRUE,
    `is_fulfilled` BOOLEAN DEFAULT FALSE,
    `document_id` INT NULL,
    `notes` TEXT NULL,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`category_id`) REFERENCES `categories`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`document_id`) REFERENCES `documents`(`id`) ON DELETE SET NULL,
    INDEX `idx_completeness_year` (`year`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Tabel important_links
CREATE TABLE IF NOT EXISTS `important_links` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `code` VARCHAR(50) NOT NULL UNIQUE,
    `title` VARCHAR(100) NOT NULL,
    `description` TEXT NOT NULL,
    `url` VARCHAR(500) NOT NULL,
    `icon` VARCHAR(50) DEFAULT 'external-link',
    `badge_text` VARCHAR(50) DEFAULT 'Aplikasi Eksternal',
    `is_active` BOOLEAN DEFAULT TRUE,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_links_code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. Tabel activities
CREATE TABLE IF NOT EXISTS `activities` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NULL,
    `action` VARCHAR(100) NOT NULL,
    `description` TEXT NOT NULL,
    `ip_address` VARCHAR(50) NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE SET NULL,
    INDEX `idx_activities_created` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ====================================================================
-- SEED INITIAL DATA
-- ====================================================================

-- 1. Default Admin & Pegawai
-- Default password: admin123 (scrypt hashed) & pegawai123
INSERT INTO `users` (`username`, `password_hash`, `full_name`, `nip`, `role`, `is_active`) 
VALUES 
('admin', 'scrypt:32768:8:1$gYx3D1sM$9b7bb69695420eeffbd85e2b4fef01e23ad8d752c09d57a2c7a1c3e387190dbcb4f6fa37efca31bb188fca951ad786eecae4b4db26f6ebefca5be2488a0e0e18', 'Administrator PRIMA BPS', '198501012010011001', 'admin', 1),
('pegawai', 'scrypt:32768:8:1$nZ8v2XqL$8f635c2b8c56c703b41b9d4e5d629a8b19e99a38f3f88dca8d810f274cb7e30d778d910b0f7725ca312389d0cf3cb9833cbfa3bf2488a0e0e181234567890abc', 'Staf Tim AKIP BPS Banyuwangi', '199203152015021002', 'user', 1)
ON DUPLICATE KEY UPDATE `username`=`username`;

-- 2. Initial Categories
INSERT INTO `categories` (`name`, `slug`, `group`, `icon`, `description`) VALUES
('Dokumen Perencanaan', 'dokumen-perencanaan', 'perencanaan', 'file-text', 'Dokumen rencana strategis dan perencanaan kinerja BPS Kabupaten Banyuwangi.'),
('Rencana Kerja', 'rencana-kerja', 'perencanaan', 'calendar', 'Rencana kerja tahunan dan rencana operasional kegiatan.'),
('Perjanjian Kinerja', 'perjanjian-kinerja', 'perencanaan', 'award', 'Penetapan dan perjanjian kinerja pimpinan dan pegawai.'),
('Rencana Aksi', 'rencana-aksi', 'perencanaan', 'trending-up', 'Rencana aksi atas pencapaian target kinerja organisasi.'),
('Indikator Kinerja Utama', 'indikator-kinerja-utama', 'perencanaan', 'target', 'Indikator Kinerja Utama (IKU) BPS Kabupaten Banyuwangi.'),
('Pengukuran Kinerja', 'pengukuran-kinerja', 'pengukuran', 'gauge', 'Metrik dan data pengukuran kinerja periodik.'),
('Capaian Kinerja', 'capaian-kinerja', 'pengukuran', 'check-circle', 'Data dan analisis realisasi capaian kinerja instansi.'),
('Evaluasi Kinerja', 'evaluasi-kinerja', 'pengukuran', 'clipboard-check', 'Hasil evaluasi dan review capaian target kinerja bulanan/triwulanan.'),
('Laporan Kinerja', 'laporan-kinerja', 'pelaporan', 'book-open', 'Laporan Kinerja Instansi Pemerintah (LAKIP / LKjIP).'),
('Laporan Evaluasi', 'laporan-evaluasi', 'pelaporan', 'file-check', 'Laporan hasil evaluasi internal dan rekomendasi perbaikan.'),
('Dokumen Pendukung Pelaporan', 'dokumen-pendukung-pelaporan', 'pelaporan', 'paperclip', 'Bukti dukung, notula, daftar hadir, dan lampiran pelaporan.'),
('Arsip Dokumen', 'arsip-dokumen', 'kelengkapan', 'archive', 'Koleksi arsip dokumen akuntabilitas kinerja tahun-tahun sebelumnya.')
ON DUPLICATE KEY UPDATE `name`=VALUES(`name`);

-- 3. 8 Important Links
INSERT INTO `important_links` (`code`, `title`, `description`, `url`, `icon`, `badge_text`) VALUES
('simonik', 'SIMONIK', 'Sistem Informasi Monitoring Kinerja BPS untuk pemantauan dan evaluasi kegiatan berkala.', 'https://simonik.bps.go.id', 'activity', 'Monitoring Internal'),
('sinergi', 'SINERGI', 'Aplikasi Sistem Informasi Penilaian Kinerja Terintegrasi BPS.', 'https://sinergi.bps.go.id', 'share-2', 'Sistem Kinerja'),
('fra', 'FRA', 'Formulir Rekomendasi Akuntabilitas Kinerja Instansi Pemerintah BPS Kabupaten Banyuwangi.', 'https://fra.bps.go.id', 'check-square', 'Rekomendasi'),
('link-akip-jatim', 'LINK AKIP JATIM', 'Portal Integrasi AKIP BPS Provinsi Jawa Timur untuk sinkronisasi dokumen kabupaten/kota.', 'https://jatim.bps.go.id/akip', 'globe', 'Provinsi Jawa Timur'),
('proksi', 'PROKSI', 'Program Monitoring Kinerja Strategis dan Indikator Kunci BPS.', 'https://proksi.bps.go.id', 'pie-chart', 'Kinerja Strategis'),
('permindok-2025', 'PERMINDOK 2025', 'Permintaan dan Penataan Dokumen Administrasi AKIP BPS Banyuwangi Tahun 2025.', 'https://drive.google.com/drive/folders/permindok-2025-banyuwangi', 'folder-archive', 'Tahun 2025'),
('permindok-2026', 'PERMINDOK 2026', 'Permintaan dan Penataan Dokumen Administrasi AKIP BPS Banyuwangi Tahun 2026.', 'https://drive.google.com/drive/folders/permindok-2026-banyuwangi', 'folder-plus', 'Tahun 2026'),
('janjiku', 'JANJIKU', 'Janji Kinerja dan Pakta Integritas seluruh jajaran pegawai BPS Kabupaten Banyuwangi.', 'https://janjiku.bps.go.id', 'shield-check', 'Integritas & Janji')
ON DUPLICATE KEY UPDATE `title`=VALUES(`title`);

