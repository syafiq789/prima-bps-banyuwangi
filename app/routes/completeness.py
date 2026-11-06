from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models import db, DocumentCompleteness, Category, Document
from app.utils import admin_required, log_activity

completeness_bp = Blueprint('completeness', __name__)

@completeness_bp.route('/checklist')
@login_required
def checklist():
    year = request.args.get('year', 2025, type=int)
    available_years = [2026, 2025, 2024, 2023]

    checklist_items = DocumentCompleteness.query.filter_by(year=year).order_by(DocumentCompleteness.category_id, DocumentCompleteness.id).all()
    categories = Category.query.all()

    total_items = len(checklist_items)
    fulfilled_items = sum(1 for item in checklist_items if item.is_fulfilled)
    percentage = round((fulfilled_items / total_items) * 100, 1) if total_items > 0 else 0

    return render_template(
        'completeness/checklist.html',
        checklist_items=checklist_items,
        selected_year=year,
        available_years=available_years,
        categories=categories,
        total_items=total_items,
        fulfilled_items=fulfilled_items,
        percentage=percentage
    )

@completeness_bp.route('/checklist/toggle/<int:item_id>', methods=['POST'])
@login_required
@admin_required
def toggle(item_id):
    item = DocumentCompleteness.query.get_or_404(item_id)
    item.is_fulfilled = not item.is_fulfilled
    db.session.commit()
    
    status_str = "Lengkap" if item.is_fulfilled else "Belum Lengkap"
    log_activity('TOGGLE_CHECKLIST', f"Mengubah status checklist '{item.item_name}' menjadi {status_str}")
    flash(f"Status '{item.item_name}' berhasil diubah menjadi {status_str}.", 'success')
    return redirect(url_for('completeness.checklist', year=item.year))

@completeness_bp.route('/checklist/add', methods=['POST'])
@login_required
@admin_required
def add_item():
    category_id = request.form.get('category_id', type=int)
    year = request.form.get('year', 2025, type=int)
    item_name = request.form.get('item_name', '').strip()
    notes = request.form.get('notes', '').strip()

    if not item_name or not category_id:
        flash('Nama item dan kategori wajib diisi.', 'danger')
        return redirect(url_for('completeness.checklist', year=year))

    new_item = DocumentCompleteness(
        category_id=category_id,
        year=year,
        item_name=item_name,
        is_required=True,
        is_fulfilled=False,
        notes=notes
    )
    db.session.add(new_item)
    db.session.commit()

    log_activity('ADD_CHECKLIST', f"Menambahkan item checklist baru: '{item_name}' (Tahun {year})")
    flash(f"Item checklist '{item_name}' berhasil ditambahkan.", 'success')
    return redirect(url_for('completeness.checklist', year=year))

@completeness_bp.route('/checklist/delete/<int:item_id>', methods=['POST'])
@login_required
@admin_required
def delete_item(item_id):
    item = DocumentCompleteness.query.get_or_404(item_id)
    year = item.year
    name = item.item_name
    db.session.delete(item)
    db.session.commit()

    log_activity('DELETE_CHECKLIST', f"Menghapus item checklist '{name}'")
    flash(f"Item checklist '{name}' berhasil dihapus.", 'success')
    return redirect(url_for('completeness.checklist', year=year))

@completeness_bp.route('/administrasi')
@login_required
def administrasi():
    categories = Category.query.all()
    stats = []
    for cat in categories:
        total = Document.query.filter_by(category_id=cat.id).count()
        lengkap = Document.query.filter_by(category_id=cat.id, status='lengkap').count()
        pct = round((lengkap / total) * 100, 1) if total > 0 else 0
        stats.append({
            'category': cat,
            'total': total,
            'lengkap': lengkap,
            'belum_lengkap': total - lengkap,
            'percentage': pct
        })

    return render_template('completeness/administrasi.html', stats=stats)

@completeness_bp.route('/belum-lengkap')
@login_required
def belum_lengkap():
    pending_documents = Document.query.filter_by(status='belum_lengkap').order_by(Document.year.desc(), Document.created_at.desc()).all()
    unfulfilled_checklist = DocumentCompleteness.query.filter_by(is_fulfilled=False).order_by(DocumentCompleteness.year.desc()).all()

    return render_template(
        'completeness/belum_lengkap.html',
        pending_documents=pending_documents,
        unfulfilled_checklist=unfulfilled_checklist
    )

