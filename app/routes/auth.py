from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, User
from app.utils import log_activity

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        # Terima input dari field 'email' (atau fallback 'username')
        email_input = (request.form.get('email') or request.form.get('username') or '').strip().lower()
        password = request.form.get('password', '')
        remember = True if request.form.get('remember') else False

        # Cari pengguna berdasarkan email atau username
        user = User.query.filter(
            (User.email == email_input) | (User.username == email_input)
        ).first()

        if not user or not user.check_password(password):
            flash('Email atau password yang Anda masukkan salah.', 'danger')
            return render_template('login.html', email=email_input)

        if not user.is_active:
            flash('Akun Anda dinonaktifkan oleh Administrator. Hubungi admin untuk mengaktifkan.', 'warning')
            return render_template('login.html', email=email_input)

        login_user(user, remember=remember)
        log_activity('LOGIN', f"Pengguna {user.email or user.username} ({user.role}) berhasil masuk ke sistem.", user.id)
        flash(f'Selamat datang kembali, {user.full_name}!', 'success')

        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('dashboard.index')
        return redirect(next_page)

    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    identifier = current_user.email or current_user.username
    uid = current_user.id
    logout_user()
    log_activity('LOGOUT', f"Pengguna {identifier} telah keluar dari sistem.", uid)
    flash('Anda telah berhasil keluar dari sistem PRIMA.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'update_profile':
            full_name = request.form.get('full_name', '').strip()
            email = request.form.get('email', '').strip().lower()
            nip = request.form.get('nip', '').strip()

            if not full_name:
                flash('Nama lengkap wajib diisi.', 'danger')
            elif email and User.query.filter(User.email == email, User.id != current_user.id).first():
                flash('Alamat email sudah digunakan oleh akun lain.', 'danger')
            else:
                current_user.full_name = full_name
                if email:
                    current_user.email = email
                current_user.nip = nip
                db.session.commit()
                log_activity('UPDATE_PROFILE', f"Memperbarui profil pengguna {current_user.email or current_user.username}")
                flash('Profil Anda berhasil diperbarui.', 'success')

        elif action == 'change_password':
            old_password = request.form.get('old_password', '')
            new_password = request.form.get('new_password', '')
            confirm_password = request.form.get('confirm_password', '')

            if not current_user.check_password(old_password):
                flash('Password saat ini salah.', 'danger')
            elif len(new_password) < 6:
                flash('Password baru minimal 6 karakter.', 'danger')
            elif new_password != confirm_password:
                flash('Konfirmasi password baru tidak cocok.', 'danger')
            else:
                current_user.set_password(new_password)
                db.session.commit()
                log_activity('CHANGE_PASSWORD', f"Mengubah password pengguna {current_user.email or current_user.username}")
                flash('Password Anda berhasil diperbarui. Gunakan password baru untuk login berikutnya.', 'success')

        return redirect(url_for('auth.profile'))

    return render_template('profile.html')
