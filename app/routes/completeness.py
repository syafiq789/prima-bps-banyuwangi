from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, DocumentCompleteness, Category, Document, SakipEvaluation
from app.utils import admin_required, roles_required, log_activity

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

@completeness_bp.route('/penilaian')
@login_required
def penilaian():
    """Halaman Penilaian Kriteria & Skor LKE SAKIP (PermenPANRB No. 88 Tahun 2021)."""
    year = request.args.get('year', 2025, type=int)
    available_years = [2026, 2025, 2024]

    evaluations = SakipEvaluation.query.filter_by(year=year).order_by(SakipEvaluation.id).all()

    total_score = round(sum(e.score for e in evaluations), 2)
    max_total_score = round(sum(e.max_score for e in evaluations), 2) or 100.0
    predicate_code, predicate_label, predicate_color = SakipEvaluation.get_predicate(total_score)

    # Kelompokkan komponen beserta ringkasan skor masing-masing
    components_order = [
        ('perencanaan', 'Perencanaan Kinerja', 30.0, 'compass', 'blue'),
        ('pengukuran', 'Pengukuran Kinerja', 30.0, 'gauge', 'emerald'),
        ('pelaporan', 'Pelaporan Kinerja', 15.0, 'file-check-2', 'amber'),
        ('evaluasi', 'Evaluasi AKIP Internal', 25.0, 'clipboard-check', 'teal')
    ]

    grouped_components = []
    for code, name, weight, icon, color in components_order:
        items = [e for e in evaluations if e.component_code == code]
        comp_score = round(sum(e.score for e in items), 2)
        comp_max = round(sum(e.max_score for e in items), 2) or weight
        comp_pct = round((comp_score / comp_max) * 100, 1) if comp_max > 0 else 0.0
        grouped_components.append({
            'code': code,
            'name': name,
            'weight': weight,
            'icon': icon,
            'color': color,
            'items': items,
            'score': comp_score,
            'max_score': comp_max,
            'percentage': comp_pct
        })

    return render_template(
        'completeness/penilaian.html',
        selected_year=year,
        available_years=available_years,
        grouped_components=grouped_components,
        total_score=total_score,
        max_total_score=max_total_score,
        predicate_code=predicate_code,
        predicate_label=predicate_label,
        predicate_color=predicate_color,
        evaluations=evaluations
    )

@completeness_bp.route('/penilaian/save/<int:year>', methods=['POST'])
@login_required
@roles_required('admin', 'kpa', 'ppk', 'staf_umum')
def save_penilaian(year):
    """Menyimpan seluruh nilai kriteria LKE SAKIP sekaligus dan menghitung total nilai & predikat."""
    evaluations = SakipEvaluation.query.filter_by(year=year).all()
    if not evaluations:
        flash(f'Data kriteria LKE SAKIP tahun {year} tidak ditemukan.', 'warning')
        return redirect(url_for('completeness.penilaian', year=year))

    for item in evaluations:
        grade = request.form.get(f'grade_{item.id}', '').strip()
        notes = request.form.get(f'notes_{item.id}', '').strip()
        evidence_url = request.form.get(f'evidence_{item.id}', '').strip()

        multiplier = SakipEvaluation.GRADE_MULTIPLIERS.get(grade, 0.0)
        item.answer_grade = grade
        item.score = round(item.max_score * multiplier, 2)
        item.evaluator_notes = notes
        if evidence_url:
            item.evidence_url = evidence_url
        item.updated_by = current_user.id

    db.session.commit()

    total_score = round(sum(e.score for e in evaluations), 2)
    pred_code, pred_label, _ = SakipEvaluation.get_predicate(total_score)

    log_activity('SAVE_SAKIP_EVALUATION', f"Menyimpan Penilaian Kriteria SAKIP Tahun {year} dengan total skor {total_score}/100 (Predikat {pred_code})")
    flash(f"Penilaian Kriteria SAKIP Tahun {year} berhasil disimpan! Total Nilai: {total_score} (Predikat {pred_code} - {pred_label}).", 'success')
    return redirect(url_for('completeness.penilaian', year=year))

@completeness_bp.route('/penilaian/reset/<int:year>', methods=['POST'])
@login_required
@admin_required
def reset_penilaian(year):
    """Mereset seluruh nilai kriteria LKE SAKIP untuk tahun tertentu ke 0."""
    evaluations = SakipEvaluation.query.filter_by(year=year).all()
    for item in evaluations:
        item.answer_grade = ''
        item.score = 0.0
        item.evaluator_notes = ''
        item.updated_by = current_user.id
    db.session.commit()

    log_activity('RESET_SAKIP_EVALUATION', f"Mereset seluruh nilai LKE SAKIP Tahun {year} menjadi 0")
    flash(f"Penilaian Kriteria SAKIP Tahun {year} berhasil direset.", 'info')
    return redirect(url_for('completeness.penilaian', year=year))


