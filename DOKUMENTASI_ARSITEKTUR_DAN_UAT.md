# DOKUMENTASI SPESIFIKASI ARSITEKTUR, PENGUJIAN BLACK BOX & USER ACCEPTANCE TESTING (UAT)
**SISTEM INFORMASI TATA KELOLA ADMINISTRASI DAN MONITORING KINERJA TERPADU (LENTERA)**
**BADAN PUSAT STATISTIK (BPS) KABUPATEN BANYUWANGI**

---

## 1. IDENTITAS USULAN TUGAS AKHIR
- **Judul Tugas Akhir**: Rancang Bangun Sistem Informasi Tata Kelola Administrasi dan Monitoring Kinerja Terpadu Berbasis Web pada BPS Kabupaten Banyuwangi
- **Nama Sistem**: **LENTERA** (*Layanan Elektronik Terintegrasi untuk Tata Kelola dan Evaluasi Kinerja*)
- **Penyusun / Peneliti**: **Syafiq Burhanuddin**
- **NIM**: **362358302068**
- **Kelas**: **4A TRPL**
- **Program Studi**: Sarjana Terapan (D4) Teknologi Rekayasa Perangkat Lunak
- **Jurusan**: Bisnis dan Informatika, Politeknik Negeri Banyuwangi (2026)
- **Instansi Studi Kasus**: Badan Pusat Statistik (BPS) Kabupaten Banyuwangi
- **Sifat Pengerjaan**: **INDIVIDU** (Seluruh tahapan SDLC dari analisis kebutuhan, perancangan antarmuka dan basis data, implementasi Full-Stack Front-End & Back-End, hingga pengujian Black Box dan User Acceptance Testing/UAT dikerjakan secara mandiri).

---

## 2. LATAR BELAKANG DAN ANALISIS KEBUTUHAN SISTEM

### 2.1. Gambaran Operasional BPS Kabupaten Banyuwangi
BPS Kabupaten Banyuwangi merupakan instansi vertikal pemerintah yang bertugas melaksanakan survei dan sensus statistik (seperti Susenas, Sakernas, survei harga konsumen, survei pertanian, hingga sensus ekonomi/penduduk). Penyelenggaraan kegiatan statistik memerlukan integrasi antara aparatur pegawai internal, Ketua Tim kegiatan teknis, serta mitra statistik lapangan (Sobat BPS) yang ditopang oleh akuntabilitas kinerja instansi pemerintah (SAKIP/AKIP) dan pelacakan anggaran DIPA.

### 2.2. Identifikasi Permasalahan Nyata di Lapangan
1. **Pengarsipan Bukti Dukung SAKIP/AKIP Belum Terpusat**: Dokumen perencanaan, pengukuran, pelaporan, dan evaluasi kinerja masih tersebar pada masing-masing penanggung jawab kegiatan, sehingga pengelola kesulitan memantau unit mana yang belum melengkapi bukti dukung administratif.
2. **Data Mitra Statistik, Rekapitulasi Aktivitas & Evaluasi Belum Terpadu**: Pencatatan ID mitra, jenis kegiatan, volume, alokasi transport, dan honorarium masih tersebar dalam lembar kerja terpisah, menyulitkan Ketua Tim dalam menelusuri rekapitulasi beban kerja bulanan mitra serta riwayat mutunya.
3. **Pemantauan Kinerja Pegawai Belum Terstruktur**: Belum adanya media pencarian riwayat penugasan survei/sensus pegawai internal beserta status penyelesaian beban kerjanya.
4. **Pelacakan Pengajuan dan Realisasi Anggaran Per Akun Masih Manual**: Pengajuan kebutuhan anggaran berbasis kode akun BPS dan pelacakan persetujuannya masih manual, menghambat transparansi pemantauan serapan dan sisa anggaran.

---

## 3. SPESIFIKASI TEKNOLOGI DAN ARSITEKTUR PERANGKAT LUNAK

Sistem dikembangkan menggunakan model **Agile Software Development** (iteratif dan inkremental) dengan spesifikasi teknologi Full-Stack:

