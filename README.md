# PRIMA - Pusat Arsip dan Manajemen AKIP Banyuwangi
> **"Arsip Tertata, Akuntabilitas Terjaga, Kinerja Prima."**
> Platform Digital Terintegrasi Pengelolaan Arsip dan Dokumen AKIP Badan Pusat Statistik (BPS) Kabupaten Banyuwangi.

---

## 📌 1. Tentang Aplikasi

**PRIMA (Pusat Arsip dan Manajemen AKIP Banyuwangi)** adalah aplikasi website modern yang dirancang khusus untuk memenuhi standar tata kelola dan akuntabilitas kinerja instansi pemerintah di lingkungan BPS Kabupaten Banyuwangi.

PRIMA mengatasi tantangan pencarian berkas fisik yang terfragmentasi, memantau tingkat pemenuhan dokumen secara berkala (*real-time compliance tracking*), serta menyatukan akses ke seluruh instrumen digital AKIP (SIMONIK, SINERGI, FRA, PROKSI, JANJIKU, PERMINDOK).

---

## 🚀 2. Tumpukan Teknologi (Tech Stack)

Aplikasi dibangun murni menggunakan stack yang diwajibkan:
- **Backend:** Python 3.12+ & **Flask 3.0+**
- **Template Engine:** Jinja2
- **Database:** **MySQL** (`prima_akip_banyuwangi`) dengan ORM **Flask-SQLAlchemy**
- **Frontend & Styling:** **Tailwind CSS**, Lucide Icons, Chart.js
- **Autentikasi & Keamanan:** **Flask-Login**, **Werkzeug Security** (Password Hashing dengan Scrypt / PBKDF2)
- **Deployment:** Gunicorn (kompatibel dengan Linux, Render, VPS, Docker)

---

## 📂 3. Struktur Direktori Proyek

```
Sistem Informasi BPS/
│
├── app/
│   ├── __init__.py                # Inisialisasi Flask App, DB fallback, Seeder data
│   ├── models.py                  # Model SQLAlchemy: User, Category, Document, Completeness, Link, Activity
│   ├── utils.py                   # Decorator hak akses, logging aktivitas, upload handler
│   │
│   ├── routes/
│   │   ├── auth.py                # Autentikasi Login, Logout, Profil, Ganti Password
│   │   ├── dashboard.py           # Dashboard utama, ringkasan metrik, visualisasi Chart.js
│   │   ├── documents.py           # CRUD dokumen, preview inline, download aman, search & filter
│   │   ├── categories.py          # Manajemen kategori AKIP
│   │   ├── completeness.py        # Checklist kepatuhan AKIP, dokumen belum lengkap, administrasi
│   │   ├── important_links.py     # 8 portal eksternal (SIMONIK, SINERGI, FRA, dll)
│   │   ├── users.py               # Manajemen pengguna (Admin & Pegawai)
│   │   ├── settings.py            # Konfigurasi link eksternal & Audit Trail Log Aktivitas
│   │   └── info.py                # Halaman Tentang PRIMA & Panduan Penggunaan
│   │
│   ├── templates/
│   │   ├── base.html              # Layout master Tailwind CSS
│   │   ├── login.html             # Tampilan login Modern Government Dashboard
│   │   ├── dashboard.html         # Dashboard 7 metrik, 2 grafik interaktif, quick shortcuts
│   │   ├── profile.html           # Pengaturan profil & password
│   │   ├── 404.html & 500.html    # Halaman error responsif
│   │   ├── components/            # Sidebar accordion, navbar, modal preview, footer
│   │   ├── documents/             # Daftar dokumen, view kategori, detail, upload, edit
│   │   ├── completeness/          # Checklist dokumen, belum lengkap, administrasi
│   │   ├── important_links/       # Katalog & halaman detail masing-masing portal
│   │   ├── categories/            # Indeks kategori
│   │   ├── users/                 # Kelola pengguna
│   │   ├── settings/              # Konfigurasi link & riwayat aktivitas
│   │   └── info/                  # Tentang PRIMA & panduan penggunaan
│   │
│   └── static/
│       ├── css/style.css          # Custom styling, accordion smooth scroll & transition
│       ├── js/main.js             # Accordion trigger, mobile drawer, preview modal handler
│       └── uploads/documents/     # Direktori penyimpanan file arsip terunggah
│
├── config.py                      # Konfigurasi aplikasi & database
├── run.py                         # File eksekusi utama (python run.py)
├── requirements.txt               # Dependensi Python
├── .env.example                   # Contoh konfigurasi environment variable
├── .env                           # File konfigurasi aktif
├── schema.sql                     # Skema SQL database MySQL lengkap beserta data awal
├── tailwind.config.js             # Konfigurasi warna resmi PRIMA BPS
├── Procfile                       # Konfigurasi deployment server
└── README.md                      # Dokumentasi komprehensif
```

