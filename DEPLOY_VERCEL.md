# 🚀 Panduan Deploy Aplikasi PRIMA ke Vercel

Panduan ini berisi langkah-langkah lengkap untuk mendeploy aplikasi **PRIMA (Pusat Arsip dan Manajemen AKIP Banyuwangi)** ke platform cloud **Vercel**.

---

## 🛠️ Berkas Konfigurasi Vercel yang Sudah Disiapkan

1. **[`api/index.py`](api/index.py)**: Handler Serverless Function WSGI untuk Vercel.
2. **[`vercel.json`](vercel.json)**: Konfigurasi routing & runtime `@vercel/python` untuk memproses seluruh request URL aplikasi.
3. **[`.vercelignore`](.vercelignore)**: Mencegah file cache, virtual environment, dan file sensitif lokal terupload ke cloud.
4. **[`requirements.txt`](requirements.txt)**: Dependensi Python lengkap (Flask, SQLAlchemy, PyMySQL, Cryptography, Psycopg2, Gunicorn, dll).
5. **[`config.py`](config.py)**: Otomatis mendeteksi lingkungan Vercel (`IS_VERCEL`), mendukung cloud database `DATABASE_URL` (MySQL / Postgres) dan fallback otomatis ke folder aman serverless.

---

## 🌟 Metode 1: Deploy via GitHub (Sangat Disarankan & Paling Mudah)

Metode ini adalah cara resmi dan paling praktis dari Vercel:

### Langkah 1: Buat Git Repository & Push ke GitHub

Buka terminal di folder proyek ini (`Sistem Informasi BPS`), lalu jalankan:

```bash
git init
git add .
git commit -m "Siap deploy PRIMA ke Vercel"
```

Buat repository baru di [GitHub](https://github.com/new) (misal: `prima-bps-banyuwangi`), lalu hubungkan dan push:

```bash
git branch -M main
git remote add origin https://github.com/USERNAME-ANDA/prima-bps-banyuwangi.git
git push -u origin main
```

### Langkah 2: Import ke Vercel

1. Buka [https://vercel.com](https://vercel.com) dan login (bisa menggunakan akun GitHub).
2. Di Dashboard Vercel, klik tombol **"Add New..."** lalu pilih **"Project"** (atau buka [vercel.com/new](https://vercel.com/new)).
3. Cari repository `prima-bps-banyuwangi` yang tadi di-push, lalu klik **"Import"**.
4. Biarkan pengaturan default (Framework Preset: **Other** / Auto).
5. *(Opsional tapi disarankan)* Tambahkan **Environment Variables** di bagian bawah jika memiliki database cloud:
   - `SECRET_KEY`: Buat string acak untuk keamanan session (contoh: `prima-rahasia-bps-bwi-2026`).
   - `DATABASE_URL`: Connection string MySQL / PostgreSQL cloud Anda (contoh: `mysql+pymysql://user:pass@host:port/dbname`).
6. Klik tombol **"Deploy"**!
7. Tunggu sekitar 1–2 menit hingga proses build selesai. Vercel akan memberikan domain publik gratis (misal: `https://prima-bps-banyuwangi.vercel.app`).

---

## 💻 Metode 2: Deploy via Terminal (Vercel CLI)

Jika Anda ingin langsung mendeploy dari terminal tanpa harus push ke GitHub:

### Langkah 1: Pasang Vercel CLI

Pastikan [Node.js](https://nodejs.org) terpasang di komputer Anda, lalu buka terminal dan pasang CLI Vercel:

```bash
npm install -g vercel
```

### Langkah 2: Jalankan Perintah Deploy

Di dalam folder proyek ini:

```bash
vercel
```

Ikuti petunjuk interaktif di terminal:
1. `Set up and deploy?` → Tekan **Y**
2. `Which scope?` → Pilih akun Vercel Anda
3. `Link to existing project?` → Ketik **N**
4. `What's your project's name?` → Tekan Enter (atau ketik `prima-banyuwangi`)
5. `In which directory is your code located?` → Tekan Enter (`./`)
6. Tunggu proses upload dan deploy selesai.

Untuk mendeploy ke versi produksi:
```bash
vercel --prod
```

---

## 🗄️ Catatan Penting Mengenai Database di Vercel

Platform Vercel berbasis **Serverless Functions** (stateless). Artinya:
- **Tanpa Database Eksternal**: Aplikasi PRIMA tetap **langsung aktif dan bisa dibuka** berkat fitur auto-fallback ke SQLite internal. Namun, data sesi uji coba akan direset ketika serverless function memasuki masa idle / cold restart.
- **Untuk Produksi Permanen (Disarankan)**:
  Cukup buat database gratis di salah satu penyedia cloud:
  1. **MySQL Cloud**: [Aiven](https://aiven.io), [Clever Cloud](https://www.clever-cloud.com), [TiDB Cloud](https://tidbcloud.com), atau [Railway](https://railway.app).
  2. **PostgreSQL Cloud**: [Neon Database](https://neon.tech) (bisa dipasang 1-klik langsung lewat menu *Storage* / *Integrations* di Dashboard Vercel) atau [Supabase](https://supabase.com).
  
  Lalu salin URL koneksi tersebut ke **Vercel Settings → Environment Variables** dengan nama:
  `DATABASE_URL = <connection_string_database_anda>`

---

## 🔐 Kredensial Login Default

Saat pertama kali dibuka setelah deploy, akun default sudah terdaftar otomatis:
- **Administrator**:
  - Username: `admin`
  - Password: `admin123`
- **Pegawai Regular**:
  - Username: `pegawai`
  - Password: `pegawai123`