| Komponen Arsitektur | Teknologi yang Digunakan | Fungsi Utama pada Sistem LENTERA |
| :--- | :--- | :--- |
| **Front-End** | **HTML5, CSS3, JavaScript, Tailwind CSS & Bootstrap 5** | Membangun antarmuka pengguna web responsif, interaktif, dan modern dengan identitas visual khas BPS (*Dark Navy* `#0D1B2A` dan *Orange BPS* `#F28C28`). Dilengkapi visualisasi Chart.js, ikonografi Lucide, modal kalkulator honor, dan tabel interaktif. |
| **Back-End** | **Python (Flask Framework)** | Menangani logika bisnis sistem, arsitektur modular (*Flask Blueprints*), pemrosesan unggah templat mitra, mekanisme filter pencarian multi-kriteria, kalkulasi otomatis volume dan honorarium akun, alur validasi persetujuan, dan routing aman. |
| **Basis Data** | **MySQL 8** *(dengan SQLite fallback untuk pengujian lokal)* | Basis data relasional terpusat yang menyimpan master data pengguna, berkas dokumen bukti dukung SAKIP/AKIP, direktori mitra statistik, catatan aktivitas pegawai, serta master akun dan transaksi anggaran keuangan. |
| **ORM** | **SQLAlchemy** | Memetakan objek kode Python ke skema basis data relasional (*Object-Relational Mapping*), menjamin integritas transaksi data atomik (*ACID*), serta mengelola relasi *foreign key* antar-entitas secara terstruktur. |
| **Autentikasi & RBAC** | **Flask-Login & Role-Based Access Control (RBAC)** | Mengamankan autentikasi sesi pengguna berbasis kata sandi terenkripsi (*Werkzeug Security hashing*) dan membatasi kewenangan operasional menu berdasarkan peran pengguna. |
| **Pengujian Sistem** | **Black Box Testing & User Acceptance Testing (UAT)** | Menguji kebenaran fungsionalitas antarmuka serta logika pengolahan data (*Black Box Testing* via automated test suite) dan menguji kesesuaian operasional bersama pengguna riil BPS Kabupaten Banyuwangi (*UAT*). |

---

## 4. RUANG LINGKUP 4 PILAR MODUL UTAMA LENTERA

Portal web terpadu LENTERA mengintegrasikan 4 modul operasional inti:

```
+---------------------------------------------------------------------------------------------------+
|                                     PORTAL TERPADU LENTERA BPS                                    |
+----------------------------------+----------------------------------+-----------------------------+
| 1. PRIMA (SAKIP / AKIP)          | 2. MONITORING MITRA              | 3. KINERJA PEGAWAI          |
| - Perencanaan Kinerja (30%)      | - Database Mitra & Impor Templat | - Pencarian Rekam Jejak     |
| - Pengukuran Kinerja (30%)       | - Filter Nama Mitra & Bulan      | - Monitoring Beban Kerja    |
| - Pelaporan Kinerja (15%)        | - Rekapitulasi Beban Penugasan   | - Rekapitulasi Capaian Harian|
| - Evaluasi Kinerja (25%)         | - Evaluasi Kinerja 3 Aspek       |                             |
| - Checklist Dokumen Lengkap      |                                  |                             |
+----------------------------------+----------------------------------+-----------------------------+
| 4. TRACKING KEUANGAN: Pengajuan Berbasis Kode Akun, Validasi BPS (Ya/Tidak), Realisasi SP2D, Sisa |
+---------------------------------------------------------------------------------------------------+
```

### 4.1. Pilar 1: PRIMA — Pusat Arsip & Manajemen AKIP
1. **Penyelarasan Regulasi PermenPANRB Nomor 88 Tahun 2021**:
   Struktur taksonomi dokumen diselaraskan dengan 4 komponen utama evaluasi akuntabilitas kinerja instansi pemerintah:
   - **Perencanaan Kinerja (Bobot 30%)**: Rencana Strategis (Renstra), Rencana Kinerja Tahunan (RKT), Perjanjian Kinerja (PK), dan Indikator Kinerja Utama (IKU).
   - **Pengukuran Kinerja (Bobot 30%)**: Mekanisme pengumpulan data kinerja, definisi operasional, KKPK, DAHA, Proksi, dan pemantauan triwulanan.
   - **Pelaporan Kinerja (Bobot 15%)**: Laporan Kinerja Instansi Pemerintah (LKjIP) dan analisis efisiensi penggunaan sumber daya.
   - **Evaluasi Akuntabilitas Kinerja Internal (Bobot 25%)**: PERMINDOK, LHE AKIP, Berita Acara, serta bukti tindak lanjut rekomendasi perbaikan.
