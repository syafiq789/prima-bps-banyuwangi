from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required
from app.models import db, ImportantLink, Activity, User, Category
from app.utils import admin_required, log_activity

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/links')
@login_required
@admin_required
def links():
    links_list = ImportantLink.query.order_by(ImportantLink.id.asc()).all()
    categories_list = Category.query.order_by(Category.group, Category.name).all()
    return render_template('settings/links.html', links=links_list, categories=categories_list)

@settings_bp.route('/category/<int:category_id>/edit-drive', methods=['POST'])
@login_required
@admin_required
def edit_category_drive(category_id):
    category = Category.query.get_or_404(category_id)
    drive_url = request.form.get('drive_url', '').strip()
    if not drive_url:
        flash('Link Google Drive tidak boleh kosong.', 'danger')
        return redirect(url_for('settings.links'))
    category.drive_url = drive_url
    db.session.commit()
    log_activity('UPDATE_CATEGORY_DRIVE', f"Memperbarui link Google Drive kategori '{category.name}' -> {drive_url}")
    flash(f"Link Google Drive untuk kategori '{category.name}' berhasil disimpan.", 'success')
    return redirect(url_for('settings.links'))

@settings_bp.route('/links/<int:link_id>/edit', methods=['POST'])
@login_required
@admin_required
def edit_link(link_id):
    link = ImportantLink.query.get_or_404(link_id)
    title = request.form.get('title', '').strip()
    url = request.form.get('url', '').strip()
    description = request.form.get('description', '').strip()
    badge_text = request.form.get('badge_text', '').strip()
    icon = request.form.get('icon', 'external-link').strip()
    is_active = True if request.form.get('is_active') else False

    if not title or not url:
        flash('Judul dan URL tidak boleh kosong.', 'danger')
        return redirect(url_for('settings.links'))

    link.title = title
    link.url = url
    link.description = description
    link.badge_text = badge_text
    link.icon = icon
    link.is_active = is_active

    db.session.commit()
    log_activity('UPDATE_IMPORTANT_LINK', f"Mengubah konfigurasi link '{title}'")
    flash(f"Pengaturan tautan '{title}' berhasil disimpan.", 'success')
    return redirect(url_for('settings.links'))

@settings_bp.route('/activities')
@login_required
@admin_required
def activities():
    page = request.args.get('page', 1, type=int)
    action_filter = request.args.get('action', '').strip()
    user_id_filter = request.args.get('user_id', type=int)

    query = Activity.query

    if action_filter:
        query = query.filter(Activity.action == action_filter)

    if user_id_filter:
        query = query.filter(Activity.user_id == user_id_filter)

    pagination = query.order_by(Activity.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )

    users = User.query.order_by(User.full_name.asc()).all()
    actions = [a[0] for a in db.session.query(Activity.action).distinct().all()]

    return render_template(
        'settings/activities.html',
        activities=pagination.items,
        pagination=pagination,
        users=users,
        actions=actions,
        selected_action=action_filter,
        selected_user_id=user_id_filter
    )

