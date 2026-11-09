import os
import logging
from flask import Flask, render_template, request
from flask_login import LoginManager
from sqlalchemy import create_engine, text
from config import config, Config
from app.models import db, User, Category, ImportantLink, Document, DocumentCompleteness, Activity

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Silakan login terlebih dahulu untuk mengakses halaman ini.'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def test_database_connection(uri):
    """Test if database URI is reachable."""
    try:
        engine = create_engine(uri, connect_args={"connect_timeout": 3} if "mysql" in uri else {})
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.warning(f"Database connection test failed for {uri}: {e}")
        return False

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')

    app = Flask(__name__)
    app.config.from_object(config.get(config_name, config['default']))

    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Database connection with graceful SQLite fallback for seamless local trial
    target_uri = app.config['SQLALCHEMY_DATABASE_URI']
    if 'mysql' in target_uri:
        logger.info(f"Checking MySQL connection: {target_uri}")
        if not test_database_connection(target_uri):
            # Check if MySQL database exists or create it, otherwise fallback
            try:
                # Try connecting without db name to create database if missing
                db_host = app.config.get('DB_HOST', 'localhost')
                db_port = app.config.get('DB_PORT', '3306')
                db_user = app.config.get('DB_USER', 'root')
                db_pass = app.config.get('DB_PASSWORD', '')
                db_name = app.config.get('DB_NAME', 'prima_akip_banyuwangi')
                root_uri = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/?charset=utf8mb4"
                
                engine = create_engine(root_uri, connect_args={"connect_timeout": 3})
                with engine.connect() as conn:
                    conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
                    conn.commit()
                logger.info(f"Database '{db_name}' checked/created successfully.")
            except Exception as ex:
                logger.warning(f"Could not connect to MySQL server ({ex}). Using local SQLite fallback for seamless execution.")
                app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLITE_URI']

    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.documents import documents_bp
    from app.routes.categories import categories_bp
    from app.routes.users import users_bp
    from app.routes.settings import settings_bp
    from app.routes.important_links import important_links_bp
    from app.routes.completeness import completeness_bp
    from app.routes.info import info_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(documents_bp, url_prefix='/documents')
    app.register_blueprint(categories_bp, url_prefix='/categories')
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(settings_bp, url_prefix='/settings')
    app.register_blueprint(important_links_bp, url_prefix='/important-links')
    app.register_blueprint(completeness_bp, url_prefix='/completeness')
    app.register_blueprint(info_bp, url_prefix='/info')

    # Global Context Processor for dynamic sidebar navigation & system metadata
    @app.context_processor
    def inject_global_data():
        try:
            # Group categories by group
            categories_by_group = {
                'perencanaan': Category.query.filter_by(group='perencanaan').all(),
                'pengukuran': Category.query.filter_by(group='pengukuran').all(),
                'pelaporan': Category.query.filter_by(group='pelaporan').all(),
            }
            important_links_list = ImportantLink.query.filter_by(is_active=True).all()
            pending_docs_count = Document.query.filter_by(status='belum_lengkap').count()
            total_docs_count = Document.query.count()
        except Exception:
            categories_by_group = {'perencanaan': [], 'pengukuran': [], 'pelaporan': []}
            important_links_list = []
            pending_docs_count = 0
            total_docs_count = 0

        return dict(
            categories_nav=categories_by_group,
            important_links_nav=important_links_list,
            pending_docs_count=pending_docs_count,
            total_docs_count=total_docs_count,
            app_name="PRIMA",
            app_fullname="Pusat Arsip dan Manajemen AKIP Banyuwangi",
            app_tagline="Arsip Tertata, Akuntabilitas Terjaga, Kinerja Prima.",
            current_path=request.path
        )

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    # Initialize tables and seed initial data
    with app.app_context():
        db.create_all()
        # Auto-migrate drive_url columns if table already existed without them
        try:
            with db.engine.connect() as conn:
                try:
                    conn.execute(text("SELECT drive_url FROM categories LIMIT 1"))
                except Exception:
                    conn.execute(text("ALTER TABLE categories ADD COLUMN drive_url VARCHAR(500)"))
                    conn.commit()
                try:
                    conn.execute(text("SELECT drive_url FROM documents LIMIT 1"))
                except Exception:
                    conn.execute(text("ALTER TABLE documents ADD COLUMN drive_url VARCHAR(500)"))
                    conn.commit()
        except Exception as e:
            logger.info(f"Database schema auto-check notice: {e}")
        seed_initial_data()

    return app