2. **Pemantauan Kelengkapan Administratif**:
   Menyediakan menu **Kelengkapan SAKIP** dan matriks **Checklist Dokumen** dengan status pemenuhan (*Lengkap* / *Belum Lengkap*) untuk mempermudah pra-evaluasi berkas bukti dukung.
3. **Mekanisme Proses Penilaian dan Predikat Hasil Evaluasi**:
   Sistem memfasilitasi evaluator dalam memeriksa dokumen bukti dukung dan menginput skor penilaian berdasarkan 8 skala mutu:
   - `AA` = 100, `A` = 90, `BB` = 80, `B` = 70, `CC` = 60, `C` = 50, `D` = 30, `E` = 0.
   - Hasil diakumulasikan berdasarkan bobot komponen untuk menghasilkan Predikat SAKIP:
     * **90–100**: `AA` (Sangat Memuaskan)
     * **80–90**: `A` (Memuaskan)
     * **70–80**: `BB` (Sangat Baik)
     * **60–70**: `B` (Baik)
     * **50–60**: `CC` (Cukup)
     * **30–50**: `C` (Kurang)
     * **0–30**: `D` (Sangat Kurang)
4. **Tautan Eksternal Terpadu (Link Penting)**:
   Akses cepat satu klik menuju portal nasional BPS: SINERGI, KiPApp, dan MAJAPAHIT.

### 4.2. Pilar 2: MONITORING MITRA — Pengelolaan & Evaluasi Mitra Statistik
1. **Database Induk Mitra & Impor Templat (Peran Admin)**:
   Pencatatan data terstruktur meliputi ID Mitra (Sobat BPS), Nama Lengkap, Alamat/Kecamatan, Nomor Telepon/WhatsApp, serta alokasi Transport dan Honorarium dengan fasilitas impor massal via templat.
2. **Pencarian Spesifik Berdasarkan Nama dan Bulan (Peran Ketua Tim)**:
   Fitur filter terstruktur yang memungkinkan Ketua Tim mencari mitra berdasarkan nama mitra dan bulan pelaksanaan survei untuk memeriksa ketersediaan petugas.
3. **Rekapitulasi Keikutsertaan Kegiatan Mitra**:
   Penyajian daftar seluruh kegiatan yang diikuti oleh seorang mitra/petugas untuk mencegah tumpang tindih penugasan (*overload*) pada periode yang bersamaan.
4. **Evaluasi Kinerja Mitra Pasca-Kegiatan**:
   Pemberian skor evaluasi mutu berbasis 3 indikator: Kualitas Hasil Pencacahan, Ketepatan Waktu Pengumpulan, dan Kedisiplinan/Kerjasama.

### 4.3. Pilar 3: KINERJA PEGAWAI — Monitoring Kinerja Pegawai BPS
1. **Pencarian Rekam Jejak Pegawai**:
   Fitur penelusuran cepat berdasarkan nama atau NIP pegawai untuk melihat keterlibatan pegawai dalam tim survei/sensus statistik.
2. **Monitoring Aktivitas & Capaian Harian**:
   Pencatatan rincian tugas dinas, tanggal mulai-selesai, dan persentase penyelesaian pekerjaan harian hingga mencapai status `SELESAI` (100%).
3. **Rekapitulasi Kinerja Tim Kerja**:
   Visualisasi distribusi beban kerja per tim fungsional (Statistik Sosial, Produksi, Distribusi, Nerwilis, IPDS, dan Bagian Umum).

### 4.4. Pilar 4: TRACKING KEUANGAN — Pengajuan & Monitoring Realisasi Anggaran
1. **Pengajuan Berbasis Database Kode Akun BPS**:
   Pemilihan kode akun MAK (Mata Anggaran Kegiatan) dari basis data yang telah memuat pagu anggaran, satuan, volume, dan standar biaya/honorarium (misal honor pengelolaan kegiatan).
2. **Mekanisme Konfirmasi Validasi Akun BPS (Opsi Ya / Tidak)**:
   Pada tahapan pemeriksaan oleh pengelola keuangan / PPK, setiap item pengajuan memiliki pilihan status konfirmasi validasi:
   - **Ya**: Menandakan item pengajuan telah sesuai kriteria dan disetujui.
   - **Tidak**: Menandakan item pengajuan belum sesuai atau memerlukan revisi perbaikan.
   - Dilengkapi kolom **Catatan Pemeriksaan / Catatan Perbaikan** untuk memberikan transparansi perbaikan kepada pengusul.
