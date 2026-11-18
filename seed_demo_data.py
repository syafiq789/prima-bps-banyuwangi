"""
Skrip Seeder Data Demonstrasi BPS Kabupaten Banyuwangi
Mengisi data realistis untuk 4 Modul Terpadu:
1. PRIMA (Pusat Arsip & SAKIP/AKIP)
2. MONITORING MITRA (Master Mitra, Penugasan Survei, & Evaluasi)
3. KINERJA PEGAWAI (Aparatur Organik & Log Aktivitas Harian)
4. TRACKING KEUANGAN (MAK DIPA 429215, Komponen, Pengajuan, Persetujuan, & SP2D)
"""

import os
from datetime import datetime, date, timedelta
from app import create_app
from app.models import (
    db, User, Category, Document, DocumentCompleteness, Activity,
    Mitra, Kegiatan, PenugasanMitra, EvaluasiMitra,
    Pegawai, AktivitasPegawai, AkunAnggaran, KomponenAnggaran,
    PengajuanAnggaran, PersetujuanAnggaran, RealisasiAnggaran
)

app = create_app()

def run_seed():
    with app.app_context():
        print("Mulai mengisi data demonstrasi 4 modul terpadu...")

        # ---------------------------------------------------------------------
        # Ambil akun pengguna admin & approver
        # ---------------------------------------------------------------------
        admin_user = User.query.filter_by(username='tfdewanto').first() or User.query.filter_by(role='admin').first()
        ppk_user = User.query.filter_by(username='ppk').first() or admin_user
        kpa_user = User.query.filter_by(username='kpa').first() or admin_user

        # =====================================================================
        # 1. MODUL PRIMA (Arsip & SAKIP Banyuwangi)
        # =====================================================================
        print("1. Mengisi data Modul PRIMA...")
        docs_data = [
            {
                "title": "Rencana Strategis (Renstra) BPS Kabupaten Banyuwangi 2025-2029",
                "cat_slug": "renstra",
                "year": 2025,
                "file_type": "pdf",
                "original_filename": "Renstra_BPS_Banyuwangi_2025_2029_Final.pdf",
                "file_size": 2845600,
                "description": "Dokumen resmi Rencana Strategis (Renstra) BPS Kabupaten Banyuwangi periode 2025-2029.",
                "drive_url": "https://drive.google.com/drive/folders/1tG_Z7uqrJQ0B8EJxbgsN-NgfgSocK1uJ"
            },
            {
                "title": "Perjanjian Kinerja (PK) Kepala BPS Kabupaten Banyuwangi Tahun 2025",
                "cat_slug": "perjanjian-kinerja",
                "year": 2025,
                "file_type": "pdf",
                "original_filename": "Perjanjian_Kinerja_Kepala_BPS_Banyuwangi_2025.pdf",
                "file_size": 1420500,
                "description": "Perjanjian Kinerja penetapan target strategis tahunan antara Kepala Kantor dengan Pimpinan BPS Provinsi.",
                "drive_url": "https://drive.google.com/drive/folders/1sPNbUk3DsKIPL4XS6ZWagtCp7Oxyp7Sy"
            },
            {
                "title": "Kertas Kerja Pengukuran Kinerja (KKPK) Triwulan IV 2024",
                "cat_slug": "kkpk",
                "year": 2024,
                "file_type": "xlsx",
                "original_filename": "KKPK_BPS_Banyuwangi_TW4_2024.xlsx",
                "file_size": 890400,
                "description": "Kertas Kerja Pengukuran Kinerja capaian output fungsional dan realisasi anggaran triwulanan.",
                "drive_url": "https://drive.google.com/drive/folders/1X3YlxX-Y9MHur9xvSxwktSHXeYeD7qY6"
            },
            {
                "title": "Dokumen Arsip Hasil Analisis (DAHA) SAKIP 2024",
                "cat_slug": "daha",
                "year": 2024,
                "file_type": "pdf",
                "original_filename": "DAHA_SAKIP_BPS_Banyuwangi_2024.pdf",
                "file_size": 3210400,
                "description": "Arsip data dan analisis hasil capaian indikator kinerja utama (IKU) operasional statistik.",
                "drive_url": "https://drive.google.com/drive/folders/1ZXCDu6HCLKHx-PwuGlhzsDQj1ck2UQpE"
            },
            {
                "title": "Laporan Kinerja Instansi Pemerintah (LAKIP) BPS Banyuwangi 2024",
                "cat_slug": "laporan-kinerja",
                "year": 2024,
                "file_type": "pdf",
                "original_filename": "LAKIP_BPS_Kabupaten_Banyuwangi_2024.pdf",
                "file_size": 4520100,
                "description": "Laporan pertanggungjawaban akuntabilitas kinerja instansi pemerintah (LKjIP / LAKIP) tahun 2024.",
                "drive_url": "https://drive.google.com/drive/folders/1APuhRzJikTUZVLujq34rhQ-z1KAzmAQ3"
            },
            {
                "title": "Laporan Hasil Evaluasi (LHE) AKIP BPS Banyuwangi 2024",
                "cat_slug": "lhe-akip",
                "year": 2024,
                "file_type": "pdf",
                "original_filename": "LHE_AKIP_BPS_Banyuwangi_2024_Inspektorat.pdf",
                "file_size": 1750200,
                "description": "Laporan evaluasi SAKIP dari Inspektorat Utama BPS dengan nilai capaian predikat A (Memuaskan).",
                "drive_url": "https://drive.google.com/drive/folders/1qafMSDY-mGhsAsC1IhNWZ1PLDbdDBRxl"
            },
            {
                "title": "SK Tim Kerja Pengelola SAKIP BPS Banyuwangi 2025",
                "cat_slug": "sk-tim-kerja-sakip",
                "year": 2025,
                "file_type": "pdf",
                "original_filename": "SK_Tim_Kerja_SAKIP_3510_Tahun_2025.pdf",
                "file_size": 940000,
                "description": "Surat Keputusan penetapan tim pengelola SAKIP, PIC data per fungsi, dan verifikator akuntabilitas.",
                "drive_url": "https://drive.google.com/drive/folders/1CNCg7oMRIuZLiYzs0h_Bju3EVhsfZPPV"
            },
            {
                "title": "Sasaran Kinerja Pegawai (SKP) Aparatur BPS Banyuwangi 2024-2025",
                "cat_slug": "skp",
                "year": 2025,
                "file_type": "pdf",
                "original_filename": "SKP_Kompilasi_ASN_BPS_Banyuwangi_2025.pdf",
                "file_size": 2100500,
                "description": "Matriks penetapan dan penilaian sasaran kinerja pegawai (SKP) seluruh aparatur ASN BPS Banyuwangi.",
                "drive_url": "https://drive.google.com/drive/folders/13MaRpuGKJqjLFbkYpdrVwo5PfQUI8pRA"
            }
        ]

        for d in docs_data:
            cat = Category.query.filter_by(slug=d["cat_slug"]).first()
            if cat:
                existing_doc = Document.query.filter_by(title=d["title"]).first()
                if not existing_doc:
                    new_doc = Document(
                        title=d["title"],
                        category_id=cat.id,
                        year=d["year"],
                        file_type=d["file_type"],
                        filename=d["original_filename"],
                        original_filename=d["original_filename"],
                        file_size=d["file_size"],
                        description=d["description"],
                        drive_url=d["drive_url"],
                        uploaded_by=admin_user.id if admin_user else 1,
                        status='lengkap'
                    )
                    db.session.add(new_doc)
                    db.session.flush()

                    # Cari item kelengkapan yang cocok dan set terpenuhi
                    comp_item = DocumentCompleteness.query.filter(
                        DocumentCompleteness.category_id == cat.id,
                        DocumentCompleteness.year == d["year"]
                    ).first()
                    if comp_item:
                        comp_item.is_fulfilled = True
                        comp_item.document_id = new_doc.id
                        comp_item.notes = f"Terpenuhi dengan dokumen: {d['title']}"

        # Catat aktivitas PRIMA
        if Activity.query.count() < 3:
            acts = [
                Activity(user_id=admin_user.id if admin_user else 1, action="UPLOAD_DOKUMEN", description="Mengunggah Rencana Strategis (Renstra) BPS Banyuwangi 2025-2029"),
                Activity(user_id=admin_user.id if admin_user else 1, action="VERIFIKASI_SAKIP", description="Verifikasi kelengkapan bukti dukung LAKIP 2024"),
                Activity(user_id=admin_user.id if admin_user else 1, action="UPDATE_STATUS", description="Memperbarui status dokumen Perjanjian Kinerja 2025 menjadi Lengkap")
            ]
            for a in acts:
                db.session.add(a)

        db.session.commit()

        # =====================================================================
        # 2. MODUL MONITORING MITRA
        # =====================================================================
        print("2. Mengisi data Modul MONITORING MITRA...")
        mitra_seed_list = [
            {
                "id_sobat": "351001001",
                "nama_lengkap": "Bambang Sutrisno, S.E.",
                "email": "bambang.sutrisno@gmail.com",
                "alamat": "Jl. Ikan Paus No. 12, Kel. Kampung Mandar",
                "no_hp": "081234567801",
                "jenis_kelamin": "Laki-laki",
                "desa": "Kampung Mandar",
                "kecamatan": "Banyuwangi",
                "keahlian": "Pemeriksaan Dokumen (PML)"
            },
            {
                "id_sobat": "351002002",
                "nama_lengkap": "Siti Nurjanah, S.Stat.",
                "email": "siti.nurjanah@gmail.com",
                "alamat": "Jl. Raya Rogojampi No. 45, Gitik",
                "no_hp": "081234567802",
                "jenis_kelamin": "Perempuan",
                "desa": "Gitik",
                "kecamatan": "Rogojampi",
                "keahlian": "Pendataan Lapangan (CAPI)"
            },
            {
                "id_sobat": "351003003",
                "nama_lengkap": "Agus Kurniawan, S.P.",
                "email": "agus.kurniawan@gmail.com",
                "alamat": "Jl. Gajah Mada No. 8, Genteng Kulon",
                "no_hp": "081234567803",
                "jenis_kelamin": "Laki-laki",
                "desa": "Genteng Kulon",
                "kecamatan": "Genteng",
                "keahlian": "Pendataan Lapangan (CAPI)"
            },
            {
                "id_sobat": "351004004",
                "nama_lengkap": "Dewi Anggraini, S.Si.",
                "email": "dewi.anggraini@gmail.com",
                "alamat": "Dusun Krajan RT 02/01, Desa Kemiren",
                "no_hp": "081234567804",
                "jenis_kelamin": "Perempuan",
                "desa": "Kemiren",
                "kecamatan": "Glagah",
                "keahlian": "Pengolahan & Entri Data"
            },
            {
                "id_sobat": "351005005",
                "nama_lengkap": "Rahmat Hidayat, S.Kom.",
                "email": "rahmat.hidayat@gmail.com",
                "alamat": "Jl. Ki Hajar Dewantara No. 19",
                "no_hp": "081234567805",
                "jenis_kelamin": "Laki-laki",
                "desa": "Singojuruh",
                "kecamatan": "Singojuruh",
                "keahlian": "Listing / Geotagging Wilkerstat"
            },
            {
                "id_sobat": "351006006",
                "nama_lengkap": "Lestari Wulandari, S.Pd.",
                "email": "lestari.w@gmail.com",
                "alamat": "Jl. Jember No. 102, Kedayunan",
                "no_hp": "081234567806",
                "jenis_kelamin": "Perempuan",
                "desa": "Kedayunan",
                "kecamatan": "Kabat",
                "keahlian": "Pendataan Lapangan (CAPI)"
            },
            {
                "id_sobat": "351007007",
                "nama_lengkap": "Eko Prasetyo",
                "email": "eko.prasetyo@gmail.com",
                "alamat": "Jl. Parijatah No. 14, Sukomaju",
                "no_hp": "081234567807",
                "jenis_kelamin": "Laki-laki",
                "desa": "Sukomaju",
                "kecamatan": "Srono",
                "keahlian": "Pendataan Lapangan (CAPI)"
            },
            {
                "id_sobat": "351008008",
                "nama_lengkap": "Nurlaila Fitriani, S.M.",
                "email": "nurlaila.fitri@gmail.com",
                "alamat": "Jl. Pelabuhan Muncar No. 3",
                "no_hp": "081234567808",
                "jenis_kelamin": "Perempuan",
                "desa": "Kedungrejo",
                "kecamatan": "Muncar",
                "keahlian": "Pemeriksaan Dokumen (PML)"
            },
            {
                "id_sobat": "351009009",
                "nama_lengkap": "Ahmad Fauzi",
                "email": "ahmad.fauzi@gmail.com",
                "alamat": "Jl. Hayam Wuruk No. 27",
                "no_hp": "081234567809",
                "jenis_kelamin": "Laki-laki",
                "desa": "Mojopanggung",
                "kecamatan": "Giri",
                "keahlian": "Listing / Geotagging Wilkerstat"
            },
            {
                "id_sobat": "351010010",
                "nama_lengkap": "Dian Permatasari",
                "email": "dian.permata@gmail.com",
                "alamat": "Jl. Raya Benculuk No. 55",
                "no_hp": "081234567810",
                "jenis_kelamin": "Perempuan",
                "desa": "Benculuk",
                "kecamatan": "Cluring",
                "keahlian": "Pengolahan & Entri Data"
            }
        ]

        created_mitras = {}
        for m_data in mitra_seed_list:
            m = Mitra.query.filter_by(id_sobat=m_data["id_sobat"]).first()
            if not m:
                m = Mitra(**m_data)
                db.session.add(m)
                db.session.flush()
            created_mitras[m_data["id_sobat"]] = m

        # Kegiatan Survei / Sensus BPS Banyuwangi
        kegiatan_seed_list = [
            {
                "kode_kegiatan": "SRV-SUS-202501",
                "nama_kegiatan": "Survei Sosial Ekonomi Nasional (Susenas) Maret 2025",
                "tahun": 2025,
                "bulan": "03",
                "tim_kerja": "Tim Distribusi",
                "tanggal_mulai": date(2025, 3, 1),
                "tanggal_selesai": date(2025, 3, 31),
                "status": "BERJALAN",
                "progres_persen": 70
            },
            {
                "kode_kegiatan": "SRV-SAK-202502",
                "nama_kegiatan": "Survei Angkatan Kerja Nasional (Sakernas) Februari 2025",
                "tahun": 2025,
                "bulan": "02",
                "tim_kerja": "Tim Distribusi",
                "tanggal_mulai": date(2025, 2, 1),
                "tanggal_selesai": date(2025, 2, 28),
                "status": "SELESAI",
                "progres_persen": 100
            },
            {
                "kode_kegiatan": "SRV-KSA-202501",
                "nama_kegiatan": "Kerangka Sampel Area (KSA) Padi Subround I 2025",
                "tahun": 2025,
                "bulan": "01",
                "tim_kerja": "Tim Produksi",
                "tanggal_mulai": date(2025, 1, 1),
                "tanggal_selesai": date(2025, 4, 30),
                "status": "BERJALAN",
                "progres_persen": 85
            },
            {
                "kode_kegiatan": "SRV-SHP-202502",
                "nama_kegiatan": "Survei Harga Perdagangan Besar & Konsumen Bulanan (SHPB/HKD)",
                "tahun": 2025,
                "bulan": "02",
                "tim_kerja": "Tim Distribusi",
                "tanggal_mulai": date(2025, 2, 1),
                "tanggal_selesai": date(2025, 2, 28),
                "status": "SELESAI",
                "progres_persen": 100
            },
            {
                "kode_kegiatan": "SRV-PDR-202501",
                "nama_kegiatan": "Penyusunan PDRB Kabupaten Banyuwangi Triwulan I",
                "tahun": 2025,
                "bulan": "03",
                "tim_kerja": "Tim Neraca",
                "tanggal_mulai": date(2025, 1, 15),
                "tanggal_selesai": date(2025, 4, 15),
                "status": "BERJALAN",
                "progres_persen": 55
            },
            {
                "kode_kegiatan": "SRV-TI-202501",
                "nama_kegiatan": "Pemutakhiran Peta Digital & Wilkerstat Sensus Banyuwangi",
                "tahun": 2025,
                "bulan": "02",
                "tim_kerja": "Tim PLS",
                "tanggal_mulai": date(2025, 2, 1),
                "tanggal_selesai": date(2025, 3, 31),
                "status": "BERJALAN",
                "progres_persen": 75
            }
        ]

        created_kegiatans = {}
        for k_data in kegiatan_seed_list:
            k = Kegiatan.query.filter_by(kode_kegiatan=k_data["kode_kegiatan"]).first()
            if not k:
                k = Kegiatan(**k_data)
                db.session.add(k)
                db.session.flush()
            created_kegiatans[k_data["kode_kegiatan"]] = k

        # Penugasan Mitra
        penugasan_seeds = [
            # Susenas Maret 2025
            {"sobat": "351001001", "keg": "SRV-SUS-202501", "peran": "PML", "target": 60, "realisasi": 45, "honor": 3600000, "status": "PROSES"},
            {"sobat": "351002002", "keg": "SRV-SUS-202501", "peran": "PPL", "target": 40, "realisasi": 30, "honor": 2800000, "status": "PROSES"},
            {"sobat": "351003003", "keg": "SRV-SUS-202501", "peran": "PPL", "target": 40, "realisasi": 28, "honor": 2800000, "status": "PROSES"},
            {"sobat": "351004004", "keg": "SRV-SUS-202501", "peran": "PENGOLAH", "target": 80, "realisasi": 60, "honor": 2400000, "status": "PROSES"},

            # Sakernas Februari 2025 (SELESAI)
            {"sobat": "351006006", "keg": "SRV-SAK-202502", "peran": "PPL", "target": 35, "realisasi": 35, "honor": 2450000, "status": "SELESAI"},
            {"sobat": "351007007", "keg": "SRV-SAK-202502", "peran": "PPL", "target": 35, "realisasi": 35, "honor": 2450000, "status": "SELESAI"},
            {"sobat": "351008008", "keg": "SRV-SAK-202502", "peran": "PML", "target": 70, "realisasi": 70, "honor": 3500000, "status": "SELESAI"},

            # KSA Padi Subround I
            {"sobat": "351005005", "keg": "SRV-KSA-202501", "peran": "PPL", "target": 24, "realisasi": 20, "honor": 1920000, "status": "PROSES"},
            {"sobat": "351009009", "keg": "SRV-TI-202501", "peran": "PPL", "target": 50, "realisasi": 38, "honor": 2500000, "status": "PROSES"},
            {"sobat": "351010010", "keg": "SRV-SHP-202502", "peran": "PENGOLAH", "target": 30, "realisasi": 30, "honor": 1800000, "status": "SELESAI"}
        ]

        for p_data in penugasan_seeds:
            mitra = created_mitras.get(p_data["sobat"])
            kegiatan = created_kegiatans.get(p_data["keg"])
            if mitra and kegiatan:
                p = PenugasanMitra.query.filter_by(mitra_id=mitra.id, kegiatan_id=kegiatan.id).first()
                if not p:
                    p = PenugasanMitra(
                        mitra_id=mitra.id,
                        kegiatan_id=kegiatan.id,
                        peran=p_data["peran"],
                        target_dokumen=p_data["target"],
                        realisasi_dokumen=p_data["realisasi"],
                        honor_total=p_data["honor"],
                        status=p_data["status"],
                        created_by=admin_user.id if admin_user else 1
                    )
                    db.session.add(p)
                    db.session.flush()

                # Evaluasi jika penugasan selesai
                if p.status == "SELESAI":
                    ev = EvaluasiMitra.query.filter_by(penugasan_id=p.id).first()
                    if not ev:
                        ev = EvaluasiMitra(
                            penugasan_id=p.id,
                            mitra_id=mitra.id,
                            nilai_kualitas=95,
                            nilai_ketepatan=98,
                            nilai_kerjasama=94,
                            catatan=f"Kinerja {mitra.nama_lengkap} sangat baik, dokumen bersih, zero-error validation, direkomendasikan untuk penugasan sensus/survei berikutnya.",
                            evaluator_id=admin_user.id if admin_user else 1
                        )
                        db.session.add(ev)

        db.session.commit()

        # =====================================================================
        # 3. MODUL KINERJA PEGAWAI
        # =====================================================================
        print("3. Mengisi data Modul KINERJA PEGAWAI...")
        pegawai_seed_list = [
            {
                "nip": "198501012010011001",
                "nama_lengkap": "T.F. Dewanto, S.Si., M.Stat.",
                "jabatan": "Kepala BPS Kabupaten Banyuwangi",
                "tim_kerja": "Subbagian Umum",
                "email": "tfdewanto@bps.go.id"
            },
            {
                "nip": "198705122011011003",
                "nama_lengkap": "Abdul Hadi, S.E.",
                "jabatan": "Kepala Subbagian Umum",
                "tim_kerja": "Subbagian Umum",
                "email": "abdulhadi@bps.go.id"
            },
            {
                "nip": "199203152015021002",
                "nama_lengkap": "Hendra Kusuma, S.Tr.Stat.",
                "jabatan": "Statistisi Ahli Muda",
                "tim_kerja": "Tim Neraca Wilayah & Analisis Statistik",
                "email": "hendra.k@bps.go.id"
            },
            {
                "nip": "199408202016022001",
                "nama_lengkap": "Anisa Rahmawati, S.Si.",
                "jabatan": "Statistisi Ahli Pertama",
                "tim_kerja": "Tim Statistik Sosial",
                "email": "anisa.r@bps.go.id"
            },
            {
                "nip": "199106182014031002",
                "nama_lengkap": "Dwi Santoso, S.P.",
                "jabatan": "Statistisi Ahli Pertama",
                "tim_kerja": "Tim Statistik Produksi",
                "email": "dwi.s@bps.go.id"
            },
            {
                "nip": "199309252016012003",
                "nama_lengkap": "Ratna Juwita, S.E.",
                "jabatan": "Statistisi Pelaksana Lanjutan",
                "tim_kerja": "Tim Statistik Distribusi",
                "email": "ratna.j@bps.go.id"
            },
            {
                "nip": "199511102018011002",
                "nama_lengkap": "Fajar Nugroho, S.Kom.",
                "jabatan": "Pranata Komputer Ahli Pertama",
                "tim_kerja": "Tim Pengolahan & TI (IPDS)",
                "email": "fajar.n@bps.go.id"
            },
            {
                "nip": "199008202014031003",
                "nama_lengkap": "Maya Indrawati, A.Md.",
                "jabatan": "Pengelola Pengadaan Barang/Jasa",
                "tim_kerja": "Subbagian Umum",
                "email": "maya.i@bps.go.id"
            }
        ]

        created_pegs = {}
        for peg_data in pegawai_seed_list:
            p = Pegawai.query.filter_by(nip=peg_data["nip"]).first()
            if not p:
                p = Pegawai(**peg_data)
                db.session.add(p)
                db.session.flush()
            created_pegs[peg_data["nip"]] = p

        # Aktivitas Pegawai
        aktivitas_seeds = [
            {
                "nip": "198501012010011001",
                "keg_kode": "SRV-SUS-202501",
                "judul": "Pengarahan Pembukaan Briefing Petugas Susenas Maret 2025",
                "deskripsi": "Memberikan arahan integritas pendataan statistik dan komitmen kualitas data kemiskinan makro Banyuwangi.",
                "tgl_mulai": date(2025, 2, 25),
                "tgl_selesai": date(2025, 2, 26),
                "progres": 100,
                "status": "SELESAI"
            },
            {
                "nip": "199203152015021002",
                "keg_kode": "SRV-PDR-202501",
                "judul": "Penyusunan Publikasi Banyuwangi Dalam Angka 2025 & PDRB",
                "deskripsi": "Kompilasi tabel sektoral, rekonsiliasi data dinas teknis, dan verifikasi angka PDRB triwulanan.",
                "tgl_mulai": date(2025, 1, 15),
                "tgl_selesai": date(2025, 3, 15),
                "progres": 85,
                "status": "PROSES"
            },
            {
                "nip": "199408202016022001",
                "keg_kode": "SRV-SUS-202501",
                "judul": "Pengawasan Lapangan & Supervisi Kualitas Susenas di Kec. Rogojampi",
                "deskripsi": "Pemeriksaan konsistensi kuesioner Kor dan Konsumsi/Pengeluaran pada rumah tangga sampel terpilih.",
                "tgl_mulai": date(2025, 3, 2),
                "tgl_selesai": date(2025, 3, 20),
                "progres": 70,
                "status": "PROSES"
            },
            {
                "nip": "199106182014031002",
                "keg_kode": "SRV-KSA-202501",
                "judul": "Pemeriksaan Foto Amatan Kerangka Sampel Area Padi Subround I",
                "deskripsi": "Verifikasi visual fase vegetatif, generatif, dan panen pada segmen sawah wilayah Banyuwangi Utara.",
                "tgl_mulai": date(2025, 1, 25),
                "tgl_selesai": date(2025, 2, 28),
                "progres": 100,
                "status": "SELESAI"
            },
            {
                "nip": "199309252016012003",
                "keg_kode": "SRV-SHP-202502",
                "judul": "Diseminasi Angka Indeks Harga Konsumen (IHK) & Inflasi Banyuwangi",
                "deskripsi": "Penyusunan Berita Resmi Statistik (BRS) inflasi bulanan dan rilis data ke media dan Pemkab Banyuwangi.",
                "tgl_mulai": date(2025, 2, 20),
                "tgl_selesai": date(2025, 3, 1),
                "progres": 100,
                "status": "SELESAI"
            },
            {
                "nip": "199511102018011002",
                "keg_kode": "SRV-TI-202501",
                "judul": "Maintenance Server Backup & Sinkronisasi CAPI Fasih BPS",
                "deskripsi": "Pemeliharaan database Wilkerstat dan optimasi alokasi beban server pendataan elektronik CAPI.",
                "tgl_mulai": date(2025, 2, 1),
                "tgl_selesai": date(2025, 3, 31),
                "progres": 65,
                "status": "PROSES"
            },
            {
                "nip": "198705122011011003",
                "keg_kode": None,
                "judul": "Penyusunan Laporan Akuntabilitas Kinerja Instansi Pemerintah (LAKIP)",
                "deskripsi": "Koordinasi pengumpulan data capaian IKU seluruh tim teknis dan evaluasi efisiensi anggaran DIPA.",
                "tgl_mulai": date(2025, 1, 5),
                "tgl_selesai": date(2025, 2, 10),
                "progres": 100,
                "status": "SELESAI"
            }
        ]

        for act_data in aktivitas_seeds:
            peg = created_pegs.get(act_data["nip"])
            keg = created_kegiatans.get(act_data["keg_kode"]) if act_data["keg_kode"] else None
            if peg:
                existing_act = AktivitasPegawai.query.filter_by(pegawai_id=peg.id, judul_aktivitas=act_data["judul"]).first()
                if not existing_act:
                    act = AktivitasPegawai(
                        pegawai_id=peg.id,
                        kegiatan_id=keg.id if keg else None,
                        judul_aktivitas=act_data["judul"],
                        deskripsi=act_data["deskripsi"],
                        tanggal_mulai=act_data["tgl_mulai"],
                        tanggal_selesai=act_data["tgl_selesai"],
                        persentase_selesai=act_data["progres"],
                        status=act_data["status"],
                        created_by=admin_user.id if admin_user else 1
                    )
                    db.session.add(act)

        db.session.commit()

        # =====================================================================
        # 4. MODUL TRACKING KEUANGAN
        # =====================================================================
        print("4. Mengisi data Modul TRACKING KEUANGAN...")
        akun_seed_list = [
            {
                "kode_akun": "521213",
                "nama_akun": "Belanja Honor Output Kegiatan (Honor Mitra Sensus & Survei)",
                "kategori": "HONOR",
                "pagu_awal": 1450000000
            },
            {
                "kode_akun": "524111",
                "nama_akun": "Belanja Perjalanan Dinas Biasa (Supervisi & Monitoring Lapangan)",
                "kategori": "PERJADIN",
                "pagu_awal": 380000000
            },
            {
                "kode_akun": "521211",
                "nama_akun": "Belanja Bahan Operasional, ATK, & Perlengkapan Petugas",
                "kategori": "BAHAN",
                "pagu_awal": 210000000
            },
            {
                "kode_akun": "522111",
                "nama_akun": "Belanja Langganan Daya dan Jasa Telekomunikasi/Internet Satker",
                "kategori": "LAINNYA",
                "pagu_awal": 95000000
            }
        ]

        created_akuns = {}
        for a_data in akun_seed_list:
            ak = AkunAnggaran.query.filter_by(kode_akun=a_data["kode_akun"]).first()
            if not ak:
                ak = AkunAnggaran(**a_data)
                db.session.add(ak)
                db.session.flush()
            created_akuns[a_data["kode_akun"]] = ak

        # Komponen Anggaran
        komponen_seed_list = [
            {
                "kode_komponen": "051.01.A",
                "nama_komponen": "Honor Petugas Pencacah Lapangan (PPL) Susenas Maret 2025",
                "kode_akun": "521213",
                "keg_kode": "SRV-SUS-202501",
                "pagu": 320000000
            },
            {
                "kode_komponen": "051.01.B",
                "nama_komponen": "Honor Petugas Pemeriksa Lapangan (PML) Susenas Maret 2025",
                "kode_akun": "521213",
                "keg_kode": "SRV-SUS-202501",
                "pagu": 140000000
            },
            {
                "kode_komponen": "052.02.A",
                "nama_komponen": "Biaya Supervisi Perjalanan Dinas Monitoring KSA Padi Subround I",
                "kode_akun": "524111",
                "keg_kode": "SRV-KSA-202501",
                "pagu": 65000000
            },
            {
                "kode_komponen": "053.03.A",
                "nama_komponen": "Pengadaan ATK, Kuesioner, & Perlengkapan Kit Survei",
                "kode_akun": "521211",
                "keg_kode": "SRV-SUS-202501",
                "pagu": 45000000
            },
            {
                "kode_komponen": "054.04.A",
                "nama_komponen": "Honor Pengolahan & Validasi Digital Wilkerstat IPDS",
                "kode_akun": "521213",
                "keg_kode": "SRV-TI-202501",
                "pagu": 85000000
            }
        ]

        created_komps = {}
        for komp_data in komponen_seed_list:
            ak = created_akuns.get(komp_data["kode_akun"])
            keg = created_kegiatans.get(komp_data["keg_kode"])
            if ak:
                kp = KomponenAnggaran.query.filter_by(kode_komponen=komp_data["kode_komponen"]).first()
                if not kp:
                    kp = KomponenAnggaran(
                        kode_komponen=komp_data["kode_komponen"],
                        nama_komponen=komp_data["nama_komponen"],
                        akun_id=ak.id,
                        kegiatan_id=keg.id if keg else None,
                        pagu_komponen=komp_data["pagu"]
                    )
                    db.session.add(kp)
                    db.session.flush()
                created_komps[komp_data["kode_komponen"]] = kp

        # Pengajuan Anggaran
        pengajuan_seed_list = [
            {
                "nomor": "AJU-20250210001",
                "judul": "Pembayaran Honor Petugas Lapangan Susenas Tahap I",
                "kode_komponen": "051.01.A",
                "kode_akun": "521213",
                "keg_kode": "SRV-SUS-202501",
                "volume": 45,
                "satuan": "Orang / Kegiatan",
                "tarif": 3200000,
                "total": 144000000,
                "is_akun_bps": True,
                "peran_tim": "Ketua Tim Lapangan",
                "honor_pengelola": 5000000,
                "status": "SELESAI",
                "tgl": date(2025, 2, 10),
                "ket": "Pengajuan honor PPL Susenas wilayah Banyuwangi Selatan sesuai dokumen BAST.",
                "sp2d_nomor": "SP2D-429215-20250214-0012",
                "sp2d_tgl": date(2025, 2, 14)
            },
            {
                "nomor": "AJU-20250215002",
                "judul": "Biaya Supervisi Perjalanan Dinas Monitoring KSA Padi Subround I",
                "kode_komponen": "052.02.A",
                "kode_akun": "524111",
                "keg_kode": "SRV-KSA-202501",
                "volume": 15,
                "satuan": "Hari / Petugas",
                "tarif": 450000,
                "total": 6750000,
                "is_akun_bps": False,
                "peran_tim": None,
                "honor_pengelola": 0,
                "status": "SELESAI",
                "tgl": date(2025, 2, 15),
                "ket": "Perjadin pengawasan amatan fase panen padi di wilayah Genteng dan Singojuruh.",
                "sp2d_nomor": "SP2D-429215-20250218-0019",
                "sp2d_tgl": date(2025, 2, 18)
            },
            {
                "nomor": "AJU-20250218003",
                "judul": "Pengadaan ATK, Kuesioner, & Buku Pedoman Petugas Survei",
                "kode_komponen": "053.03.A",
                "kode_akun": "521211",
                "keg_kode": "SRV-SUS-202501",
                "volume": 60,
                "satuan": "Paket Kit",
                "tarif": 250000,
                "total": 15000000,
                "is_akun_bps": False,
                "peran_tim": None,
                "honor_pengelola": 0,
                "status": "DISETUJUI",
                "tgl": date(2025, 2, 18),
                "ket": "Belanja bahan dan perlengkapan kit pelatihan petugas di Hotel eL Royale Banyuwangi.",
                "sp2d_nomor": None,
                "sp2d_tgl": None
            },
            {
                "nomor": "AJU-20250222004",
                "judul": "Honor Pengolahan Digital & Validasi Wilkerstat IPDS",
                "kode_komponen": "054.04.A",
                "kode_akun": "521213",
                "keg_kode": "SRV-TI-202501",
                "volume": 10,
                "satuan": "Orang / Paket",
                "tarif": 1800000,
                "total": 18000000,
                "is_akun_bps": True,
                "peran_tim": "Koordinator Pengolahan",
                "honor_pengelola": 2000000,
                "status": "MENUNGGU",
                "tgl": date(2025, 2, 22),
                "ket": "Pengajuan honor entri data dan validasi citra spasial desa/kelurahan.",
                "sp2d_nomor": None,
                "sp2d_tgl": None
            }
        ]

        ketua_peg = created_pegs.get("199408202016022001") or created_pegs.get("198501012010011001")

        for aju_data in pengajuan_seed_list:
            kp = created_komps.get(aju_data["kode_komponen"])
            ak = created_akuns.get(aju_data["kode_akun"])
            keg = created_kegiatans.get(aju_data["keg_kode"])
            if kp and ak:
                p_anggaran = PengajuanAnggaran.query.filter_by(nomor_pengajuan=aju_data["nomor"]).first()
                if not p_anggaran:
                    p_anggaran = PengajuanAnggaran(
                        nomor_pengajuan=aju_data["nomor"],
                        judul_pengajuan=aju_data["judul"],
                        kegiatan_id=keg.id if keg else None,
                        akun_id=ak.id,
                        komponen_id=kp.id,
                        volume_kegiatan=aju_data["volume"],
                        satuan_volume=aju_data["satuan"],
                        tarif_satuan=aju_data["tarif"],
                        is_akun_bps=aju_data["is_akun_bps"],
                        ketua_tim_id=ketua_peg.id if (aju_data["is_akun_bps"] and ketua_peg) else None,
                        peran_tim=aju_data["peran_tim"],
                        honor_pengelola=aju_data["honor_pengelola"],
                        jumlah_diajukan=aju_data["total"],
                        pengaju_id=admin_user.id if admin_user else 1,
                        status=aju_data["status"],
                        tanggal_pengajuan=aju_data["tgl"],
                        keterangan=aju_data["ket"]
                    )
                    db.session.add(p_anggaran)
                    db.session.flush()

                # Tambahkan persetujuan jika DISETUJUI atau SELESAI
                if aju_data["status"] in ("DISETUJUI", "SELESAI"):
                    pers = PersetujuanAnggaran.query.filter_by(pengajuan_id=p_anggaran.id).first()
                    if not pers:
                        pers = PersetujuanAnggaran(
                            pengajuan_id=p_anggaran.id,
                            approver_id=ppk_user.id if ppk_user else (admin_user.id if admin_user else 1),
                            status_keputusan="DISETUJUI",
                            jumlah_disetujui=p_anggaran.jumlah_diajukan,
                            catatan_persetujuan="Dokumen pertanggungjawaban lengkap, sesuai SBML dan alokasi Pagu DIPA Satker 429215.",
                            tanggal_keputusan=datetime.combine(aju_data["tgl"] + timedelta(days=2), datetime.min.time())
                        )
                        db.session.add(pers)

                # Tambahkan realisasi SP2D jika SELESAI
                if aju_data["status"] == "SELESAI" and aju_data["sp2d_nomor"]:
                    real = RealisasiAnggaran.query.filter_by(pengajuan_id=p_anggaran.id).first()
                    if not real:
                        real = RealisasiAnggaran(
                            pengajuan_id=p_anggaran.id,
                            nomor_sp2d=aju_data["sp2d_nomor"],
                            jumlah_realisasi=p_anggaran.jumlah_diajukan,
                            tanggal_realisasi=aju_data["sp2d_tgl"],
                            keterangan=f"Telah diterbitkan SP2D oleh KPPN Banyuwangi nomor {aju_data['sp2d_nomor']}.",
                            dicatat_oleh_id=admin_user.id if admin_user else 1
                        )
                        db.session.add(real)

        db.session.commit()
        print("Data demonstrasi 4 modul terpadu berhasil diisi secara lengkap!")

if __name__ == '__main__':
    run_seed()
