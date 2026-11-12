from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    nip = db.Column(db.String(30), nullable=True)
    role = db.Column(db.String(30), default='pegawai', nullable=False) # 'admin', 'pegawai', 'staf_umum', 'petugas_ipds', 'ppk', 'kpa'
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Available Roles Definition
    ROLES = {
        'admin': 'Administrator',
        'pegawai': 'Pegawai',
        'staf_umum': 'Staf Subbagian Umum',
        'petugas_ipds': 'Petugas IPDS',
        'ppk': 'Pejabat Pembuat Komitmen (PPK)',
        'kpa': 'Kuasa Pengguna Anggaran (KPA)'
    }

    # Relationships
    documents = db.relationship('Document', backref='uploader', lazy='dynamic')
    activities = db.relationship('Activity', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_staf_umum(self):
        return self.role == 'staf_umum'

    @property
    def is_petugas_ipds(self):
        return self.role == 'petugas_ipds'

    @property
    def is_ppk(self):
        return self.role == 'ppk'

    @property
    def is_kpa(self):
        return self.role == 'kpa'

    @property
    def role_display_name(self):
        return self.ROLES.get(self.role, self.role.upper())

    @property
    def can_manage_documents(self):
        # Admin, Staf Umum, dan PPK memiliki hak upload dan kelola dokumen arsip
        return self.role in ('admin', 'staf_umum', 'ppk')

    def __repr__(self):
        return f'<User {self.username} - {self.role}>'


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    group = db.Column(db.String(50), nullable=False) # 'perencanaan', 'pengukuran', 'pelaporan', 'dokumen_penting', 'kelengkapan'
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(50), default='folder')
    drive_url = db.Column(db.String(500), nullable=True) # Link Folder Google Drive
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    documents = db.relationship('Document', backref='category', lazy='dynamic', cascade='all, delete-orphan')
    checklist_items = db.relationship('DocumentCompleteness', backref='category', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def gdrive_link(self):
        return self.drive_url or f"https://drive.google.com/drive/search?q={self.slug}"

    def __repr__(self):
        return f'<Category {self.name}>'


class Document(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='CASCADE'), nullable=False)
    year = db.Column(db.Integer, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    drive_url = db.Column(db.String(500), nullable=True) # Link Berkas / Folder Google Drive
    filename = db.Column(db.String(255), nullable=True)
    original_filename = db.Column(db.String(255), nullable=True)
    file_size = db.Column(db.Integer, default=0) # in bytes
    file_type = db.Column(db.String(50), default='gdrive', nullable=False) # gdrive, folder, pdf, docx, xlsx, pptx
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.String(20), default='lengkap', nullable=False) # 'lengkap', 'belum_lengkap'
    notes = db.Column(db.Text, nullable=True)
    download_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def is_gdrive(self):
        return bool(self.drive_url)

    @property
    def access_url(self):
        return self.drive_url or f"/documents/{self.id}/download"

    @property
    def formatted_size(self):
        size = self.file_size or 0
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.2f} MB"

    def __repr__(self):
        return f'<Document {self.title}>'


class DocumentCompleteness(db.Model):
    __tablename__ = 'document_completeness'

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='CASCADE'), nullable=False)
    year = db.Column(db.Integer, nullable=False, index=True)
    item_name = db.Column(db.String(255), nullable=False)
    is_required = db.Column(db.Boolean, default=True)
    is_fulfilled = db.Column(db.Boolean, default=False)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id', ondelete='SET NULL'), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Document relationship
    linked_document = db.relationship('Document', foreign_keys=[document_id], backref='completeness_links')

    def __repr__(self):
        return f'<DocumentCompleteness {self.item_name} - {self.is_fulfilled}>'


class ImportantLink(db.Model):
    __tablename__ = 'important_links'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True) # e.g. 'simonik', 'sinergi', 'fra', 'link-akip-jatim', 'proksi', 'permindok-2025', 'permindok-2026', 'janjiku'
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    url = db.Column(db.String(500), nullable=False)
    icon = db.Column(db.String(50), default='external-link')
    badge_text = db.Column(db.String(50), default='Aplikasi Eksternal')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<ImportantLink {self.title}>'


class Activity(db.Model):
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    ip_address = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f'<Activity {self.action} by {self.user_id}>'


# ==============================================================================
# MODUL BARU: MONITORING MITRA, KINERJA PEGAWAI, TRACKING KEUANGAN
# ==============================================================================

class Kegiatan(db.Model):
    """Tabel Kegiatan Terpadu untuk Modul Mitra, Pegawai, dan Keuangan."""
    __tablename__ = 'simpatik_kegiatan'

    id = db.Column(db.Integer, primary_key=True)
    kode_kegiatan = db.Column(db.String(40), unique=True, nullable=False)
    nama_kegiatan = db.Column(db.String(200), nullable=False)
    tahun = db.Column(db.Integer, default=2025)
    tanggal_mulai = db.Column(db.Date, nullable=False)
    tanggal_selesai = db.Column(db.Date, nullable=False)
    penanggung_jawab_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    status = db.Column(db.String(20), default='BERJALAN') # 'PERENCANAAN', 'BERJALAN', 'SELESAI'
    progres_persen = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    penugasan_mitra = db.relationship('PenugasanMitra', backref='kegiatan', lazy='dynamic', cascade='all, delete-orphan')