3. **Monitoring Realisasi Anggaran**:
   Menyajikan pagu anggaran awal, total usulan diajukan, nominal divalidasi, realisasi pencairan (SP2D), sisa anggaran, dan persentase penyerapan anggaran dalam bentuk tabel dan grafik.
4. **Rekapitulasi & Ekspor Laporan Anggaran**:
   Fitur ekspor data pengajuan dan realisasi anggaran ke format Excel (`.xlsx`) dan PDF untuk arsip pertanggungjawaban keuangan.

---

## 5. RUANG LINGKUP 4 MODUL PENDUKUNG SISTEM

1. **Login & Hak Akses Multi-Peran (RBAC)**:
   - *Administrator*: Manajemen pengguna, hak akses, data master, dan pemantauan sistem.
   - *Pimpinan BPS (Kepala)*: Akses dashboard eksekutif, monitoring kegiatan, dan laporan capaian.
   - *Ketua Tim*: Alokasi penugasan mitra, pengajuan kebutuhan anggaran, dan evaluasi mitra.
   - *Pengelola Keuangan (PPK/KPA)*: Validasi kode akun (Ya/Tidak), catatan perbaikan, persetujuan anggaran, dan pencatatan nomor SP2D.
   - *Pengelola SAKIP/AKIP*: Pengelolaan bukti dukung kriteria evaluasi dan checklist kelengkapan.
   - *Pegawai*: Pelaporan aktivitas kinerja harian dan riwayat penugasan survei.
2. **Dashboard Monitoring Terpadu (Interactive Dashboard)**:
   Menampilkan kartu ringkasan metrik 4 pilar utama secara terintegrasi (total mitra terdaftar, progres penugasan, serapan anggaran akun DIPA, dan kelengkapan dokumen SAKIP) dengan visualisasi Chart.js.
3. **Notifikasi Status Otomatis (In-App Notification)**:
   Notifikasi real-time pada sistem saat terdapat pengajuan anggaran baru, perubahan status validasi kode akun (Ya/Tidak), pembaruan data mitra, atau penambahan dokumen SAKIP.
4. **Pratinjau Dokumen dan Ekspor Laporan (Document Viewer & Report Export)**:
   Fasilitas pratinjau dokumen digital langsung di peramban web (*modal preview*) tanpa harus mengunduh berkas, serta fungsi cetak laporan rekapitulasi format Excel dan PDF.

---

## 6. HASIL PENGUJIAN BLACK BOX TESTING (AUTOMATED TEST SUITE)

Pengujian fungsional *Black Box Testing* dijalankan menggunakan modul automated test suite Python `unittest` (`tests/test_blackbox.py`). Seluruh 8 kasus uji inti berhasil lulus (*PASSED* 100%):

| Kode Kasus Uji | Modul / Skenario Pengujian | Masukan (Input Test Case) | Hasil yang Diharapkan | Status Hasil |
| :---: | :--- | :--- | :--- | :---: |
| **TC-01** | **Keamanan Hak Akses (RBAC)** | Permintaan HTTP GET ke rute privat (`/dashboard`, `/mitra/*`, `/pegawai/*`, `/keuangan/*`) tanpa sesi login | Sistem menolak akses anonim dan mengalihkan (*302 Redirect*) ke `/auth/login` | **BERHASIL (OK)** |
| **TC-02** | **Autentikasi Pengguna Valid** | Kredensial pengguna valid (Username/Email & Password sesuai basis data) | Sistem membuat sesi terautentikasi dan mengarahkan ke dashboard utama | **BERHASIL (OK)** |
| **TC-03** | **Autentikasi Pengguna Tidak Valid** | Username benar, password sengaja disalahkan | Sistem menolak pembuatan sesi login dan menampilkan flash warning error | **BERHASIL (OK)** |
| **TC-04** | **Pilar 1: PRIMA (SAKIP/AKIP)** | Akses `/dashboard` dan `/completeness/checklist` kelengkapan dokumen | Menampilkan matriks kelengkapan 4 kriteria evaluasi beserta status checklist berkas | **BERHASIL (OK)** |
| **TC-05** | **Pilar 2: Monitoring Mitra** | Pendaftaran data mitra baru, alokasi penugasan survei, dan pembaruan dokumen lapangan | Data mitra tersimpan, progres terhitung otomatis, status berganti `SELESAI` saat target terpenuhi | **BERHASIL (OK)** |
| **TC-06** | **Pilar 3: Kinerja Pegawai** | Pencatatan aktivitas dinas pegawai dan pembaruan persentase progres ke 100% | Aktivitas tercatat di basis data dan status otomatis bertransformasi menjadi `SELESAI` | **BERHASIL (OK)** |
| **TC-07** | **Pilar 4: Tracking Keuangan** | Pengajuan berbasis akun, mekanisme validasi akun (Ya/Tidak), dan pencatatan nomor SP2D | Alur status bertahap: `MENUNGGU` $\rightarrow$ Validasi `YA` $\rightarrow$ Pencatatan Realisasi `SP2D` | **BERHASIL (OK)** |
| **TC-08** | **Integritas Seluruh Rute Sistem** | Uji HTTP GET pada seluruh 21 rute navigasi terdaftar (PRIMA, Mitra, Pegawai, Keuangan, Hub) | Seluruh 21 rute mengembalikan respons status **HTTP 200 OK** secara konsisten | **BERHASIL (OK)** |