---

## 🔑 4. Akun Pengguna Default (Siap Pakai)

Sistem sudah dilengkapi dengan *data seeder* otomatis saat aplikasi pertama kali dijalankan:

| Role | Username | Password | Hak Akses |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `admin123` | Akses penuh CRUD dokumen, kelola pengguna, kelola kategori, ubah tautan portal, checklist kelengkapan, dan melihat riwayat aktivitas. |
| **User (Pegawai)**| `pegawai`| `pegawai123` | Melihat dokumen, mencari arsip, filter tahun/status, pratinjau dokumen, dan mengunduh berkas. |

---

## 💻 5. Panduan Menjalankan Aplikasi Secara Lokal

### Langkah 1: Persiapan Environment
Pastikan Python 3.12 atau yang lebih baru telah terpasang.
Buka terminal (Command Prompt / PowerShell / Terminal) pada folder proyek ini:

```bash
# Buat virtual environment (opsional namun disarankan)
python -m venv venv

# Aktifkan virtual environment
# Pada Windows:
venv\Scripts\activate
# Pada macOS/Linux:
source venv/bin/activate
```

### Langkah 2: Instalasi Dependensi
```bash
pip install -r requirements.txt
```

### Langkah 3: Konfigurasi Database MySQL
1. Buka MySQL Server lokal Anda (misal melalui XAMPP, Laragon, MySQL Community Server, atau Docker).
2. Buat database:
   ```sql
   CREATE DATABASE prima_akip_banyuwangi CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
3. Sesuaikan file `.env` dengan kredensial MySQL Anda:
   ```ini
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=
   DB_NAME=prima_akip_banyuwangi
   DATABASE_URL=mysql+pymysql://root:@localhost:3306/prima_akip_banyuwangi
   ```
   *(Opsional: Anda juga dapat langsung mengimpor file `schema.sql` via phpMyAdmin atau MySQL CLI).*

> **Catatan Smart Resiliency:**
> Jika saat pertama kali pengujian lokal service MySQL belum Anda jalankan, aplikasi memiliki mekanisme *graceful fallback* ke SQLite lokal secara otomatis sehingga Anda tetap dapat langsung meninjau seluruh antarmuka dan fitur tanpa kendala fatal.

### Langkah 4: Jalankan Aplikasi
Jalankan perintah berikut:
```bash
python run.py
```

Buka peramban (browser) dan akses alamat:
```
http://localhost:5000
```

---

## 🧭 6. Struktur Navigasi Menu & Submenu (Sidebar Accordion)

Sidebar PRIMA menerapkan animasi accordion mulus dengan indikator aktif dan status drawer pada layar ponsel/tablet:

1. **MENU UTAMA**
   - 📊 `Dashboard`: 7 kartu metrik, 2 grafik interaktif Chart.js, feed dokumen terbaru & aktivitas.
   - ℹ️ `Tentang PRIMA`: Profil, latar belakang, visi-misi AKIP, dan pilar manajemen.
   - 📖 `Panduan Penggunaan`: Panduan langkah pengoperasian fitur bagi pengguna dan admin.

2. **PERENCANAAN**
   - 📄 `Dokumen Perencanaan`: Renstra, perencanaan strategis.
   - 📅 `Rencana Kerja`: RKT tahunan dan program kerja operasional.
   - 🏆 `Perjanjian Kinerja`: Penetapan PK pimpinan dan seluruh ketua tim.
   - 📈 `Rencana Aksi`: Matriks target akselerasi capaian kinerja.
   - 🎯 `Indikator Kinerja Utama`: IKU BPS Kabupaten Banyuwangi.

3. **PENGUKURAN**
   - ⏱️ `Pengukuran Kinerja`: Data pengukuran kinerja periodik.
   - 📊 `Capaian Kinerja`: Analisis realisasi target triwulanan.
   - 📋 `Evaluasi Kinerja`: Hasil reviu capaian target internal.

4. **PELAPORAN**
   - 📘 `Laporan Kinerja`: LAKIP / LKjIP resmi tahunan.
   - 📝 `Laporan Evaluasi`: Hasil evaluasi akuntabilitas kinerja dan rekomendasi.
   - 📎 `Dokumen Pendukung Pelaporan`: Bukti dukung, notula rapat, daftar hadir, dan SK tim.

5. **DOKUMEN PENTING**
   - 🌐 `SIMONIK` (Sistem Informasi Monitoring Kinerja)
   - 🌐 `SINERGI` (Sistem Informasi Penilaian Kinerja Terintegrasi)
   - 🌐 `FRA` (Formulir Rekomendasi Akuntabilitas Kinerja)
   - 🌐 `LINK AKIP JATIM` (Portal Integrasi AKIP BPS Provinsi Jawa Timur)
   - 🌐 `PROKSI` (Program Monitoring Kinerja Strategis)
   - 🌐 `PERMINDOK 2025` (Permintaan Dokumen Administrasi 2025)
   - 🌐 `PERMINDOK 2026` (Permintaan Dokumen Administrasi 2026)
   - 🌐 `JANJIKU` (Pakta Integritas dan Janji Kinerja Pegawai)

6. **KELENGKAPAN**
   - ☑️ `Checklist Dokumen`: Pemantauan pemenuhan dokumen wajib per tahun dengan progress bar.
   - 📑 `Kelengkapan Administrasi`: Rekapitulasi persentase kepatuhan per kategori.
   - 🗄️ `Arsip Dokumen`: Arsip dokumen kinerja tahun-tahun sebelumnya.
   - ⚠️ `Dokumen Belum Lengkap`: Monitoring prioritas dokumen yang belum lengkap untuk tindak lanjut.

---

## 🌐 7. Panduan Deployment (Render / Cloud Hosting)

PRIMA telah disiapkan agar siap di-deploy secara *out-of-the-box* ke layanan hosting seperti **Render.com**:

### Opsi A: Vercel (Rekomendasi Serverless)
Proyek sudah dilengkapi berkas konfigurasi `vercel.json`, `api/index.py`, dan `.vercelignore`:
1. Push repository ini ke GitHub.
2. Buka [Vercel Dashboard](https://vercel.com/new) dan klik **Import Project**.
3. Pilih repository Anda, lalu klik **Deploy**!
4. Panduan lengkap tersedia di [`DEPLOY_VERCEL.md`](DEPLOY_VERCEL.md).

### Opsi B: Render / VPS Linux
1. Unggah kode ke repositori GitHub / GitLab.
2. Pada dashboard **Render**, buat layanan **Web Service** baru dan hubungkan ke repositori Anda.
3. Masukkan konfigurasi berikut:
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn run:app`
4. Tambahkan **Environment Variables**:
   - `FLASK_ENV` = `production`
   - `SECRET_KEY` = `kunci-rahasia-yang-panjang-dan-acak`
   - `DATABASE_URL` = `mysql+pymysql://<user>:<password>@<host>:<port>/<dbname>`
5. Deploy Web Service. Aplikasi PRIMA siap diakses secara online!

---

## 🎨 8. Standar Desain Resmi

- **Navy Blue (`#142B4A`)**: Mencerminkan wibawa institusi pemerintah dan integritas data statistik.
- **Dark Navy (`#0D1B2A`)**: Memberikan kontras tinggi dan kenyamanan visual pada sidebar navigasi.
- **Orange (`#F28C28`)**: Warna identitas BPS yang energik dan melambangkan semangat pelayanan prima.
- **White (`#FFFFFF`) & Light Gray (`#F4F6F9`)**: Menjamin keterbacaan (*readability*) dan kesan bersih minimalis.

---
*Dibuat untuk Badan Pusat Statistik (BPS) Kabupaten Banyuwangi.*

