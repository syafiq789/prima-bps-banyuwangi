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
                try:
                    conn.execute(text("SELECT email FROM users LIMIT 1"))
                except Exception:
                    conn.execute(text("ALTER TABLE users ADD COLUMN email VARCHAR(120)"))
                    conn.commit()
        except Exception as e:
            logger.info(f"Database schema auto-check notice: {e}")
        seed_initial_data()

    return app

def seed_initial_data():
    """Seed initial categories, important links, default admin, and sample data if database is empty."""
    try:
        # 1. Hapus akun-akun demo/seed lama agar sistem login murni memakai Akun Google masing-masing
        legacy_seed_usernames = ['admin', 'pegawai', 'staf_umum', 'petugas_ipds', 'ppk', 'kpa']
        User.query.filter(User.username.in_(legacy_seed_usernames)).delete(synchronize_session=False)
        db.session.commit()

        # 2. Categories Resmi Sesuai Dokumen PRIMA BPS Banyuwangi
        categories_data = [
            # PERENCANAAN
            {
                "name": "Rencana Awal Renstra", 
                "slug": "rencana-awal-renstra", 
                "group": "perencanaan", 
                "icon": "file-text", 
                "drive_url": "https://drive.google.com/drive/folders/13z-GsSIqqSXNa4QbdAj9ezuYQ-K0V89y?usp=sharing",
                "desc": "Dokumen rancangan awal Rencana Strategis (Renstra) BPS Kabupaten Banyuwangi."
            },
            {
                "name": "Renstra", 
                "slug": "renstra", 
                "group": "perencanaan", 
                "icon": "compass", 
                "drive_url": "https://drive.google.com/drive/folders/1tG_Z7uqrJQ0B8EJxbgsN-NgfgSocK1uJ?usp=sharing",
                "desc": "Dokumen Rencana Strategis (Renstra) resmi BPS Kabupaten Banyuwangi."
            },
            {
                "name": "Perjanjian Kinerja", 
                "slug": "perjanjian-kinerja", 
                "group": "perencanaan", 
                "icon": "award", 
                "drive_url": "https://drive.google.com/drive/folders/1sPNbUk3DsKIPL4XS6ZWagtCp7Oxyp7Sy?usp=sharing",
                "desc": "Penetapan dan komitmen Perjanjian Kinerja (PK) pimpinan dan jajaran pegawai."
            },
            
            # PENGUKURAN (Monitoring Capaian Kinerja)
            {
                "name": "KKPK", 
                "slug": "kkpk", 
                "group": "pengukuran", 
                "icon": "gauge", 
                "drive_url": "https://drive.google.com/drive/folders/1X3YlxX-Y9MHur9xvSxwktSHXeYeD7qY6?usp=sharing",
                "desc": "Kertas Kerja Pengukuran Kinerja (KKPK) BPS Kabupaten Banyuwangi."
            },
            {
                "name": "DAHA", 
                "slug": "daha", 
                "group": "pengukuran", 
                "icon": "activity", 
                "drive_url": "https://drive.google.com/drive/folders/1ZXCDu6HCLKHx-PwuGlhzsDQj1ck2UQpE?usp=sharing",
                "desc": "Data dan Arsip Hasil Analisis (DAHA) kinerja operasional statistik."
            },
            {
                "name": "Proksi", 
                "slug": "proksi", 
                "group": "pengukuran", 
                "icon": "shield-check", 
                "drive_url": "https://drive.google.com/drive/folders/1dKKWp8QvaBSOwQitaADRup27ktVdu485?usp=sharing",
                "desc": "Pengawasan dan Pengendalian Kinerja Statistik Internal (Proksi)."
            },
            {
                "name": "Monitoring Capaian Renstra", 
                "slug": "monitoring-capaian-renstra", 
                "group": "pengukuran", 
                "icon": "trending-up", 
                "drive_url": "https://drive.google.com/drive/folders/1BYW2BPyeDHEGI7AbcmkywUaaHdguZbe-?usp=sharing",
                "desc": "Monitoring dan evaluasi berkala capaian target Rencana Strategis (Renstra)."
            },
            
            # PELAPORAN
            {
                "name": "Laporan Kinerja", 
                "slug": "laporan-kinerja", 
                "group": "pelaporan", 
                "icon": "book-open", 
                "drive_url": "https://drive.google.com/drive/folders/1APuhRzJikTUZVLujq34rhQ-z1KAzmAQ3?usp=sharing",
                "desc": "Laporan Kinerja Instansi Pemerintah (LAKIP / LKjIP) BPS Kabupaten Banyuwangi."
            },

            # EVALUASI
            {
                "name": "PERMINDOK", 
                "slug": "permindok", 
                "group": "evaluasi", 
                "icon": "folder-check", 
                "drive_url": "https://drive.google.com/drive/folders/1MZNZ5ybRGqwKP16L-ZcJNaYTb2Wkvu5Y?usp=sharing",
                "desc": "Permintaan Dokumen dan kelengkapan administrasi evaluasi kinerja BPS."
            },
            {
                "name": "LHE AKIP", 
                "slug": "lhe-akip", 
                "group": "evaluasi", 
                "icon": "clipboard-check", 
                "drive_url": "https://drive.google.com/drive/folders/1qafMSDY-mGhsAsC1IhNWZ1PLDbdDBRxl?usp=sharing",
                "desc": "Laporan Hasil Evaluasi (LHE) Akuntabilitas Kinerja Instansi Pemerintah."
            },
            {
                "name": "Berita Acara", 
                "slug": "berita-acara", 
                "group": "evaluasi", 
                "icon": "file-text", 
                "drive_url": "https://drive.google.com/drive/folders/1EvOLIDXtA-2p9Y1Uz2rJwUEtZV7THPcG?usp=sharing",
                "desc": "Berita Acara rapat, rekonsiliasi, dan evaluasi berkala SAKIP."
            },
            
            # KELENGKAPAN SAKIP
            {
                "name": "SK Tim Kerja SAKIP", 
                "slug": "sk-tim-kerja-sakip", 
                "group": "kelengkapan", 
                "icon": "users", 
                "drive_url": "https://drive.google.com/drive/folders/1CNCg7oMRIuZLiYzs0h_Bju3EVhsfZPPV?usp=sharing",
                "desc": "Surat Keputusan (SK) pembentukan Tim Pengelola SAKIP BPS Kabupaten Banyuwangi."
            },
            {
                "name": "Reward dan Punishment", 
                "slug": "reward-dan-punishment", 
                "group": "kelengkapan", 
                "icon": "gift", 
                "drive_url": "https://drive.google.com/drive/folders/1nMcUg8C6FiVyMRRFqiQCUmaspezWYzQ3?usp=sharing",
                "desc": "Dokumen kebijakan pemberian reward & punishment kinerja pegawai."
            },
            {
                "name": "MPH", 
                "slug": "mph", 
                "group": "kelengkapan", 
                "icon": "calendar", 
                "drive_url": "https://drive.google.com/drive/folders/1Q4Fyhv6MGXEGVHwg9NQ5SQgTRvr4eCki?usp=sharing",
                "desc": "Manajemen Pengelolaan Hari / Matriks Perencanaan Harian (MPH)."
            },
            {
                "name": "SKP", 
                "slug": "skp", 
                "group": "kelengkapan", 
                "icon": "award", 
                "drive_url": "https://drive.google.com/drive/folders/13MaRpuGKJqjLFbkYpdrVwo5PfQUI8pRA?usp=sharing",
                "desc": "Sasaran Kinerja Pegawai (SKP) seluruh ASN BPS Kabupaten Banyuwangi."
            },
            {
                "name": "Pedoman Teknis", 
                "slug": "pedoman-teknis", 
                "group": "kelengkapan", 
                "icon": "book-marked", 
                "drive_url": "https://drive.google.com/drive/folders/1WNZs2D4AeNCrYv6wOtS3qHWPvS7-xLHy?usp=sharing",
                "desc": "Pedoman teknis, manual standar operasional, dan juklak pelaksanaan SAKIP."
            }
        ]

        for cat in categories_data:
            existing = Category.query.filter_by(slug=cat['slug']).first()
            if not existing:
                new_cat = Category(
                    name=cat['name'],
                    slug=cat['slug'],
                    group=cat['group'],
                    icon=cat['icon'],
                    description=cat['desc'],
                    drive_url=cat['drive_url']
                )
                db.session.add(new_cat)
            else:
                existing.name = cat['name']
                existing.group = cat['group']
                existing.icon = cat['icon']
                existing.description = cat['desc']
                existing.drive_url = cat['drive_url']

        # 3. Important Links Resmi (SINERGI, KiPApp, MAJAPAHIT)
        important_links_data = [
            {
                "code": "sinergi",
                "title": "SINERGI",
                "description": "Sistem Informasi Penilaian Kinerja Terintegrasi BPS.",
                "url": "https://sinergi.web.bps.go.id/",
                "icon": "share-2",
                "badge_text": "Kinerja BPS"
            },
            {
                "code": "kipapp",
                "title": "KiPApp",
                "description": "Keep Your Performance Up - Aplikasi Manajemen Kinerja BPS.",
                "url": "https://kipapp.bps.go.id/",
                "icon": "trending-up",
                "badge_text": "Performance"
            },
            {
                "code": "majapahit",
                "title": "MAJAPAHIT",
                "description": "Portal Layanan Aplikasi Majapahit Terintegrasi BPS Jawa Timur.",
                "url": "https://www.majapah.it/",
                "icon": "globe",
                "badge_text": "Portal Jatim"
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
            else:
                existing.title = link['title']
                existing.description = link['description']
                existing.url = link['url']
                existing.icon = link['icon']
                existing.badge_text = link['badge_text']
                existing.is_active = True

        db.session.commit()

        # 4. Tabel Document dikosongkan (0 dokumen diupload secara awal)
        # Menghapus dokumen bawaan awal agar data mencerminkan unggahan riil pengguna
        db.session.query(Document).delete()
        db.session.commit()

        # 5. Checklist Kelengkapan Dokumen Standard AKIP (Status Awal: Belum Lengkap / 0 Terpenuhi)
        checklist_templates = [
            {"cat_slug": "renstra", "year": 2025, "item": "Rencana Strategis (Renstra) BPS Banyuwangi 2025-2029"},
            {"cat_slug": "rencana-awal-renstra", "year": 2024, "item": "Dokumen Rancangan Awal Renstra"},
            {"cat_slug": "perjanjian-kinerja", "year": 2025, "item": "Perjanjian Kinerja (PK) Kepala Kantor & Tim"},
            {"cat_slug": "kkpk", "year": 2025, "item": "Kertas Kerja Pengukuran Kinerja (KKPK)"},
            {"cat_slug": "daha", "year": 2025, "item": "Dokumen Arsip Hasil Analisis (DAHA)"},
            {"cat_slug": "proksi", "year": 2025, "item": "Laporan Pengawasan & Pengendalian (Proksi)"},
            {"cat_slug": "laporan-kinerja", "year": 2024, "item": "Laporan Kinerja (LAKIP / LKjIP) Tahunan"},
            {"cat_slug": "permindok", "year": 2025, "item": "Permintaan Dokumen Evaluasi (PERMINDOK)"},
            {"cat_slug": "lhe-akip", "year": 2024, "item": "Laporan Hasil Evaluasi (LHE) AKIP"},
            {"cat_slug": "sk-tim-kerja-sakip", "year": 2025, "item": "SK Tim Kerja Pengelola SAKIP BPS"},
            {"cat_slug": "skp", "year": 2025, "item": "Sasaran Kinerja Pegawai (SKP) Aparatur BPS"},
            {"cat_slug": "pedoman-teknis", "year": 2024, "item": "Buku Pedoman Teknis & SOP SAKIP"}
        ]

        for chk_item in checklist_templates:
            cat = Category.query.filter_by(slug=chk_item['cat_slug']).first()
            if cat:
                c_item = DocumentCompleteness.query.filter_by(item_name=chk_item['item']).first()
                if not c_item:
                    c_item = DocumentCompleteness(
                        category_id=cat.id,
                        year=chk_item['year'],
                        item_name=chk_item['item'],
                        is_required=True,
                        is_fulfilled=False,
                        notes="Belum ada dokumen yang diunggah."
                    )
                    db.session.add(c_item)
                else:
                    c_item.is_fulfilled = False
                    c_item.category_id = cat.id
                    c_item.notes = "Belum ada dokumen yang diunggah."

        db.session.commit()

        logger.info("Database initialization completed with 0 initial uploaded documents.")
    except Exception as e:
        logger.error(f"Error during seeding initial data: {e}")
        db.session.rollback()

