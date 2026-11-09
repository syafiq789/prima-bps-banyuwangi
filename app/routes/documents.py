import os
from flask import (
    Blueprint, render_template, request, redirect, url_for, 
    flash, current_app, send_from_directory, abort
)
from flask_login import login_required, current_user
from sqlalchemy import or_
from app.models import db, Document, Category, User
from app.utils import (
    admin_required, roles_required, log_activity, allowed_file, 
    save_document_file, delete_document_file, get_document_file_path
)

documents_bp = Blueprint('documents', __name__)

@documents_bp.route('/')
@login_required
def index():
    """
    Halaman utama daftar seluruh dokumen AKIP dengan fitur:
    - Pencarian kata kunci (judul, deskripsi, nama file asli)
    - Filter kategori & kelompok
    - Filter tahun kinerja
    - Filter status kelengkapan
    - Paginasi dinamis
    """
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('q', '').strip()
    category_slug = request.args.get('category', '').strip()
    year_filter = request.args.get('year', '', type=str).strip()
    status_filter = request.args.get('status', '').strip()

    query = Document.query

    # Filter Kategori
    selected_category = None
    if category_slug:
        selected_category = Category.query.filter_by(slug=category_slug).first()
        if selected_category:
            query = query.filter(Document.category_id == selected_category.id)

    # Filter Kata Kunci
    if search_query:
        query = query.filter(
            or_(
                Document.title.ilike(f'%{search_query}%'),
                Document.description.ilike(f'%{search_query}%'),
                Document.original_filename.ilike(f'%{search_query}%')
            )
        )

    # Filter Tahun
    if year_filter and year_filter.isdigit():
        query = query.filter(Document.year == int(year_filter))

    # Filter Status Kelengkapan
    if status_filter in ['lengkap', 'belum_lengkap']:
        query = query.filter(Document.status == status_filter)

    pagination = query.order_by(Document.year.desc(), Document.created_at.desc()).paginate(
        page=page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False
    )

    categories = Category.query.order_by(Category.group, Category.name).all()
    available_years = [y[0] for y in db.session.query(Document.year).distinct().order_by(Document.year.desc()).all()]
    if not available_years:
        available_years = [2026, 2025, 2024, 2023]

    return render_template(
        'documents/index.html',
        documents=pagination.items,
        pagination=pagination,
        categories=categories,
        selected_category=selected_category,
        search_query=search_query,
        year_filter=year_filter,
        status_filter=status_filter,
        available_years=available_years,
        page_title="Daftar Seluruh Dokumen AKIP"
    )

@documents_bp.route('/category/<slug>')
@login_required
def category_view(slug):
    """
    Halaman khusus per submenu kategori AKIP (misal: Dokumen Perencanaan, Rencana Kerja, dll).
    """
    category = Category.query.filter_by(slug=slug).first_or_404()
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('q', '').strip()
    year_filter = request.args.get('year', '', type=str).strip()
    status_filter = request.args.get('status', '').strip()

    query = Document.query.filter_by(category_id=category.id)

    if search_query:
        query = query.filter(
            or_(
                Document.title.ilike(f'%{search_query}%'),
                Document.description.ilike(f'%{search_query}%'),
                Document.original_filename.ilike(f'%{search_query}%')
            )
        )

    if year_filter and year_filter.isdigit():
        query = query.filter(Document.year == int(year_filter))

    if status_filter in ['lengkap', 'belum_lengkap']:
        query = query.filter(Document.status == status_filter)

    pagination = query.order_by(Document.year.desc(), Document.created_at.desc()).paginate(
        page=page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False
    )

    available_years = [y[0] for y in db.session.query(Document.year).filter_by(category_id=category.id).distinct().order_by(Document.year.desc()).all()]
    if not available_years:
        available_years = [2026, 2025, 2024, 2023]

    return render_template(
        'documents/category_view.html',
        category=category,
        documents=pagination.items,
        pagination=pagination,
        search_query=search_query,
        year_filter=year_filter,
        status_filter=status_filter,
        available_years=available_years,
        page_title=f"{category.name} - BPS Banyuwangi"
    )

@documents_bp.route('/upload', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'staf_umum', 'ppk')
def upload():
    """
    Formulir & aksi pengunggahan dokumen baru (Admin, Staf Umum, PPK).
    File fisik disimpan di server, metadata disimpan ke MySQL.
    """
    categories = Category.query.order_by(Category.group, Category.name).all()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category_id = request.form.get('category_id', type=int)
        year = request.form.get('year', type=int)
        description = request.form.get('description', '').strip()
        status = request.form.get('status', 'lengkap')
        notes = request.form.get('notes', '').strip()
        file = request.files.get('file')

        if not title:
            flash('Judul dokumen wajib diisi.', 'danger')
            return render_template('documents/upload.html', categories=categories)

        if not category_id or not Category.query.get(category_id):
            flash('Kategori dokumen tidak valid.', 'danger')
            return render_template('documents/upload.html', categories=categories)

        if not year or year < 2000 or year > 2100:
            flash('Tahun dokumen tidak valid.', 'danger')
            return render_template('documents/upload.html', categories=categories)

        if not file or file.filename == '':
            flash('File dokumen wajib dipilih.', 'danger')
            return render_template('documents/upload.html', categories=categories)

        if not allowed_file(file.filename):
            flash('Format file tidak didukung. Format yang diperbolehkan: PDF, DOC, DOCX, XLS, XLSX, PPTX.', 'danger')
            return render_template('documents/upload.html', categories=categories)

        try:
            # 1. Simpan fisik file ke folder uploads
            filename, orig_name, file_size, file_type = save_document_file(file)

            # 2. Simpan metadata ke tabel documents MySQL
            new_doc = Document(
                title=title,
                category_id=category_id,
                year=year,
                description=description,
                filename=filename,
                original_filename=orig_name,
                file_size=file_size,
                file_type=file_type,
                uploaded_by=current_user.id,
                status=status,
                notes=notes
            )
            db.session.add(new_doc)
            db.session.commit()

            # 3. Rekam audit trail log aktivitas
            log_activity('UPLOAD_DOCUMENT', f"Mengunggah dokumen baru: '{title}' ({new_doc.category.name})")
            flash(f"Dokumen '{title}' berhasil diunggah ke sistem PRIMA.", 'success')
            return redirect(url_for('documents.detail', doc_id=new_doc.id))

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error upload dokumen: {e}")
            flash(f"Terjadi kesalahan saat mengunggah file: {str(e)}", 'danger')

    selected_cat_id = request.args.get('category_id', type=int)
    return render_template('documents/upload.html', categories=categories, selected_cat_id=selected_cat_id)