class TemplateKegiatan(db.Model):
    __tablename__ = 'simpatik_template_kegiatan'

    id = db.Column(db.Integer, primary_key=True)
    nama_template = db.Column(db.String(150), nullable=False)
    jenis_survei = db.Column(db.String(100), nullable=False)
    honor_standar = db.Column(db.BigInteger, default=0)
    deskripsi = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Mitra(db.Model):
    __tablename__ = 'simpatik_mitra'

    id = db.Column(db.Integer, primary_key=True)
    id_sobat = db.Column(db.String(30), unique=True, nullable=False)
    nama_lengkap = db.Column(db.String(150), nullable=False)
    kecamatan = db.Column(db.String(100), nullable=False)
    no_hp = db.Column(db.String(25), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    keahlian = db.Column(db.String(150), default='Pendataan Lapangan (CAPI)')
    status_aktif = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    penugasan = db.relationship('PenugasanMitra', backref='mitra', lazy='dynamic', cascade='all, delete-orphan')
    evaluasi_list = db.relationship('EvaluasiMitra', backref='mitra', lazy='dynamic', cascade='all, delete-orphan')


class PenugasanMitra(db.Model):
    __tablename__ = 'simpatik_penugasan_mitra'

    id = db.Column(db.Integer, primary_key=True)
    mitra_id = db.Column(db.Integer, db.ForeignKey('simpatik_mitra.id', ondelete='CASCADE'), nullable=False)
    kegiatan_id = db.Column(db.Integer, db.ForeignKey('simpatik_kegiatan.id', ondelete='CASCADE'), nullable=False)
    peran = db.Column(db.String(20), default='PPL') # 'PPL', 'PML', 'PENGOLAH'
    target_dokumen = db.Column(db.Integer, default=10)
    realisasi_dokumen = db.Column(db.Integer, default=0)
    honor_total = db.Column(db.BigInteger, default=0)
    status = db.Column(db.String(20), default='PROSES') # 'PROSES', 'SELESAI'
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    evaluasi = db.relationship('EvaluasiMitra', backref='penugasan', uselist=False, cascade='all, delete-orphan')

    @property
    def progres_persen(self):
        if not self.target_dokumen:
            return 0
        return min(100, round((self.realisasi_dokumen / self.target_dokumen) * 100))


class EvaluasiMitra(db.Model):
    __tablename__ = 'simpatik_evaluasi_mitra'

    id = db.Column(db.Integer, primary_key=True)
    penugasan_id = db.Column(db.Integer, db.ForeignKey('simpatik_penugasan_mitra.id', ondelete='CASCADE'), nullable=False, unique=True)
    mitra_id = db.Column(db.Integer, db.ForeignKey('simpatik_mitra.id', ondelete='CASCADE'), nullable=False)
    nilai_kualitas = db.Column(db.Integer, default=85)
    nilai_ketepatan = db.Column(db.Integer, default=85)
    nilai_kerjasama = db.Column(db.Integer, default=85)
    catatan = db.Column(db.Text, nullable=True)
    evaluator_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def rata_rata(self):
        return round((self.nilai_kualitas + self.nilai_ketepatan + self.nilai_kerjasama) / 3, 1)


class Pegawai(db.Model):
    __tablename__ = 'simpatik_pegawai'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    nip = db.Column(db.String(30), unique=True, nullable=False)
    nama_lengkap = db.Column(db.String(150), nullable=False)
    jabatan = db.Column(db.String(120), nullable=False)
    tim_kerja = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    status_aktif = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    aktivitas = db.relationship('AktivitasPegawai', backref='pegawai', lazy='dynamic', cascade='all, delete-orphan')


class AktivitasPegawai(db.Model):
    __tablename__ = 'simpatik_aktivitas_pegawai'

    id = db.Column(db.Integer, primary_key=True)
    pegawai_id = db.Column(db.Integer, db.ForeignKey('simpatik_pegawai.id', ondelete='CASCADE'), nullable=False)
    kegiatan_id = db.Column(db.Integer, db.ForeignKey('simpatik_kegiatan.id', ondelete='SET NULL'), nullable=True)
    judul_aktivitas = db.Column(db.String(200), nullable=False)
    deskripsi = db.Column(db.Text, nullable=True)
    tanggal_mulai = db.Column(db.Date, nullable=False)
    tanggal_selesai = db.Column(db.Date, nullable=False)
    persentase_selesai = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='PROSES') # 'PROSES', 'SELESAI'
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    kegiatan = db.relationship('Kegiatan', backref='aktivitas_pegawai')


