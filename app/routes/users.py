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
    email = request.form.get('email', '').strip().lower()
    username = request.form.get('username', '').strip().lower()
    full_name = request.form.get('full_name', '').strip()
    nip = request.form.get('nip', '').strip()
    role = request.form.get('role', 'pegawai')
    password = request.form.get('password', '')

    if role not in User.ROLES:
        role = 'pegawai'

    # Auto-generate username from email prefix if username omitted
    if not username and email:
        username = email.split('@')[0]

    if not email or not full_name or not password:
        flash('Email, Nama Lengkap, dan Password wajib diisi.', 'danger')
        return redirect(url_for('users.index'))

    if len(password) < 6:
        flash('Password minimal 6 karakter.', 'danger')
        return redirect(url_for('users.index'))

    if User.query.filter_by(email=email).first():
        flash(f"Pengguna dengan email '{email}' sudah terdaftar.", 'warning')
        return redirect(url_for('users.index'))

    if User.query.filter_by(username=username).first():
        # Make username unique if prefix collides
        import uuid
        username = f"{username}_{uuid.uuid4().hex[:4]}"

    new_user = User(
        username=username,
        email=email,
        full_name=full_name,
        nip=nip,
        role=role,
        is_active=True
    )
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    log_activity('CREATE_USER', f"Menambahkan pengguna baru '{email}' ({role})")
    flash(f"Pengguna '{full_name}' ({email}) berhasil ditambahkan.", 'success')
    return redirect(url_for('users.index'))

@users_bp.route('/<int:user_id>/edit', methods=['POST'])
@login_required
@admin_required
def edit(user_id):
    user = User.query.get_or_404(user_id)
    email = request.form.get('email', '').strip().lower()
    full_name = request.form.get('full_name', '').strip()
    nip = request.form.get('nip', '').strip()
    role = request.form.get('role', user.role)
    new_password = request.form.get('new_password', '').strip()

    if not full_name:
        flash('Nama Lengkap tidak boleh kosong.', 'danger')
        return redirect(url_for('users.index'))

    if email:
        existing_email = User.query.filter(User.email == email, User.id != user.id).first()
        if existing_email:
            flash(f"Email '{email}' sudah dipakai oleh akun lain.", 'warning')
            return redirect(url_for('users.index'))
        user.email = email

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