---

## 7. INSTRUMEN PENGUJIAN USER ACCEPTANCE TESTING (UAT)

Instrumen pengujian ini disiapkan untuk diujikan secara langsung kepada para pemangku kepentingan di lingkungan BPS Kabupaten Banyuwangi:
1. **Ketua Tim Kegiatan Survei / Sensus**
2. **Subbagian Umum & Pengelola Keuangan (PPK)**
3. **Pengelola SAKIP/AKIP & Tim Evaluator**
4. **Pegawai Internal BPS Kabupaten Banyuwangi**
5. **Pimpinan BPS Kabupaten Banyuwangi**

### Skala Penilaian Likert:
- **1** = Sangat Tidak Setuju (STS)
- **2** = Tidak Setuju (TS)
- **3** = Cukup Setuju (CS)
- **4** = Setuju (S)
- **5** = Sangat Setuju (SS)

### Matriks Kuesioner Pengujian UAT:

| No | Parameter Pengujian / Pernyataan Kuesioner | Kriteria Evaluasi | Skala (1-5) | Catatan / Umpan Balik Pengguna |
| :---: | :--- | :--- | :---: | :--- |
| **A** | **Dimensi Tampilan Antarmuka & Kemudahan Penggunaan (UI/UX)** | | | |
| 1 | Desain antarmuka LENTERA modern, bersih, dan konsisten menggunakan identitas BPS (*Dark Navy* & *Orange BPS*). | Estetika Visual | [ ] | |
| 2 | Struktur navigasi 4 kartu master modul (PRIMA, Mitra, Pegawai, Keuangan) dengan sistem expand-collapse memudahkan berpindah halaman. | Navigasi Menu | [ ] | |
| 3 | Visualisasi grafik data (*Chart.js*) menyajikan informasi beban kerja dan serapan anggaran secara jelas dan informatif. | Penyajian Data | [ ] | |
| 4 | Tata letak aplikasi responsif dan nyaman digunakan baik melalui perangkat desktop PC maupun laptop kantor. | Responsivitas | [ ] | |
| **B** | **Dimensi Modul PRIMA (Pusat Arsip & Evaluasi SAKIP/AKIP)** | | | |
| 5 | Struktur taksonomi 4 komponen (Perencanaan, Pengukuran, Pelaporan, Evaluasi Internal) selaras dengan PermenPANRB 88/2021. | Kesesuaian Regulasi | [ ] | |
| 6 | Menu Kelengkapan Dokumen SAKIP memudahkan pemantauan dokumen bukti dukung yang telah lengkap maupun yang belum diunggah. | Efektivitas Arsip | [ ] | |
| 7 | Fitur pratinjau dokumen (*document preview*) mempermudah tim penilai memeriksa bukti dukung tanpa perlu mengunduh file. | Efisiensi Kerja | [ ] | |
| **C** | **Dimensi Monitoring & Evaluasi Mitra Statistik** | | | |
| 8 | Fasilitas database mitra dan impor templat mempermudah pengelolaan direktori petugas mitra sensus/survei. | Manajemen Data | [ ] | |
| 9 | Fitur pencarian spesifik berdasarkan nama mitra dan bulan pelaksanaan membantu Ketua Tim mengalokasikan petugas secara tepat. | Akurasi Alokasi | [ ] | |
| 10 | Formulir evaluasi kinerja mitra 3 aspek (Kualitas, Ketepatan, Kedisiplinan) membantu rekam jejak mutu mitra untuk kegiatan berikutnya. | Penilaian Kinerja | [ ] | |
| **D** | **Dimensi Monitoring Kinerja Pegawai BPS** | | | |
| 11 | Fitur pencarian rekam jejak pegawai mempermudah pemantauan riwayat penugasan dan beban kerja antar-seksi/tim kerja. | Transparansi Kerja | [ ] | |
| 12 | Pencatatan aktivitas harian dan pembaruan progres penyelesaian tugas pegawai praktis dan mudah diperbarui. | Akuntabilitas Pegawai | [ ] | |
| **E** | **Dimensi Tracking Keuangan & Anggaran DIPA** | | | |
| 13 | Formulir pengajuan berbasis database kode akun BPS memudahkan pengisian volume kegiatan dan standar biaya honorarium. | Akurasi Pengajuan | [ ] | |
| 14 | Mekanisme validasi akun BPS dengan opsi Ya / Tidak dan catatan perbaikan memberikan kejelasan status bagi pengusul. | Verifikasi Akun | [ ] | |
| 15 | Dashboard pemantauan realisasi anggaran (pagu, diajukan, SP2D, dan sisa anggaran) menyajikan data serapan secara akurat. | Transparansi Anggaran| [ ] | |
| **F** | **Dimensi Keamanan, RBAC, dan Kelayakan Implementasi Sistem** | | | |
| 16 | Pembatasan hak akses berbasis peran (RBAC) mengamankan data dan membatasi kewenangan sesuai tupoksi masing-masing pengguna. | Keamanan Sistem | [ ] | |
| 17 | Fitur notifikasi otomatis memberikan informasi perubahan status pengajuan secara tepat waktu. | Keandalan Informasi | [ ] | |
| 18 | Secara menyeluruh, sistem informasi terintegrasi LENTERA sangat layak untuk diterapkan pada operasional BPS Kabupaten Banyuwangi. | Kelayakan Sistem | [ ] | |