class AkunAnggaran(db.Model):
    __tablename__ = 'simpatik_akun_anggaran'

    id = db.Column(db.Integer, primary_key=True)
    kode_akun = db.Column(db.String(20), unique=True, nullable=False)
    nama_akun = db.Column(db.String(180), nullable=False)
    kategori = db.Column(db.String(30), default='HONOR') # 'HONOR', 'PERJADIN', 'BAHAN', 'LAINNYA'
    pagu_awal = db.Column(db.BigInteger, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    komponen_list = db.relationship('KomponenAnggaran', backref='akun', lazy='dynamic', cascade='all, delete-orphan')
    pengajuan_list = db.relationship('PengajuanAnggaran', backref='akun', lazy='dynamic', cascade='all, delete-orphan')


class KomponenAnggaran(db.Model):
    __tablename__ = 'simpatik_komponen_anggaran'

    id = db.Column(db.Integer, primary_key=True)
    kode_komponen = db.Column(db.String(30), nullable=False)
    nama_komponen = db.Column(db.String(200), nullable=False)
    akun_id = db.Column(db.Integer, db.ForeignKey('simpatik_akun_anggaran.id', ondelete='CASCADE'), nullable=False)
    kegiatan_id = db.Column(db.Integer, db.ForeignKey('simpatik_kegiatan.id', ondelete='SET NULL'), nullable=True)
    pagu_komponen = db.Column(db.BigInteger, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    kegiatan = db.relationship('Kegiatan', backref='komponen_anggaran')


class PengajuanAnggaran(db.Model):
    __tablename__ = 'simpatik_pengajuan_anggaran'

    id = db.Column(db.Integer, primary_key=True)
    nomor_pengajuan = db.Column(db.String(40), unique=True, nullable=False)
    judul_pengajuan = db.Column(db.String(200), nullable=False)
    kegiatan_id = db.Column(db.Integer, db.ForeignKey('simpatik_kegiatan.id', ondelete='SET NULL'), nullable=True)
    akun_id = db.Column(db.Integer, db.ForeignKey('simpatik_akun_anggaran.id', ondelete='CASCADE'), nullable=False)
    komponen_id = db.Column(db.Integer, db.ForeignKey('simpatik_komponen_anggaran.id', ondelete='CASCADE'), nullable=False)
    jumlah_diajukan = db.Column(db.BigInteger, nullable=False)
    pengaju_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    status = db.Column(db.String(20), default='MENUNGGU') # 'MENUNGGU', 'DISETUJUI', 'DITOLAK', 'DIREVISI'
    tanggal_pengajuan = db.Column(db.Date, default=datetime.utcnow)
    keterangan = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    komponen = db.relationship('KomponenAnggaran', backref='pengajuan_list')
    kegiatan = db.relationship('Kegiatan', backref='pengajuan_anggaran')
    pengaju = db.relationship('User', foreign_keys=[pengaju_id])
    persetujuan = db.relationship('PersetujuanAnggaran', backref='pengajuan', uselist=False, cascade='all, delete-orphan')
    realisasi_list = db.relationship('RealisasiAnggaran', backref='pengajuan', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def realisasi(self):
        return self.realisasi_list.first()


class PersetujuanAnggaran(db.Model):
    __tablename__ = 'simpatik_persetujuan_anggaran'

    id = db.Column(db.Integer, primary_key=True)
    pengajuan_id = db.Column(db.Integer, db.ForeignKey('simpatik_pengajuan_anggaran.id', ondelete='CASCADE'), nullable=False, unique=True)
    approver_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    status_keputusan = db.Column(db.String(20), nullable=False) # 'DISETUJUI', 'DITOLAK', 'DIREVISI'
    jumlah_disetujui = db.Column(db.BigInteger, default=0)
    catatan_persetujuan = db.Column(db.Text, nullable=True)
    tanggal_keputusan = db.Column(db.DateTime, default=datetime.utcnow)

    approver = db.relationship('User', foreign_keys=[approver_id])

    @property
    def status(self):
        return self.status_keputusan

    @property
    def catatan(self):
        return self.catatan_persetujuan


class RealisasiAnggaran(db.Model):
    __tablename__ = 'simpatik_realisasi_anggaran'

    id = db.Column(db.Integer, primary_key=True)
    pengajuan_id = db.Column(db.Integer, db.ForeignKey('simpatik_pengajuan_anggaran.id', ondelete='CASCADE'), nullable=False)
    nomor_sp2d = db.Column(db.String(60), nullable=False)
    jumlah_realisasi = db.Column(db.BigInteger, nullable=False)
    tanggal_realisasi = db.Column(db.Date, default=datetime.utcnow)
    keterangan = db.Column(db.Text, nullable=True)
    dicatat_oleh_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def nomor_spm_sp2d(self):
        return self.nomor_sp2d


