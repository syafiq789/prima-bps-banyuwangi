from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    documents = db.relationship('Document', backref='category', lazy='dynamic', cascade='all, delete-orphan')
    checklist_items = db.relationship('DocumentCompleteness', backref='category', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Category {self.name}>'


class Document(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='CASCADE'), nullable=False)
    year = db.Column(db.Integer, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, default=0) # in bytes
    file_type = db.Column(db.String(20), nullable=False) # pdf, docx, xlsx, pptx
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.String(20), default='lengkap', nullable=False) # 'lengkap', 'belum_lengkap'
    notes = db.Column(db.Text, nullable=True)
    download_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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

