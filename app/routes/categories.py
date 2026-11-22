from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models import db, Category, Document
from app.utils import admin_required, log_activity

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/')
@login_required
def index():
    categories = Category.query.order_by(Category.group, Category.name).all()
    # Add count per category
    for cat in categories:
        cat.doc_count = Document.query.filter_by(category_id=cat.id).count()
    return render_template('categories/index.html', categories=categories)

@categories_bp.route('/create', methods=['POST'])
@login_required
@admin_required
def create():
    name = request.form.get('name', '').strip()
    slug = request.form.get('slug', '').strip().lower().replace(' ', '-')
    group = request.form.get('group', 'perencanaan')
    description = request.form.get('description', '').strip()
    icon = request.form.get('icon', 'folder').strip()
    drive_url = request.form.get('drive_url', '').strip()

    if not name or not slug:
        flash('Nama kategori dan slug wajib diisi.', 'danger')
        return redirect(url_for('categories.index'))

    existing = Category.query.filter((Category.slug == slug) | (Category.name == name)).first()
    if existing:
        flash('Kategori dengan nama atau slug tersebut sudah ada.', 'warning')
        return redirect(url_for('categories.index'))

    new_cat = Category(
        name=name,
        slug=slug,
        group=group,
        description=description,
        icon=icon,
        drive_url=drive_url if drive_url else None
    )
    db.session.add(new_cat)
    db.session.commit()

    log_activity('CREATE_CATEGORY', f"Membuat kategori baru: '{name}'")
    flash(f"Kategori '{name}' berhasil ditambahkan.", 'success')
    return redirect(url_for('categories.index'))

@categories_bp.route('/<int:cat_id>/edit', methods=['POST'])
@login_required
@admin_required
def edit(cat_id):
    cat = Category.query.get_or_404(cat_id)
    name = request.form.get('name', '').strip()
    group = request.form.get('group', cat.group)
    description = request.form.get('description', '').strip()
    icon = request.form.get('icon', cat.icon).strip()

    if not name:
        flash('Nama kategori tidak boleh kosong.', 'danger')
        return redirect(url_for('categories.index'))

    cat.name = name
    cat.group = group
    cat.description = description
    cat.icon = icon
    drive_url = request.form.get('drive_url', '').strip()
    cat.drive_url = drive_url if drive_url else None

    db.session.commit()
    log_activity('EDIT_CATEGORY', f"Memperbarui kategori ID #{cat_id}: '{name}'")
    flash(f"Kategori '{name}' berhasil diperbarui.", 'success')
    return redirect(url_for('categories.index'))

@categories_bp.route('/<int:cat_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(cat_id):
    cat = Category.query.get_or_404(cat_id)
    doc_count = Document.query.filter_by(category_id=cat.id).count()

    if doc_count > 0:
        flash(f"Kategori '{cat.name}' tidak dapat dihapus karena masih memuat {doc_count} dokumen.", 'danger')
        return redirect(url_for('categories.index'))

    name = cat.name
    db.session.delete(cat)
    db.session.commit()

    log_activity('DELETE_CATEGORY', f"Menghapus kategori '{name}'")
    flash(f"Kategori '{name}' berhasil dihapus.", 'success')
    return redirect(url_for('categories.index'))

