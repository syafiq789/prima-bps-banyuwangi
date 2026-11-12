"""
SUITE PENGUJIAN BLACK BOX TESTING & INTEGRASI SISTEM INFORMASI BPS
Sistem PRIMA & SIMPATIK BPS Kabupaten Banyuwangi

Metode Pengujian: Black Box Testing
Fokus Uji:
1. Autentikasi Pengguna & Role-Based Access Control (RBAC)
2. Fungsionalitas Modul PRIMA (SAKIP / AKIP)
3. Fungsionalitas Modul MONITORING MITRA
4. Fungsionalitas Modul KINERJA PEGAWAI
5. Fungsionalitas Modul TRACKING KEUANGAN
6. Integritas Basis Data & Relasi ORM (SQLAlchemy)
"""

import unittest
from datetime import datetime, date
from app import create_app
from app.models import (
    db, User, Mitra, PenugasanMitra, EvaluasiMitra,
    Pegawai, AktivitasPegawai, AkunAnggaran, KomponenAnggaran,
    PengajuanAnggaran, PersetujuanAnggaran, RealisasiAnggaran,
    Kegiatan, Document, DocumentCompleteness
)

class BlackBoxSystemTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app('testing')
        cls.app.config['TESTING'] = True
        cls.app.config['WTF_CSRF_ENABLED'] = False
        cls.client = cls.app.test_client()

    def setUp(self):
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    # =========================================================================
    # 1. PENGUJIAN AUTENTIKASI & RBAC (BLACK BOX)
    # =========================================================================
    def test_tc01_unauthenticated_access_redirect(self):
        """TC-01: Akses halaman privat tanpa login harus dialihkan (302) ke login."""
        protected_urls = [
            '/dashboard',
            '/mitra/dashboard',
            '/pegawai/dashboard',
            '/keuangan/dashboard'
        ]
        for url in protected_urls:
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 302, f"URL {url} harus memblokir akses tanpa login")
            self.assertIn('/auth/login', resp.headers.get('Location', ''))

    def test_tc02_login_valid_admin(self):
        """TC-02: Login dengan kredensial valid harus berhasil masuk."""
        resp = self.client.post('/auth/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'PRIMA', resp.data)

    def test_tc03_login_invalid_credentials(self):
        """TC-03: Login dengan password salah harus ditolak."""
        self.client.get('/auth/logout') # pastikan sesi logout
        resp = self.client.post('/auth/login', data={
            'email': 'admin',
            'password': 'passwordsalah'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Email / Username atau password yang Anda masukkan salah', resp.data)

    # =========================================================================
    # 2. PENGUJIAN MODUL PRIMA (SAKIP / AKIP)
    # =========================================================================
    def test_tc04_prima_dashboard_and_completeness(self):
        """TC-04: Dashboard PRIMA dan Checklist Kelengkapan Dokumen SAKIP."""
        with self.client.session_transaction() as sess:
            user = User.query.filter_by(role='admin').first()
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True

        # Akses Dashboard
        resp_dash = self.client.get('/dashboard')
        self.assertEqual(resp_dash.status_code, 200)

        # Akses Kelengkapan SAKIP
        resp_comp = self.client.get('/completeness/checklist')
        self.assertEqual(resp_comp.status_code, 200)
        self.assertIn(b'Kelengkapan', resp_comp.data)

    # =========================================================================
    # 3. PENGUJIAN MODUL MONITORING MITRA
    # =========================================================================
    def test_tc05_mitra_crud_and_assignment(self):
        """TC-05: Tambah Mitra, Buat Penugasan, dan Perbarui Progres Dokumen."""
        with self.client.session_transaction() as sess:
            user = User.query.filter_by(role='admin').first()
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True

        # Tambah Mitra Baru
        unique_sobat = f"BB_{int(datetime.utcnow().timestamp())}"
        resp_add = self.client.post('/mitra/database/create', data={
            'id_sobat': unique_sobat,
            'nama_lengkap': 'Mitra Uji Blackbox',
            'kecamatan': 'Banyuwangi',
            'no_hp': '081999888777',
            'email': 'mitra.uji@bps.go.id',
            'keahlian': 'Pendataan Lapangan (CAPI)'
        }, follow_redirects=True)
        self.assertEqual(resp_add.status_code, 200)

        created_mitra = Mitra.query.filter_by(id_sobat=unique_sobat).first()
        self.assertIsNotNone(created_mitra)

        # Buat Penugasan
        kegiatan = Kegiatan.query.first()
        resp_assign = self.client.post('/mitra/penugasan/create', data={
            'mitra_id': created_mitra.id,
            'kegiatan_id': kegiatan.id,
            'peran': 'PPL',
            'target_dokumen': 30,
            'honor_total': 3000000
        }, follow_redirects=True)
        self.assertEqual(resp_assign.status_code, 200)

        penugasan = PenugasanMitra.query.filter_by(mitra_id=created_mitra.id).first()
        self.assertIsNotNone(penugasan)

        # Update Progres Dokumen Lapangan
        resp_prog = self.client.post(f'/mitra/penugasan/{penugasan.id}/update-progress', data={
            'realisasi_dokumen': 30
        }, follow_redirects=True)
        self.assertEqual(resp_prog.status_code, 200)

        # Verifikasi status otomatis SELESAI jika mencapai target
        penugasan_updated = PenugasanMitra.query.get(penugasan.id)
        self.assertEqual(penugasan_updated.status, 'SELESAI')
        self.assertEqual(penugasan_updated.progres_persen, 100)

    # =========================================================================
    # 4. PENGUJIAN MODUL KINERJA PEGAWAI
    # =========================================================================
    def test_tc06_pegawai_activity_and_monitoring(self):
        """TC-06: Pencatatan Aktivitas Pegawai dan Pembaruan Progres Kerja."""
        with self.client.session_transaction() as sess:
            user = User.query.filter_by(role='admin').first()
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True

        pegawai = Pegawai.query.first()
        self.assertIsNotNone(pegawai)

        # Catat Aktivitas Baru
        resp_act = self.client.post('/pegawai/aktivitas/create', data={
            'pegawai_id': pegawai.id,
            'judul_aktivitas': 'Uji Validasi Data Sensus BPS',
            'deskripsi': 'Pemeriksaan konsistensi dokumen',
            'tanggal_mulai': '2025-03-01',
            'tanggal_selesai': '2025-03-10',
            'persentase_selesai': 40
        }, follow_redirects=True)
        self.assertEqual(resp_act.status_code, 200)

        act = AktivitasPegawai.query.filter_by(judul_aktivitas='Uji Validasi Data Sensus BPS').first()
        self.assertIsNotNone(act)
        self.assertEqual(act.status, 'PROSES')

        # Update Capaian Progres Menjadi 100%
        resp_up = self.client.post(f'/pegawai/aktivitas/{act.id}/update-progress', data={
            'persentase_selesai': 100
        }, follow_redirects=True)
        self.assertEqual(resp_up.status_code, 200)

        act_updated = AktivitasPegawai.query.get(act.id)
        self.assertEqual(act_updated.status, 'SELESAI')

    # =========================================================================
    # 5. PENGUJIAN MODUL TRACKING KEUANGAN
    # =========================================================================
    def test_tc07_keuangan_pengajuan_dan_persetujuan_ppk(self):
        """TC-07: Alur Usulan Pengajuan Anggaran, Persetujuan PPK, dan Realisasi SP2D."""
        with self.client.session_transaction() as sess:
            user = User.query.filter_by(role='admin').first()
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True

        akun = AkunAnggaran.query.first()
        komponen = KomponenAnggaran.query.first()
        kegiatan = Kegiatan.query.first()

        # 1. Ajukan Anggaran
        resp_aju = self.client.post('/keuangan/pengajuan/create', data={
            'judul_pengajuan': 'Pengajuan Biaya Operasional Pengujian Blackbox',
            'akun_id': akun.id,
            'komponen_id': komponen.id,
            'kegiatan_id': kegiatan.id,
            'jumlah_diajukan': 5000000,
            'keterangan': 'Dokumen lampiran lengkap'
        }, follow_redirects=True)
        self.assertEqual(resp_aju.status_code, 200)

        pengajuan = PengajuanAnggaran.query.filter_by(judul_pengajuan='Pengajuan Biaya Operasional Pengujian Blackbox').first()
        self.assertIsNotNone(pengajuan)
        self.assertEqual(pengajuan.status, 'MENUNGGU')

        # 2. Persetujuan oleh PPK (DISETUJUI)
        resp_acc = self.client.post('/keuangan/persetujuan/action', data={
            'pengajuan_id': pengajuan.id,
            'status': 'DISETUJUI',
            'catatan': 'Disetujui untuk diproses SP2D'
        }, follow_redirects=True)
        self.assertEqual(resp_acc.status_code, 200)

        pengajuan_acc = PengajuanAnggaran.query.get(pengajuan.id)
        self.assertEqual(pengajuan_acc.status, 'DISETUJUI')

        # 3. Pencatatan Realisasi SP2D
        sp2d_nomor = f"SP2D-UJI-{int(datetime.utcnow().timestamp())}"
        resp_real = self.client.post('/keuangan/realisasi/create', data={
            'pengajuan_id': pengajuan.id,
            'nomor_spm_sp2d': sp2d_nomor,
            'jumlah_realisasi': 5000000,
            'keterangan': 'Dana ditransfer via KPPN'
        }, follow_redirects=True)
        self.assertEqual(resp_real.status_code, 200)

        realisasi = RealisasiAnggaran.query.filter_by(nomor_sp2d=sp2d_nomor).first()
        self.assertIsNotNone(realisasi)
        self.assertEqual(realisasi.jumlah_realisasi, 5000000)

    # =========================================================================
    # 6. PENGUJIAN INTEGRITAS SELURUH ENDPOINT DASHBOARD & REKAP (HTTP 200)
    # =========================================================================
    def test_tc08_all_navigation_routes_200(self):
        """TC-08: Seluruh rute navigasi modul SIMPATIK dan PRIMA harus mengembalikan 200."""
        with self.client.session_transaction() as sess:
            user = User.query.filter_by(role='admin').first()
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True

        endpoints = [
            '/',
            '/dashboard',
            '/mitra/dashboard',
            '/mitra/database',
            '/mitra/penugasan',
            '/mitra/monitoring',
            '/mitra/evaluasi',
            '/mitra/rekapitulasi',
            '/mitra/template',
            '/pegawai/dashboard',
            '/pegawai/database',
            '/pegawai/aktivitas',
            '/pegawai/monitoring',
            '/pegawai/rekapitulasi',
            '/keuangan/dashboard',
            '/keuangan/akun',
            '/keuangan/komponen',
            '/keuangan/pengajuan',
            '/keuangan/persetujuan',
            '/keuangan/realisasi',
            '/keuangan/rekapitulasi',
        ]
        for ep in endpoints:
            res = self.client.get(ep, follow_redirects=True)
            self.assertEqual(res.status_code, 200, f"Endpoint {ep} gagal mengembalikan HTTP 200")

if __name__ == '__main__':
    unittest.main()