def seed_initial_data():
    """Seed initial categories, important links, default admin, and sample data if database is empty."""
    try:
        # 1. Default Users per Role (RBAC)
        rbac_seed_users = [
            {
                'username': 'admin',
                'full_name': 'Administrator PRIMA BPS',
                'nip': '198501012010011001',
                'role': 'admin',
                'password': 'admin123'
            },
            {
                'username': 'pegawai',
                'full_name': 'Pegawai BPS Banyuwangi',
                'nip': '199203152015021002',
                'role': 'pegawai',
                'password': 'pegawai123'
            },
            {
                'username': 'staf_umum',
                'full_name': 'Staf Subbagian Umum',
                'nip': '199008202014031003',
                'role': 'staf_umum',
                'password': 'umum123'
            },
            {
                'username': 'petugas_ipds',
                'full_name': 'Petugas Diseminasi IPDS',
                'nip': '199304122016021004',
                'role': 'petugas_ipds',
                'password': 'ipds123'
            },
            {
                'username': 'ppk',
                'full_name': 'Pejabat Pembuat Komitmen (PPK)',
                'nip': '198207102008011005',
                'role': 'ppk',
                'password': 'ppk123'
            },
            {
                'username': 'kpa',
                'full_name': 'Kuasa Pengguna Anggaran (KPA)',
                'nip': '197805152003121006',
                'role': 'kpa',
                'password': 'kpa123'
            }
        ]

        for udata in rbac_seed_users:
            u = User.query.filter_by(username=udata['username']).first()
            if not u:
                new_u = User(
                    username=udata['username'],
                    full_name=udata['full_name'],
                    nip=udata['nip'],
                    role=udata['role'],
                    is_active=True
                )
                new_u.set_password(udata['password'])
                db.session.add(new_u)
                logger.info(f"Created seed user [{udata['role']}]: {udata['username']} / {udata['password']}")
            elif u.role == 'user':
                # Update legacy 'user' role to 'pegawai'
                u.role = 'pegawai'

        # 2. Categories sesuai Struktur Prompt
        categories_data = [
            # PERENCANAAN
            {"name": "Dokumen Perencanaan", "slug": "dokumen-perencanaan", "group": "perencanaan", "icon": "file-text", "desc": "Dokumen rencana strategis dan perencanaan kinerja BPS Kabupaten Banyuwangi."},
            {"name": "Rencana Kerja", "slug": "rencana-kerja", "group": "perencanaan", "icon": "calendar", "desc": "Rencana kerja tahunan dan rencana operasional kegiatan."},
            {"name": "Perjanjian Kinerja", "slug": "perjanjian-kinerja", "group": "perencanaan", "icon": "award", "desc": "Penetapan dan perjanjian kinerja pimpinan dan pegawai."},
            {"name": "Rencana Aksi", "slug": "rencana-aksi", "group": "perencanaan", "icon": "trending-up", "desc": "Rencana aksi atas pencapaian target kinerja organisasi."},
            {"name": "Indikator Kinerja Utama", "slug": "indikator-kinerja-utama", "group": "perencanaan", "icon": "target", "desc": "Indikator Kinerja Utama (IKU) BPS Kabupaten Banyuwangi."},
            
            # PENGUKURAN
            {"name": "Pengukuran Kinerja", "slug": "pengukuran-kinerja", "group": "pengukuran", "icon": "gauge", "desc": "Metrik dan data pengukuran kinerja periodik."},
            {"name": "Capaian Kinerja", "slug": "capaian-kinerja", "group": "pengukuran", "icon": "check-circle", "desc": "Data dan analisis realisasi capaian kinerja instansi."},
            {"name": "Evaluasi Kinerja", "slug": "evaluasi-kinerja", "group": "pengukuran", "icon": "clipboard-check", "desc": "Hasil evaluasi dan review capaian target kinerja bulanan/triwulanan."},
            
            # PELAPORAN
            {"name": "Laporan Kinerja", "slug": "laporan-kinerja", "group": "pelaporan", "icon": "book-open", "desc": "Laporan Kinerja Instansi Pemerintah (LAKIP / LKjIP)."},
            {"name": "Laporan Evaluasi", "slug": "laporan-evaluasi", "group": "pelaporan", "icon": "file-check", "desc": "Laporan hasil evaluasi internal dan rekomendasi perbaikan."},
            {"name": "Dokumen Pendukung Pelaporan", "slug": "dokumen-pendukung-pelaporan", "group": "pelaporan", "icon": "paperclip", "desc": "Bukti dukung, notula, daftar hadir, dan lampiran pelaporan."},
            
            # ARSIP & KELENGKAPAN
            {"name": "Arsip Dokumen", "slug": "arsip-dokumen", "group": "kelengkapan", "icon": "archive", "desc": "Koleksi arsip dokumen akuntabilitas kinerja tahun-tahun sebelumnya."}
        ]

        for cat in categories_data:
            drive_folder_url = f"https://drive.google.com/drive/folders/bps-banyuwangi-{cat['slug']}"
            existing = Category.query.filter_by(slug=cat['slug']).first()
            if not existing:
                new_cat = Category(
                    name=cat['name'],
                    slug=cat['slug'],
                    group=cat['group'],
                    icon=cat['icon'],
                    description=cat['desc'],
                    drive_url=drive_folder_url
                )
                db.session.add(new_cat)
            elif not existing.drive_url:
                existing.drive_url = drive_folder_url

        # 3. Important Links sesuai spesifikasi prompt
        important_links_data = [
            {
                "code": "simonik",
                "title": "SIMONIK",
                "description": "Sistem Informasi Monitoring Kinerja BPS untuk pemantauan dan evaluasi kegiatan berkala.",
                "url": "https://simonik.bps.go.id",
                "icon": "activity",
                "badge_text": "Monitoring Internal"
            },
            {
                "code": "sinergi",
                "title": "SINERGI",
                "description": "Aplikasi Sistem Informasi Penilaian Kinerja Terintegrasi BPS.",
                "url": "https://sinergi.bps.go.id",
                "icon": "share-2",
                "badge_text": "Sistem Kinerja"
            },
            {
                "code": "fra",
                "title": "FRA",
                "description": "Formulir Rekomendasi Akuntabilitas Kinerja Instansi Pemerintah BPS Kabupaten Banyuwangi.",
                "url": "https://fra.bps.go.id",
                "icon": "check-square",
                "badge_text": "Rekomendasi"
            },
            {
                "code": "link-akip-jatim",
                "title": "LINK AKIP JATIM",
                "description": "Portal Integrasi AKIP BPS Provinsi Jawa Timur untuk sinkronisasi dokumen kabupaten/kota.",
                "url": "https://jatim.bps.go.id/akip",
                "icon": "globe",
                "badge_text": "Provinsi Jawa Timur"
            },
            {
                "code": "proksi",
                "title": "PROKSI",
                "description": "Program Monitoring Kinerja Strategis dan Indikator Kunci BPS.",
                "url": "https://proksi.bps.go.id",
                "icon": "pie-chart",
                "badge_text": "Kinerja Strategis"
            },
            {
                "code": "permindok-2025",
                "title": "PERMINDOK 2025",
                "description": "Permintaan dan Penataan Dokumen Administrasi AKIP BPS Banyuwangi Tahun 2025.",
                "url": "https://drive.google.com/drive/folders/permindok-2025-banyuwangi",
                "icon": "folder-archive",
                "badge_text": "Tahun 2025"
            },
            {
                "code": "permindok-2026",
                "title": "PERMINDOK 2026",
                "description": "Permintaan dan Penataan Dokumen Administrasi AKIP BPS Banyuwangi Tahun 2026.",
                "url": "https://drive.google.com/drive/folders/permindok-2026-banyuwangi",
                "icon": "folder-plus",
                "badge_text": "Tahun 2026"
            },
            {
                "code": "janjiku",
                "title": "JANJIKU",
                "description": "Janji Kinerja dan Pakta Integritas seluruh jajaran pegawai BPS Kabupaten Banyuwangi.",
                "url": "https://janjiku.bps.go.id",
                "icon": "shield-check",
                "badge_text": "Integritas & Janji"
            }
        ]

        for link in important_links_data:
            existing = ImportantLink.query.filter_by(code=link['code']).first()
            if not existing:
                new_link = ImportantLink(
                    code=link['code'],
                    title=link['title'],
                    description=link['description'],
                    url=link['url'],
                    icon=link['icon'],
                    badge_text=link['badge_text'],
                    is_active=True
                )
                db.session.add(new_link)

        db.session.commit()

        # Catatan: Tabel documents dibiarkan bersih (kosong) agar pengguna dapat mengunggah dokumen sendiri secara langsung.

        # 4. Checklist Kelengkapan Dokumen Standard AKIP (jika masih kosong)
        if DocumentCompleteness.query.count() == 0:
            cat_ren = Category.query.filter_by(slug='dokumen-perencanaan').first()
            cat_pk = Category.query.filter_by(slug='perjanjian-kinerja').first()
            cat_iku = Category.query.filter_by(slug='indikator-kinerja-utama').first()
            cat_cap = Category.query.filter_by(slug='capaian-kinerja').first()
            cat_lakip = Category.query.filter_by(slug='laporan-kinerja').first()

            checklist_data = [
                {"category_id": cat_ren.id if cat_ren else 1, "year": 2025, "item_name": "Dokumen Renstra BPS 2025-2029", "is_required": True, "is_fulfilled": False, "notes": "Perlu diunggah"},
                {"category_id": cat_ren.id if cat_ren else 1, "year": 2025, "item_name": "Rencana Kerja Tahunan (RKT) 2025", "is_required": True, "is_fulfilled": False, "notes": "Perlu diunggah"},
                {"category_id": cat_pk.id if cat_pk else 1, "year": 2025, "item_name": "Perjanjian Kinerja Eselon III", "is_required": True, "is_fulfilled": False, "notes": "Perlu diunggah"},
                {"category_id": cat_pk.id if cat_pk else 1, "year": 2025, "item_name": "Perjanjian Kinerja Seluruh Ketua Tim", "is_required": True, "is_fulfilled": False, "notes": "Perlu diunggah"},
                {"category_id": cat_iku.id if cat_iku else 1, "year": 2025, "item_name": "Matriks Definisi Operasional IKU 2025", "is_required": True, "is_fulfilled": False, "notes": "Perlu diunggah"},
                {"category_id": cat_cap.id if cat_cap else 1, "year": 2025, "item_name": "Laporan Capaian Kinerja Triwulan I 2025", "is_required": True, "is_fulfilled": False, "notes": "Perlu diunggah"},
                {"category_id": cat_cap.id if cat_cap else 1, "year": 2025, "item_name": "Laporan Capaian Kinerja Triwulan II 2025", "is_required": True, "is_fulfilled": False, "notes": "Perlu diunggah"},
                {"category_id": cat_cap.id if cat_cap else 1, "year": 2025, "item_name": "Laporan Capaian Kinerja Triwulan III 2025", "is_required": True, "is_fulfilled": False, "notes": "Perlu diunggah"},
                {"category_id": cat_lakip.id if cat_lakip else 1, "year": 2025, "item_name": "Laporan Kinerja (LAKIP) 2025", "is_required": True, "is_fulfilled": False, "notes": "Perlu diunggah"}
            ]

            for item in checklist_data:
                chk = DocumentCompleteness(
                    category_id=item['category_id'],
                    year=item['year'],
                    item_name=item['item_name'],
                    is_required=item['is_required'],
                    is_fulfilled=item['is_fulfilled'],
                    notes=item['notes']
                )
                db.session.add(chk)
            db.session.commit()

            # Activity log awal
            admin_account = User.query.filter_by(username='admin').first()
            admin_id = admin_account.id if admin_account else 1
            act1 = Activity(
                user_id=admin_id,
                action='INITIALIZE_SYSTEM',
                description='Sistem PRIMA BPS Kabupaten Banyuwangi diinisialisasi secara otomatis.',
                ip_address='127.0.0.1'
            )
            db.session.add(act1)
            db.session.commit()

        logger.info("Database initialization and initial data seeding completed.")
    except Exception as e:
        logger.error(f"Error during seeding initial data: {e}")
        db.session.rollback()

