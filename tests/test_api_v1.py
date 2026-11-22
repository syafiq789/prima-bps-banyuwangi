import io
import unittest
from app import create_app
from app.models import db


class ApiV1TestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def _login(self):
        res = self.client.post('/api/v1/auth/login', json={
            'username': 'tfdewanto@bps.go.id',
            'password': '12345678'
        })
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.get_json()['ok'])

    def test_full_api_v1_flow(self):
        # 1. Auth me (unauthenticated)
        res = self.client.get('/api/v1/auth/me')
        self.assertEqual(res.status_code, 200)
        self.assertFalse(res.get_json()['authenticated'])

        # 2. Login + Auth me
        self._login()
        res = self.client.get('/api/v1/auth/me')
        self.assertTrue(res.get_json()['authenticated'])

        # 3. Hub
        res = self.client.get('/api/v1/hub')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.get_json()['ok'])

        # 4. Upload Mitra CSV (8 official columns)
        mitra_csv = (
            "id_sobat,nama,email,alamat,nomor_hp,jenis_kelamin,desa,kecamatan\n"
            "35102025901,Rina Kartika,rina@mitrabps.id,Jl. Merdeka 1,081234560901,Perempuan,Rogojampi,Rogojampi\n"
        ).encode('utf-8')
        res = self.client.post(
            '/api/v1/mitra/upload-mitra',
            data={'file': (io.BytesIO(mitra_csv), 'mitra.csv')},
            content_type='multipart/form-data'
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()['added'], 1)

        # 5. Upload Kegiatan CSV (6 official columns)
        keg_csv = (
            "nama_kegiatan,tim_kerja,tahun,bulan,tanggal_mulai,tanggal_selesai\n"
            "Survei Harga Konsumen,Tim Distribusi,2025,Januari,2025-01-05,2025-01-31\n"
        ).encode('utf-8')
        res = self.client.post(
            '/api/v1/mitra/upload-kegiatan',
            data={'file': (io.BytesIO(keg_csv), 'kegiatan.csv')},
            content_type='multipart/form-data'
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()['added'], 1)

        # 6. Mitra list & kegiatan list
        mitra_list = self.client.get('/api/v1/mitra/list').get_json()['items']
        keg_list = self.client.get('/api/v1/mitra/kegiatan').get_json()['items']
        self.assertEqual(len(mitra_list), 1)
        self.assertEqual(len(keg_list), 1)

        # 7. Penugasan create + progress update
        res = self.client.post('/api/v1/mitra/penugasan/create', json={
            'mitra_id': mitra_list[0]['id'],
            'kegiatan_id': keg_list[0]['id'],
            'peran': 'PPL',
            'target_dokumen': 20,
            'honor_total': 2500000
        })
        self.assertEqual(res.status_code, 201)
        pen_id = res.get_json()['item']['id']

        res = self.client.post(f'/api/v1/mitra/penugasan/{pen_id}/progress', json={'realisasi_dokumen': 20})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()['item']['status'], 'SELESAI')

        # 8. Evaluasi create
        res = self.client.post('/api/v1/mitra/evaluasi/create', json={
            'penugasan_id': pen_id,
            'nilai_kualitas': 92,
            'nilai_ketepatan': 90,
            'nilai_kerjasama': 94,
            'catatan': 'Sangat baik'
        })
        self.assertEqual(res.status_code, 201)

        # 9. Dashboard, Rekapitulasi, Ephemeral Sync
        dash = self.client.get('/api/v1/mitra/dashboard').get_json()
        self.assertEqual(dash['kpi']['total_mitra'], 1)
        self.assertEqual(dash['kpi']['total_kegiatan'], 1)
        self.assertEqual(dash['kpi']['total_honor_all'], 2500000)

        rekap = self.client.get('/api/v1/mitra/rekapitulasi').get_json()
        self.assertEqual(len(rekap['rekap_mitra']), 1)
        self.assertEqual(rekap['rekap_mitra'][0]['predikat'], 'Sangat Baik (A)')

        snap = self.client.get('/api/v1/mitra/ephemeral-sync').get_json()
        self.assertTrue(snap['ok'])
        self.assertEqual(len(snap['mitra']), 1)
        self.assertEqual(len(snap['kegiatan']), 1)
        self.assertEqual(len(snap['penugasan']), 1)
        self.assertEqual(len(snap['evaluasi']), 1)

        # 10. Pegawai, Keuangan, AKIP overviews
        self.assertEqual(self.client.get('/api/v1/pegawai/overview').status_code, 200)
        self.assertEqual(self.client.get('/api/v1/keuangan/overview').status_code, 200)
        self.assertEqual(self.client.get('/api/v1/akip/overview').status_code, 200)


if __name__ == '__main__':
    unittest.main()
