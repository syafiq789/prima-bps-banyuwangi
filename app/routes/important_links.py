from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, ImportantLink
from app.utils import admin_required, log_activity

important_links_bp = Blueprint('important_links', __name__)

@important_links_bp.route('/')
@login_required
def index():
    links = ImportantLink.query.order_by(ImportantLink.id.asc()).all()
    return render_template('important_links/index.html', links=links)

@important_links_bp.route('/<code_slug>')
@login_required
def detail(code_slug):
    link = ImportantLink.query.filter_by(code=code_slug).first_or_404()
    all_links = ImportantLink.query.all()
    return render_template('important_links/detail.html', link=link, all_links=all_links)

@important_links_bp.route('/<code_slug>/update', methods=['POST'])
@login_required
@admin_required
def update(code_slug):
    link = ImportantLink.query.filter_by(code=code_slug).first_or_404()
    
    url = request.form.get('url', '').strip()
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    badge_text = request.form.get('badge_text', '').strip()

    if not url:
        flash('URL eksternal tidak boleh kosong.', 'danger')
        return redirect(url_for('important_links.detail', code_slug=code_slug))

    link.url = url
    if title:
        link.title = title
    if description:
        link.description = description
    if badge_text:
        link.badge_text = badge_text

    db.session.commit()
    log_activity('UPDATE_LINK', f"Memperbarui link eksternal '{link.title}' ({link.code}) -> {link.url}")
    flash(f"Konfigurasi tautan {link.title} berhasil diperbarui.", 'success')
    return redirect(url_for('important_links.detail', code_slug=code_slug))

