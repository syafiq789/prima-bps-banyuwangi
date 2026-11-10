import uuid
import urllib.parse
import requests
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, session
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, User
from app.utils import log_activity

auth_bp = Blueprint('auth', __name__)

def _get_google_redirect_uri():
    """Mendapatkan URL callback Google OAuth dengan skema HTTPS otomatis di Vercel/Production."""
    explicit_uri = current_app.config.get('GOOGLE_REDIRECT_URI')
    if explicit_uri:
        return explicit_uri
    scheme = 'https' if (request.headers.get('X-Forwarded-Proto') == 'https' or current_app.config.get('IS_VERCEL')) else request.scheme
    return url_for('auth.google_callback', _external=True, _scheme=scheme)

@auth_bp.route('/login', methods=['GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    google_configured = bool(
        current_app.config.get('GOOGLE_CLIENT_ID') and current_app.config.get('GOOGLE_CLIENT_SECRET')
    )
    redirect_uri = _get_google_redirect_uri()
    return render_template('login.html', google_configured=google_configured, callback_url=redirect_uri)

@auth_bp.route('/google/login')
def google_login():
    """Mengarahkan pengguna ke halaman pemilihan Akun Google (Google OAuth 2.0)."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    client_id = current_app.config.get('GOOGLE_CLIENT_ID')
    client_secret = current_app.config.get('GOOGLE_CLIENT_SECRET')

    if not client_id or not client_secret:
        flash('Konfigurasi Google Login belum lengkap. Tambahkan GOOGLE_CLIENT_ID dan GOOGLE_CLIENT_SECRET di environment.', 'warning')
        return redirect(url_for('auth.login'))

    state = uuid.uuid4().hex
    session['google_oauth_state'] = state

    params = {
        'client_id': client_id,
        'redirect_uri': _get_google_redirect_uri(),
        'response_type': 'code',
        'scope': 'openid email profile',
        'access_type': 'offline',
        'prompt': 'select_account',
        'state': state
    }
    google_auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"
    return redirect(google_auth_url)

@auth_bp.route('/google/callback')
def google_callback():
    """Menerima respons autentikasi dari Google dan memasukkan pengguna ke PRIMA."""
    error = request.args.get('error')
    if error:
        flash(f'Proses masuk dengan Google dibatalkan ({error}).', 'warning')
        return redirect(url_for('auth.login'))

    code = request.args.get('code')
    if not code:
        flash('Kode verifikasi dari Google tidak ditemukan.', 'danger')
        return redirect(url_for('auth.login'))

    client_id = current_app.config.get('GOOGLE_CLIENT_ID')
    client_secret = current_app.config.get('GOOGLE_CLIENT_SECRET')

    try:
        # 1. Tukar authorization code dengan access token
        token_resp = requests.post(
            'https://oauth2.googleapis.com/token',
            data={
                'code': code,
                'client_id': client_id,
                'client_secret': client_secret,
                'redirect_uri': _get_google_redirect_uri(),
                'grant_type': 'authorization_code'
            },
            timeout=10
        )
        token_data = token_resp.json()
        access_token = token_data.get('access_token')

        if not access_token:
            current_app.logger.error(f"Google token error: {token_data}")
            flash('Gagal mendapatkan akses token dari Google. Silakan coba lagi.', 'danger')
            return redirect(url_for('auth.login'))

        # 2. Ambil profil akun Google pengguna
        userinfo_resp = requests.get(
            'https://www.googleapis.com/oauth2/v3/userinfo',
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=10
        )
        user_info = userinfo_resp.json()
        email = (user_info.get('email') or '').strip().lower()
        full_name = (user_info.get('name') or email.split('@')[0] or 'Pegawai BPS').strip()

        if not email:
            flash('Akun Google Anda tidak memberikan informasi email yang valid.', 'danger')
            return redirect(url_for('auth.login'))

        # 3. Cari pengguna di database berdasarkan email, atau buat otomatis
        user = User.query.filter_by(email=email).first()
        if not user:
            # Generate username unik dari prefix email
            base_username = email.split('@')[0][:40]
            username = base_username
            if User.query.filter_by(username=username).first():
                username = f"{base_username[:35]}_{uuid.uuid4().hex[:4]}"

            # Pengguna pertama yang login atau email di ADMIN_EMAILS otomatis jadi Administrator
            admin_emails = current_app.config.get('ADMIN_EMAILS', [])
            has_admin = User.query.filter_by(role='admin').count() > 0
            assigned_role = 'admin' if (not has_admin or email in admin_emails) else 'pegawai'

            user = User(
                username=username,
                email=email,
                full_name=full_name,
                role=assigned_role,
                is_active=True
            )
            user.set_password(uuid.uuid4().hex)
            db.session.add(user)
            db.session.commit()
            log_activity('REGISTER_GOOGLE', f"Akun baru terdaftar via Google: {email} ({assigned_role})", user.id)
        else:
            if not user.is_active:
                flash('Akun Anda sedang dinonaktifkan oleh Administrator.', 'warning')
                return redirect(url_for('auth.login'))
            # Update nama lengkap jika masih kosong
            if not user.full_name and full_name:
                user.full_name = full_name
                db.session.commit()

        login_user(user, remember=True)
        log_activity('LOGIN_GOOGLE', f"Pengguna {email} ({user.role}) masuk menggunakan akun Google.", user.id)
        flash(f'Selamat datang di PRIMA, {user.full_name}!', 'success')
        return redirect(url_for('dashboard.index'))

    except Exception as e:
        current_app.logger.error(f"Google OAuth Callback Error: {e}")
        flash(f'Terjadi kendala saat menghubungkan ke Google: {str(e)}', 'danger')
        return redirect(url_for('auth.login'))

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
            nip = request.form.get('nip', '').strip()

            if not full_name:
                flash('Nama lengkap wajib diisi.', 'danger')
            else:
                current_user.full_name = full_name
                current_user.nip = nip
                db.session.commit()
                log_activity('UPDATE_PROFILE', f"Memperbarui profil pengguna {current_user.email or current_user.username}")
                flash('Profil Anda berhasil diperbarui.', 'success')

        return redirect(url_for('auth.profile'))

    return render_template('profile.html')
