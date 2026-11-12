# DOKUMENTASI SPESIFIKASI ARSITEKTUR, PENGUJIAN BLACK BOX & USER ACCEPTANCE TESTING (UAT)
**Sistem Informasi Terintegrasi BPS Kabupaten Banyuwangi (PRIMA & SIMPATIK)**

---

## 1. PEMETAAN KOMPONEN DAN SPESIFIKASI TEKNOLOGI

Berikut adalah tabel spesifikasi teknis dan fungsi utama yang telah diimplementasikan pada sistem:

| Komponen | Teknologi | Fungsi Utama |
| :--- | :--- | :--- |
| **Front-End** | **HTML5, CSS3, JavaScript, Tailwind CSS & Bootstrap 5** | Membangun antarmuka aplikasi berbasis web yang responsif, interaktif, dan mudah digunakan. Mendukung pembuatan dashboard dengan Chart.js, tabel monitoring, formulir pengajuan dinamis, modal kalkulator honor, serta tampilan informasi administrasi dan kelengkapan dokumen SAKIP/AKIP. |
| **Back-End** | **Python dengan Flask Framework** | Mengelola seluruh proses logika aplikasi, routing modular (Blueprints), pengolahan data pengajuan anggaran, validasi formulir, proses pemeriksaan dan persetujuan bertingkat oleh PPK, pengelolaan berkas dokumen, serta pemantauan status layanan dan kinerja secara terpadu. |
| **Basis Data** | **MySQL 8 & PostgreSQL** (dengan SQLite Fallback) | Menyimpan dan mengelola data pengguna (users), pengajuan anggaran, komponen MAK DIPA, dokumen SAKIP/AKIP, database mitra pendataan, aktivitas kerja pegawai, serta riwayat log aktivitas sistem secara aman dan terstruktur. |
| **ORM** | **SQLAlchemy** | Menghubungkan aplikasi Python dengan basis data relasional melalui pemodelan objek (ORM) sehingga manipulasi data, transaksi atomik, dan integritas relasi antartabel (*one-to-many*, *foreign key constraints*) berjalan konsisten. |
| **Autentikasi & Otorisasi** | **Flask-Login & Role-Based Access Control (RBAC)** | Mengelola proses otentikasi sesi login pengguna, enkripsi kata sandi (*Werkzeug security hashing*), serta pembatasan hak akses (*authorization*) terhadap fitur aplikasi berdasarkan peran (*Admin*, *Pegawai*, *Staf Umum*, *Petugas IPDS*, *PPK*, dan *KPA*). |
| **Pengujian** | **Black Box Testing & User Acceptance Testing (UAT)** | Menguji fungsionalitas antarmuka dan logika sistem berdasarkan masukan (*input*) dan luaran (*output*) tanpa melihat struktur internal kode, serta menguji penerimaan pengguna riil di lingkungan BPS Kabupaten Banyuwangi untuk menjamin kesesuaian proses bisnis. |

---

## 2. HASIL PENGUJIAN BLACK BOX TESTING (AUTOMATED TEST SUITE)

Pengujian fungsional *Black Box Testing* dijalankan menggunakan modul `unittest` Python pada file `tests/test_blackbox.py`. Seluruh 8 skenario pengujian utama berhasil lulus (*PASSED*):

| Kode Kasus Uji | Skenario Pengujian | Masukan (Input) | Hasil yang Diharapkan | Status |
| :--- | :--- | :--- | :--- | :---: |
| **TC-01** | Pengujian Keamanan Akses Halaman Privat | Akses URL `/dashboard`, `/mitra/*`, `/pegawai/*`, `/keuangan/*` tanpa sesi login | Sistem memblokir akses dan mengalihkan (*HTTP 302*) ke halaman `/auth/login` | **BERHASIL (OK)** |
| **TC-02** | Autentikasi Pengguna Valid | Username: `admin`, Password valid | Sistem memvalidasi kredensial, membuat sesi login, dan membuka dashboard | **BERHASIL (OK)** |
| **TC-03** | Autentikasi Kredensial Tidak Valid | Username: `admin`, Password salah | Sistem menolak login dan menampilkan pesan kesalahan: *"Email / Username atau password yang Anda masukkan salah"* | **BERHASIL (OK)** |
| **TC-04** | Modul PRIMA: Dashboard & Dokumen SAKIP | Akses rute `/dashboard` dan `/completeness/checklist` | Menampilkan matriks checklist kelengkapan dokumen AKIP/SAKIP BPS beserta persentase pemenuhan | **BERHASIL (OK)** |
| **TC-05** | Modul Mitra: Pendaftaran, Penugasan & Progres | Input data mitra baru, alokasi kegiatan, dan update dokumen tercacah | Data mitra tersimpan, progres terhitung otomatis, dan status berganti **SELESAI** saat target tercapai | **BERHASIL (OK)** |
| **TC-06** | Modul Pegawai: Catat Aktivitas & Update Capaian | Input tugas dinas pegawai dan pembaruan progres hingga 100% | Aktivitas tercatat dan status otomatis diperbarui menjadi **SELESAI** | **BERHASIL (OK)** |
| **TC-07** | Modul Keuangan: Siklus Pengajuan & Persetujuan | Input usulan anggaran, persetujuan PPK, dan pencatatan nomor SP2D KPPN | Status pengajuan berubah dari **MENUNGGU** $\rightarrow$ **DISETUJUI** $\rightarrow$ diterbitkan realisasi SP2D | **BERHASIL (OK)** |
| **TC-08** | Verifikasi Integritas Rute Sistem | Pengujian HTTP GET pada seluruh 21 rute sistem SIMPATIK & PRIMA | Seluruh 21 rute mengembalikan respons **HTTP 200 OK** | **BERHASIL (OK)** |

