from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, User
from app.utils import admin_required, log_activity

users_bp = Blueprint('users', __name__)

@users_bp.route('/')
@login_required
@admin_required
def index():
    users = User.query.order_by(User.role.asc(), User.created_at.desc()).all()
    return render_template('users/index.html', users=users)

@users_bp.route('/create', methods=['POST'])
@login_required
@admin_required
def create():
    username = request.form.get('username', '').strip().lower()
    full_name = request.form.get('full_name', '').strip()
    nip = request.form.get('nip', '').strip()
    role = request.form.get('role', 'user')
    password = request.form.get('password', '')

    if not username or not full_name or not password:
        flash('Username, Nama Lengkap, dan Password wajib diisi.', 'danger')
        return redirect(url_for('users.index'))

    if len(password) < 6:
        flash('Password minimal 6 karakter.', 'danger')
        return redirect(url_for('users.index'))

    existing = User.query.filter_by(username=username).first()
    if existing:
        flash(f"Pengguna dengan username '{username}' sudah terdaftar.", 'warning')
        return redirect(url_for('users.index'))

    new_user = User(
        username=username,
        full_name=full_name,
        nip=nip,
        role=role,
        is_active=True
    )
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    log_activity('CREATE_USER', f"Menambahkan pengguna baru '{username}' ({role})")
    flash(f"Pengguna '{full_name}' ({username}) berhasil ditambahkan.", 'success')
    return redirect(url_for('users.index'))

@users_bp.route('/<int:user_id>/edit', methods=['POST'])
@login_required
@admin_required
def edit(user_id):
    user = User.query.get_or_404(user_id)
    full_name = request.form.get('full_name', '').strip()
    nip = request.form.get('nip', '').strip()
    role = request.form.get('role', user.role)
    new_password = request.form.get('new_password', '').strip()

    if not full_name:
        flash('Nama Lengkap tidak boleh kosong.', 'danger')
        return redirect(url_for('users.index'))

    user.full_name = full_name
    user.nip = nip
    
    # Prevent demoting the last admin
    if user.id == current_user.id and role != 'admin':
        flash('Anda tidak dapat mengubah role akun Anda sendiri menjadi non-admin.', 'warning')
    else:
        user.role = role

    if new_password:
        if len(new_password) < 6:
            flash('Password baru minimal 6 karakter.', 'danger')
            return redirect(url_for('users.index'))
        user.set_password(new_password)

    db.session.commit()
    log_activity('EDIT_USER', f"Memperbarui data pengguna '{user.username}'")
    flash(f"Data pengguna '{user.full_name}' berhasil diperbarui.", 'success')
    return redirect(url_for('users.index'))

@users_bp.route('/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_status(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Anda tidak dapat menonaktifkan akun Anda sendiri.', 'warning')
        return redirect(url_for('users.index'))

    user.is_active = not user.is_active
    db.session.commit()

    status_str = "diaktifkan" if user.is_active else "dinonaktifkan"
    log_activity('TOGGLE_USER_STATUS', f"Akun '{user.username}' {status_str}")
    flash(f"Akun pengguna '{user.username}' berhasil {status_str}.", 'success')
    return redirect(url_for('users.index'))

@users_bp.route('/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Anda tidak dapat menghapus akun Anda sendiri.', 'danger')
        return redirect(url_for('users.index'))

    username = user.username
    db.session.delete(user)
    db.session.commit()

    log_activity('DELETE_USER', f"Menghapus pengguna '{username}' (ID: {user_id})")
    flash(f"Pengguna '{username}' berhasil dihapus.", 'success')
    return redirect(url_for('users.index'))

