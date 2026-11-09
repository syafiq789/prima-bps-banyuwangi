from flask import Blueprint, render_template
from flask_login import login_required
from sqlalchemy import func
from app.models import db, Document, Category, ImportantLink, Activity, DocumentCompleteness

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    # 1. Dokumen Statistik
    total_docs = Document.query.count()
    
    docs_perencanaan = Document.query.join(Category).filter(Category.group == 'perencanaan').count()
    docs_pengukuran = Document.query.join(Category).filter(Category.group == 'pengukuran').count()
    docs_pelaporan = Document.query.join(Category).filter(Category.group == 'pelaporan').count()
    docs_evaluasi = Document.query.join(Category).filter(Category.group == 'evaluasi').count()
    docs_kelengkapan = Document.query.join(Category).filter(Category.group == 'kelengkapan').count()
    total_important_links = ImportantLink.query.filter_by(is_active=True).count()
    
    docs_lengkap = Document.query.filter_by(status='lengkap').count()
    docs_belum_lengkap = Document.query.filter_by(status='belum_lengkap').count()
    
    # Persentase kelengkapan dokumen
    if total_docs > 0:
        completion_percentage = round((docs_lengkap / total_docs) * 100, 1)
    else:
        completion_percentage = 0.0

    # 2. Checklist AKIP Summary
    total_checklist = DocumentCompleteness.query.count()
    fulfilled_checklist = DocumentCompleteness.query.filter_by(is_fulfilled=True).count()
    checklist_percentage = round((fulfilled_checklist / total_checklist) * 100, 1) if total_checklist > 0 else 0.0

    # 3. Dokumen Terakhir Diunggah (limit 8)
    recent_documents = Document.query.order_by(Document.created_at.desc()).limit(8).all()

    # 4. Aktivitas Terbaru (limit 6)
    recent_activities = Activity.query.order_by(Activity.created_at.desc()).limit(6).all()

    # 5. Data Grafik: Dokumen per Kelompok
    group_counts = {
        'Perencanaan': docs_perencanaan,
        'Pengukuran': docs_pengukuran,
        'Pelaporan': docs_pelaporan,
        'Evaluasi': docs_evaluasi,
        'Kelengkapan SAKIP': docs_kelengkapan
    }

    # 6. Data Grafik: Tren Dokumen per Tahun
    year_stats = db.session.query(
        Document.year, func.count(Document.id)
    ).group_by(Document.year).order_by(Document.year.asc()).all()
    
    chart_years = [str(y[0]) for y in year_stats] if year_stats else ['2023', '2024', '2025', '2026']
    chart_year_counts = [y[1] for y in year_stats] if year_stats else [1, 2, 4, 3]

    # Quick links to categories
    categories = Category.query.order_by(Category.group, Category.name).all()

    return render_template('dashboard.html',
        total_docs=total_docs,
        docs_perencanaan=docs_perencanaan,
        docs_pengukuran=docs_pengukuran,
        docs_pelaporan=docs_pelaporan,
        docs_evaluasi=docs_evaluasi,
        docs_kelengkapan=docs_kelengkapan,
        total_important_links=total_important_links,
        docs_lengkap=docs_lengkap,
        docs_belum_lengkap=docs_belum_lengkap,
        completion_percentage=completion_percentage,
        total_checklist=total_checklist,
        fulfilled_checklist=fulfilled_checklist,
        checklist_percentage=checklist_percentage,
        recent_documents=recent_documents,
        recent_activities=recent_activities,
        group_counts=group_counts,
        chart_years=chart_years,
        chart_year_counts=chart_year_counts,
        categories=categories
    )