---

### Rumus Perhitungan Persentase Kelayakan UAT:
$$\text{Persentase Kelayakan (\%)} = \left( \frac{\sum \text{Skor Aktual Jawaban}}{\sum \text{Skor Maksimum}} \right) \times 100\%$$

**Kategori Tingkat Kelayakan:**
- **81% – 100%**: Sangat Layak / Sangat Diterima (*Implementasi Penuh*)
- **61% – 80%**: Layak / Diterima (*Implementasi dengan Penyesuaian Minor*)
- **41% – 60%**: Cukup Layak (*Perlu Penyempurnaan*)
- **< 40%**: Tidak Layak (*Perlu Perancangan Ulang*)

---

## 8. LANDASAN REGULASI DAN DAFTAR REFERENSI
1. **Peraturan Presiden Nomor 95 Tahun 2018** tentang Sistem Pemerintahan Berbasis Elektronik (SPBE).
2. **Peraturan Presiden Nomor 29 Tahun 2014** tentang Sistem Akuntabilitas Kinerja Instansi Pemerintah (SAKIP).
3. **Peraturan Menteri Pendayagunaan Aparatur Negara dan Reformasi Birokrasi Nomor 88 Tahun 2021** tentang Evaluasi Akuntabilitas Kinerja Instansi Pemerintah.
4. **Dybå, T., & Dingsøyr, T. (2008)**. *Empirical Studies of Agile Software Development: A Systematic Review*. Information and Software Technology.
5. **Pressman, R. S., & Maxim, B. R. (2020)**. *Software Engineering: A Practitioner's Approach (9th ed.)*. McGraw-Hill Education.
6. **Grinberg, M. (2018)**. *Flask Web Development: Developing Web Applications with Python (2nd ed.)*. O'Reilly Media.
7. **Sandhu, R. S., et al. (1996)**. *Role-Based Access Control Models*. IEEE Computer, 29(2), 38-47.
8. **ISO/IEC/IEEE 29119-1:2022**. *Software and Systems Engineering: Software Testing*. ISO.
