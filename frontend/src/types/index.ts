export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: string;
  nip: string;
}

export interface AuthMeResponse {
  authenticated: boolean;
  user: User | null;
  is_ephemeral_db: boolean;
  counts?: {
    mitra: number;
    kegiatan: number;
    penugasan: number;
    evaluasi: number;
  };
}

export interface MitraItem {
  id: number;
  id_sobat: string;
  nama: string;
  email: string;
  alamat: string;
  nomor_hp: string;
  jenis_kelamin: string;
  desa: string;
  kecamatan: string;
  status_aktif: boolean;
}

export interface KegiatanItem {
  id: number;
  kode_kegiatan: string;
  nama_kegiatan: string;
  tim_kerja: string;
  tahun: number;
  bulan: string;
  tanggal_mulai: string;
  tanggal_selesai: string;
  status: string;
  total_mitra: number;
  total_dokumen_target: number;
  total_dokumen_realisasi: number;
  total_honor_mitra: number;
}

export interface PenugasanItem {
  id: number;
  mitra_id: number;
  mitra_nama: string;
  mitra_id_sobat: string;
  mitra_kecamatan: string;
  kegiatan_id: number;
  kegiatan_nama: string;
  kegiatan_tim: string;
  kegiatan_bulan: string;
  kegiatan_tahun: number;
  peran: string;
  target_dokumen: number;
  realisasi_dokumen: number;
  honor_total: number;
  status: string;
  sudah_dinilai: boolean;
}

export interface EvaluasiItem {
  id: number;
  mitra_nama: string;
  mitra_id_sobat: string;
  mitra_kecamatan: string;
  kegiatan_nama: string;
  kegiatan_tim: string;
  kegiatan_tahun: number;
  nilai_kualitas: number;
  nilai_ketepatan: number;
  nilai_kerjasama: number;
  rata_rata: number;
  catatan: string;
}

export interface RekapMitraRow {
  mitra: MitraItem;
  total_tugas: number;
  tugas_selesai: number;
  tugas_berjalan: number;
  tim_list: string[];
  kegiatan_list: string[];
  jumlah_eval: number;
  avg_score: number;
  predikat: string;
  total_honor: number;
}

export interface RekapKecamatanRow {
  kecamatan: string;
  total_mitra: number;
  total_tugas: number;
  total_honor: number;
}

export interface RekapTimRow {
  nama: string;
  desc: string;
  total_kegiatan: number;
  total_tugas: number;
  total_honor: number;
}