---

## 3. INSTRUMEN PENGUJIAN USER ACCEPTANCE TESTING (UAT)

Instrumen pengujian penerimaan pengguna ini dirancang untuk diisi oleh para calon pengguna di lingkungan BPS Kabupaten Banyuwangi (Admin SAKIP, Kasubbag Umum, Tim Kerja Teknis, dan PPK).

### Skala Penilaian:
- **1** = Sangat Tidak Setuju (STS)
- **2** = Tidak Setuju (TS)
- **3** = Cukup Setuju (CS)
- **4** = Setuju (S)
- **5** = Sangat Setuju (SS)

### Matriks Kuesioner UAT:

| No | Aspek Pengujian / Pernyataan | Kriteria Evaluasi | Skala (1-5) | Catatan Pengguna |
| :---: | :--- | :--- | :---: | :--- |
| **A** | **Aspek Tampilan Antarmuka (UI/UX)** | | | |
| 1 | Desain antarmuka aplikasi modern, rapi, dan mencerminkan identitas BPS (Dark Navy & Orange BPS). | Desain Visual | [ ] | |
| 2 | Struktur navigasi 4 kartu master sidebar (PRIMA, Mitra, Pegawai, Keuangan) memudahkan perpindahan modul. | Kemudahan Navigasi | [ ] | |
| 3 | Tampilan visual grafik (Chart.js) pada dashboard menyajikan informasi capaian secara jelas dan mudah dipahami. | Keterbacaan Informasi | [ ] | |
| 4 | Aplikasi responsif dan nyaman digunakan baik pada layar komputer maupun laptop. | Responsivitas | [ ] | |
| **B** | **Aspek Fungsionalitas Modul PRIMA (AKIP)** | | | |
| 5 | Menu Kelengkapan Dokumen SAKIP memudahkan pemantauan ketersediaan bukti dukung kinerja. | Fungsionalitas | [ ] | |
| 6 | Pengelolaan kategori dan dokumen AKIP berjalan sesuai dengan pedoman evaluasi kinerja organisasi. | Kesesuaian Alur | [ ] | |
| **C** | **Aspek Monitoring Mitra Statistik** | | | |
| 7 | Fitur database mitra memudahkan pencarian dan pengelolaan data mitra Sobat BPS per kecamatan. | Efektivitas | [ ] | |
| 8 | Fitur penugasan dan update realisasi dokumen lapangan berjalan cepat dan transparan. | Operasional | [ ] | |
| 9 | Sistem penilaian evaluasi 3 aspek (Kualitas, Ketepatan, Kerjasama) membantu penentuan predikat mutu mitra. | Pengambilan Keputusan | [ ] | |
| **D** | **Aspek Kinerja & Aktivitas Pegawai** | | | |
| 10 | Pencatatan aktivitas harian pegawai mudah dioperasikan dan mempermudah pelaporan capaian tugas. | Produktivitas | [ ] | |
| 11 | Matriks monitoring tim kerja memberikan gambaran pemerataan beban kerja aparatur secara akurat. | Transparansi Beban Kerja | [ ] | |
| **E** | **Aspek Tracking Keuangan & Anggaran DIPA** | | | |
| 12 | Formulir pengajuan anggaran dengan kalkulator otomatis meminimalkan kesalahan perhitungan volume honor/biaya. | Akurasi Perhitungan | [ ] | |
| 13 | Alur verifikasi dan persetujuan oleh PPK berjalan sistematis sebelum pencatatan realisasi SP2D. | Akuntabilitas | [ ] | |
| 14 | Rekapitulasi serapan anggaran per MAK DIPA membantu pemantauan indikator kinerja pelaksanaan anggaran (IKPA). | Pelaporan Keuangan | [ ] | |
| **F** | **Aspek Keamanan & Keandalan Sistem** | | | |
| 15 | Sistem autentikasi dan pembatasan hak akses (RBAC) melindungi data sensitif sesuai kewenangan pengguna. | Keamanan Sistem | [ ] | |
| 16 | Secara keseluruhan, sistem ini layak diimplementasikan untuk mendukung operasional BPS Kabupaten Banyuwangi. | Kelayakan Implementasi | [ ] | |

---

### Rumus Perhitungan Persentase Kelayakan UAT:
$$\text{Persentase Kelayakan (\%)} = \left( \frac{\text{Total Skor Riil}}{\text{Total Skor Maksimum}} \right) \times 100\%$$

- **81% – 100%**: Sangat Layak / Sangat Diterima
- **61% – 80%**: Layak / Diterima
- **41% – 60%**: Cukup Layak
- **< 40%**: Tidak Layak