@documents_bp.route('/<int:doc_id>')
@login_required
def detail(doc_id):
    """Halaman rincian informasi dan status kelengkapan dokumen."""
    document = Document.query.get_or_404(doc_id)
    return render_template('documents/detail.html', document=document)

@documents_bp.route('/<int:doc_id>/edit', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'staf_umum', 'ppk')
def edit(doc_id):
    """
    Formulir edit metadata dokumen atau penggantian file fisik (Admin, Staf Umum, PPK).
    """
    document = Document.query.get_or_404(doc_id)
    categories = Category.query.order_by(Category.group, Category.name).all()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category_id = request.form.get('category_id', type=int)
        year = request.form.get('year', type=int)
        description = request.form.get('description', '').strip()
        status = request.form.get('status', 'lengkap')
        notes = request.form.get('notes', '').strip()
        file = request.files.get('file')

        if not title:
            flash('Judul dokumen wajib diisi.', 'danger')
            return render_template('documents/edit.html', document=document, categories=categories)

        if not category_id or not Category.query.get(category_id):
            flash('Kategori dokumen tidak valid.', 'danger')
            return render_template('documents/edit.html', document=document, categories=categories)

        document.title = title
        document.category_id = category_id
        document.year = year
        document.description = description
        document.status = status
        document.notes = notes

        # Jika ada penggantian file fisik
        if file and file.filename != '':
            if not allowed_file(file.filename):
                flash('Format file pengganti tidak didukung.', 'danger')
                return render_template('documents/edit.html', document=document, categories=categories)

            # Hapus file fisik lama
            delete_document_file(document.filename)

            # Simpan file fisik baru
            filename, orig_name, file_size, file_type = save_document_file(file)
            document.filename = filename
            document.original_filename = orig_name
            document.file_size = file_size
            document.file_type = file_type

        db.session.commit()
        log_activity('EDIT_DOCUMENT', f"Memperbarui dokumen ID #{document.id}: '{document.title}'")
        flash(f"Informasi dokumen '{document.title}' berhasil diperbarui.", 'success')
        return redirect(url_for('documents.detail', doc_id=document.id))

    return render_template('documents/edit.html', document=document, categories=categories)

@documents_bp.route('/<int:doc_id>/delete', methods=['POST'])
@login_required
@roles_required('admin', 'staf_umum', 'ppk')
def delete(doc_id):
    """
    Menghapus dokumen dari database dan menghapus file fisiknya dari server (Admin, Staf Umum, PPK).
    """
    document = Document.query.get_or_404(doc_id)
    doc_title = document.title
    cat_slug = document.category.slug
    doc_filename = document.filename

    # Hapus file fisik dari server
    delete_document_file(doc_filename)

    # Hapus data dari MySQL
    db.session.delete(document)
    db.session.commit()

    log_activity('DELETE_DOCUMENT', f"Menghapus dokumen '{doc_title}' (ID: {doc_id})")
    flash(f"Dokumen '{doc_title}' berhasil dihapus dari sistem PRIMA.", 'success')
    return redirect(url_for('documents.category_view', slug=cat_slug))

@documents_bp.route('/<int:doc_id>/download')
@login_required
def download(doc_id):
    """
    Mengunduh file dokumen dengan nama file asli saat diunggah.
    Secara otomatis mencatat counter download dan log aktivitas.
    """
    document = Document.query.get_or_404(doc_id)
    document.download_count += 1
    db.session.commit()

    log_activity('DOWNLOAD_DOCUMENT', f"Mengunduh dokumen: '{document.title}'")

    file_path = get_document_file_path(document.filename)
    if not os.path.exists(file_path):
        # Auto recover dummy file jika hilang saat testing
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"PRIMA BPS Banyuwangi Document: {document.title}\nCategory: {document.category.name}\nYear: {document.year}")

    return send_from_directory(
        current_app.config['UPLOAD_FOLDER'],
        document.filename,
        as_attachment=True,
        download_name=document.original_filename
    )

@documents_bp.route('/<int:doc_id>/preview')
@login_required
def preview(doc_id):
    """
    Melayani file untuk pratinjau langsung di dalam peramban / modal viewer.
    """
    document = Document.query.get_or_404(doc_id)
    file_path = get_document_file_path(document.filename)
    
    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"PRIMA BPS Banyuwangi Document: {document.title}\nCategory: {document.category.name}\nYear: {document.year}")

    return send_from_directory(
        current_app.config['UPLOAD_FOLDER'],
        document.filename,
        as_attachment=False
    )
